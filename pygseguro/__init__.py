"""
Esse módulo implementa o padrão de projeto Fachada de forma pytonica.

Ele é interface para acessar todos elememntos da biblioteca
"""

from pygseguro import config as _config
from pygseguro.plano_recorrente_automatico import CriadorPlanoRecorrente as _C

__version__ = '0.1'

ConfigConta = _config.ConfigConta  # Dando visibilidade na fachada para a classe ConfigConta
ConfigApp = _config.ConfigApp
Config = _config.Config
CriadorPlanoRecorrente = _C
PRODUCAO = _config.PRODUCAO
SANDBOX = _config.SANDBOX


def apagar_config_padrao() -> None:
    """
    Função que apaga a configuração padrão alterando seu valor para None
    """
    set_config_padrao(None)


get_config_padrao = _config.get_config_padrao


def set_config_padrao(config: Config):
    """
    Função que altera configuração padrão da aplicação
    :param config: ConfigConta
    """
    _config.config_padrao = config
