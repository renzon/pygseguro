"""
Esse módulo contém a configuração padrão das chamadas e fornece uma classe de Config que representa essa configuração
"""

config_padrao = None


class Config:
    """
    Classe que representa uma configuração
    """

    def __init__(self, email=None, token=None):
        self.token = token
        self.email = email

    def __repr__(self):
        return f'Config(email={self.email!r}, token={self.token!r})'
