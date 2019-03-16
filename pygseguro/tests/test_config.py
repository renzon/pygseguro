"""
Módulo destinado a testar as configurações do projeto
"""
import pytest

from pygseguro import Config, apagar_config_padrao, get_config_padrao, set_config_padrao


@pytest.fixture
def cfg():
    return Config(email='foo@bar.com', token='blah')


def test_config_padrao(cfg):
    apagar_config_padrao()
    assert get_config_padrao() is None
    set_config_padrao(cfg)
    assert get_config_padrao() is cfg
