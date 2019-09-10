from netbox_agent.dmidecode import parse
from netbox_agent.server import ServerBase
from tests.conftest import parametrize_with_fixtures


@parametrize_with_fixtures('dmidecode/')
def test_init(fixture):
    dmi = parse(fixture)
    server = ServerBase(dmi)
    assert server
