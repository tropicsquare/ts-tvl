import pytest

from tvl.api.l3_api import TsL3PingCommand, TsL3PingResult
from tvl.constants import L3ResultFieldEnum
from tvl.host.host import Host
from tvl.messages.randomize import randomize

from ..utils import as_slow


@pytest.mark.parametrize("times", as_slow(list(range(33)), 10))
def test(host: Host, times: int):
    command = randomize(TsL3PingCommand)
    result = host.send_command(command)

    assert result.result.value == L3ResultFieldEnum.OK
    assert isinstance(result, TsL3PingResult)
    assert result.data_out.to_bytes() == command.data_in.to_bytes()


# TODO add tests with no rights
