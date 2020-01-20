import subprocess
import json
import logging
import sys

from netbox_agent.misc import is_tool


class LSHW():
    def __init__(self):
        if not is_tool('lshw'):
            logging.error('lshw does not seem to be installed')
            sys.exit(1)

        data = subprocess.getoutput(
            'sudo /usr/sbin/lshw -quiet -json'
        )
        self.hw_info = json.loads(data)
        self.info = {}
        self.memories = []
        self.interfaces = []
        self.cpus = []
        self.power = []
        self.disks = []
        self.vendor = self.hw_info["vendor"]
        self.product = self.hw_info["product"]
        self.chassis_serial = self.hw_info["serial"]
        self.motherboard_serial = self.hw_info["children"][0].get("serial", "No S/N")
        self.motherboard = self.hw_info["children"][0].get("product", "Motherboard")

        for k in self.hw_info["children"]:
            if k["class"] == "power":
                # self.power[k["id"]] = k
                self.power.append(k)

            if "children" in k:
                for j in k["children"]:
                    if j["class"] == "generic":
                        continue

                    if j["class"] == "storage":
                        self.find_storage(j)

                    if j["class"] == "memory":
                        self.find_memories(j)

                    if j["class"] == "processor":
                        self.find_cpus(j)

                    if j["class"] == "bridge":
                        self.walk_bridge(j)

    def get_hw_linux(self, hwclass):
        if hwclass == "cpu":
            return self.cpus
        if hwclass == "network":
            return self.interfaces
        if hwclass == 'storage':
            return self.disks
        if hwclass == 'memory':
            return self.memories

    def find_network(self, obj):
        d = {}
        d["name"] = obj["logicalname"]
        d["macaddress"] = obj["serial"]
        d["serial"] = obj["serial"]
        d["product"] = obj["product"]
        d["vendor"] = obj["vendor"]
        d["description"] = obj["description"]

        self.interfaces.append(d)

    def find_storage(self, obj):
        if "children" in obj:
            for device in obj["children"]:
                d = {}
                d["logicalname"] = device.get("logicalname")
                d["product"] = device.get("product")
                d["serial"] = device.get("serial")
                d["version"] = device.get("version")
                d["size"] = device.get("size")
                d["description"] = device.get("description")

                self.disks.append(d)

        elif "nvme" in obj["configuration"]["driver"]:
            nvme = json.loads(
                            subprocess.check_output(
                                ["sudo", "/usr/sbin/nvme", '-list', '-o', 'json'],
                                encoding='utf8')
                            )

            d = {}
            d["vendor"] = obj["vendor"]
            d["version"] = obj["version"]
            d["product"] = obj["product"]

            d['description'] = "NVME Disk"
            d['product'] = nvme["Devices"][0]["ModelNumber"]
            d['size'] = nvme["Devices"][0]["PhysicalSize"]
            d['serial'] = nvme["Devices"][0]["SerialNumber"]
            d['logicalname'] = nvme["Devices"][0]["DevicePath"]

            self.disks.append(d)

    def find_cpus(self, obj):
        c = {}
        c["product"] = obj["product"]
        c["vendor"] = obj["vendor"]
        c["description"] = obj["description"]
        c["location"] = obj["slot"]

        self.cpus.append(c)

    def find_memories(self, obj):
        if "children" not in obj:
            # print("not a DIMM memory.")
            return

        for dimm in obj["children"]:
            if "empty" in dimm["description"]:
                continue

            d = {}
            d["slot"] = dimm.get("slot")
            d["description"] = dimm.get("description")
            d["id"] = dimm.get("id")
            d["serial"] = dimm.get("serial", 'N/A')
            d["vendor"] = dimm.get("vendor", 'N/A')
            d["product"] = dimm.get("product")
            d["size"] = dimm.get("size", 0) / 2 ** 20 / 1024

            self.memories.append(d)

    def walk_bridge(self, obj):
        if "children" not in obj:
            return

        for bus in obj["children"]:
            if bus["class"] == "storage":
                self.find_storage(bus)

            if "children" in bus:
                for b in bus["children"]:
                    if b["class"] == "storage":
                        self.find_storage(b)
                    if b["class"] == "network":
                        self.find_network(b)


if __name__ == "__main__":
    pass
