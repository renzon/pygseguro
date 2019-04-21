"""
Módulo destinado a testar as configurações do projeto
"""
import pytest

from pygseguro import ConfigApp, ConfigConta, apagar_config_padrao, get_config_padrao, set_config_padrao


@pytest.fixture
def cfg_conta() -> ConfigConta:
    return ConfigConta(email='foo@bar.com', token='blah')


@pytest.fixture
def cfg_app() -> ConfigApp:
    return ConfigApp(app_id='1234', app_key='segredo')


def test_config_padrao(cfg_conta: ConfigConta):
    """Cecha possibilidade de configuração global"""
    apagar_config_padrao()
    assert get_config_padrao() is None
    set_config_padrao(cfg_conta)
    assert get_config_padrao() is cfg_conta


def test_token_omitido_repr_ConfigConta(cfg_conta: ConfigConta):
    """Verifica se o token foi omitido no repr de ConfigConta"""
    cfg_conta_expected = "ConfigConta(email='foo@bar.com', token='****')"
    assert cfg_conta_expected == repr(cfg_conta)


def test_token_omitido_repr_ConfigApp(cfg_app: ConfigApp):
    """Verifica se o app_key foi omitido no repr de ConfigApp"""
    cfg_app_expected = "ConfigApp(app_id='1234', app_key='*******')"
    assert cfg_app_expected == repr(cfg_app)


endpoints = pytest.mark.parametrize('endpoint', '/comprar /checkout /notificaes'.split())


@endpoints
def test_config_conta_url_producao(cfg_conta: ConfigConta, endpoint: str):
    """Testa geração de url apontado para ambiente de produção por padrão e autentação de conta"""
    assert cfg_conta.construir_url(
        endpoint) == f'https://ws.pagseguro.uol.com.br{endpoint}?email=foo@bar.com&token=blah'


@endpoints
def test_config_app_url_producao(cfg_app: ConfigApp, endpoint: str):
    """Testa geração de url apontado para ambiente de produção por padrão e autentação de app"""
    assert cfg_app.construir_url(endpoint) == f'https://ws.pagseguro.uol.com.br{endpoint}?appID=1234&appKey=segredo'
