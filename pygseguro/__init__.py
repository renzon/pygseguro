"""
Esse módulo implementa o padrão de projeto Fachada de forma pytonica.

Ele é interface para acessar todos elememntos da biblioteca
"""

import pygseguro.config as _config

__version__ = '0.1'

Config = _config.Config  # Dando visibilidade na fachada para a classe Config


def apagar_config_padrao() -> None:
    """
    Função que apaga a configuração padrão alterando seu valor para None
    """
    set_config_padrao(None)


def get_config_padrao() -> Config:
    """
    Função que retorna configuração padrão atual da aplicação
    :return: Configuração atual
    """
    return _config.config_padrao


def set_config_padrao(config: Config):
    """
    Função que altera configuração padrão da aplicação
    :param config: Config
    """
    _config.config_padrao = config
