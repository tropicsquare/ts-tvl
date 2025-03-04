from tvl.api.l3_api import TsL3MacAndDestroyCommand
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.messages.randomize import randomize


def test(host: Host):
    command = randomize(TsL3MacAndDestroyCommand)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.INVALID_CMD
