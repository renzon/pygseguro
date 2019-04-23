"""
Esse módulo contém a configuração padrão das chamadas e fornece uma classe de ConfigConta que representa essa
configuração

Doc da API: https://dev.pagseguro.uol.com.br/reference#autenticacao

"""

config_padrao = None

PRODUCAO = 'https://ws.pagseguro.uol.com.br'


class Config():
    def __init__(self, ambiente: str):
        self.ambiente = ambiente

    def ambiente_endpoint(self, endpoint: str) -> str:
        """
        Constroi o {schema}://{ambiente}/{endpoint} para o pagseguro
        :param endpoint: endpoint para onde será enviada a requisição
        :return: base da url para o endpoint
        """
        return f'{self.ambiente}{endpoint}'

    def query_string(self) -> str:
        """
        Metodo abstrato que deve ser implementado em cada subclasse.
        Deve retornar a query string que deve ser enviada para autenticao no endpoint
        :return: query string
        """
        raise NotImplementedError()

    def construir_url(self, endpoint: str) -> str:
        """
        Método que constroi a url para completa para envio de requisição para a API
        :param endpoint:
        :return:
        """
        return f'{self.ambiente_endpoint(endpoint)}?{self.query_string()}'


class ConfigConta(Config):
    """
    Classe que representa uma configuração por email e token
    """

    def __init__(self, email: str, token: str, ambiente: str = PRODUCAO):
        super().__init__(ambiente=ambiente)
        self.token = token
        self.email = email

    def __repr__(self) -> str:
        return f'ConfigConta(email={self.email!r}, token={self.token!r})'

    def query_string(self) -> str:
        """
        Constroi query string contendo email e token
        :return:
        """
        return f'email={self.email}&token={self.token}'


class ConfigApp(Config):
    """
    Classe que representa uma configuração por app_id e app_key
    """

    def __init__(self, app_id: str, app_key: str, ambiente: str = PRODUCAO):
        super().__init__(ambiente)
        self.app_key = app_key
        self.app_id = app_id

    def __repr__(self) -> str:
        return f'ConfigApp(app_id={self.app_id!r}, app_key={self.app_key!r})'

    def query_string(self) -> str:
        """
        Constroi query string contendo app_key e app_id
        :return:
        """
        return f'appID={self.app_id}&appKey={self.app_key}'
