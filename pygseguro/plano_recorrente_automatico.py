from datetime import datetime
from decimal import Decimal
from typing import Dict

import pytz
import requests

from pygseguro.config import Config, get_config_padrao


def _to_decimal_string(decimal: Decimal):
    return f'{decimal:.2f}'


class PassoDePlanoRecorrente:

    def __init__(self, config: Config = None, main_data: Dict = None, pre_approval: Dict = None, receiver: Dict = None,
                 expiration: Dict = None):
        self._main_data = {} if main_data is None else main_data
        self._pre_approval = {} if pre_approval is None else pre_approval
        self._receiver = {} if receiver is None else receiver
        self._expiration = {} if expiration is None else expiration
        self._main_data['preApproval'] = self._pre_approval
        if config is None:
            config = get_config_padrao()

        self._config = config

    def _construir_proximo_passo(self, proximo_passo_cls) -> 'PassoDePlanoRecorrente':
        return proximo_passo_cls(self._config, self._main_data, self._pre_approval, self._receiver, self._expiration)

    def _manipular_payload(self, *args, **kwargs):
        raise NotImplementedError()


class CriadorPlanoRecorrente(PassoDePlanoRecorrente):

    def __init__(self, config: Config = None):
        super().__init__(config)

    def plano_automatico_idenficacao(self, referencia, nome, detalhes=None, receiver_email=None):
        plano = self._construir_proximo_passo(PlanoAutomaticoIdentificacao)
        plano._manipular_payload(referencia=referencia, nome=nome, detalhes=detalhes,
                                 receiver_email=receiver_email)
        return plano


class PlanoAutomaticoIdentificacao(PassoDePlanoRecorrente):

    def _manipular_payload(self, referencia, nome, detalhes=None, receiver_email=None):
        self._main_data['reference'] = referencia
        self._pre_approval['charge'] = 'AUTO'
        self._pre_approval['name'] = nome
        if detalhes is not None:
            self._pre_approval['details'] = detalhes
        if receiver_email is not None:
            self._receiver['email'] = receiver_email
            self._main_data['receiver'] = self._receiver

    def expiracao_em_meses(self, meses: int) -> 'Expiracao':
        expiracao = self._construir_proximo_passo(Expiracao)
        expiracao._manipular_payload(Expiracao.MONTHS, meses)
        return expiracao


class Expiracao(PassoDePlanoRecorrente):
    MONTHS = 'MONTHS'

    def _manipular_payload(self, unidade: str, valor: int):
        self._expiration['unit'] = unidade
        self._expiration['value'] = valor
        self._pre_approval['expiration'] = self._expiration

    def valores_automaticos(self, valor_periodico: Decimal, taxa_adesao: Decimal = None) -> 'ValoresAutomaticos':
        valores = self._construir_proximo_passo(ValoresAutomaticos)
        valores._manipular_payload(valor_periodico, taxa_adesao)
        return valores


class ValoresAutomaticos(PassoDePlanoRecorrente):
    def _manipular_payload(self, valor_periodico: Decimal, taxa_adesao: Decimal = None):
        self._pre_approval['amountPerPayment'] = _to_decimal_string(valor_periodico)
        if taxa_adesao is not None:
            self._pre_approval['membershipFee'] = _to_decimal_string(taxa_adesao)

    def frequencia_semanal(self) -> 'FrequenciaPlanoAutomatico':
        return self._setar_frequencia(FrequenciaPlanoAutomatico.WEEKLY)

    def frequencia_mensal(self) -> 'FrequenciaPlanoAutomatico':
        return self._setar_frequencia(FrequenciaPlanoAutomatico.MONTHLY)

    def frequencia_bimestral(self) -> 'FrequenciaPlanoAutomatico':
        return self._setar_frequencia(FrequenciaPlanoAutomatico.BIMONTHLY)

    def frequencia_semestral(self) -> 'FrequenciaPlanoAutomatico':
        return self._setar_frequencia(FrequenciaPlanoAutomatico.SEMIANNUALLY)

    def frequencia_anual(self) -> 'FrequenciaPlanoAutomatico':
        return self._setar_frequencia(FrequenciaPlanoAutomatico.YEARLY)

    def _setar_frequencia(self, tipo_frequencia: str) -> 'FrequenciaPlanoAutomatico':
        frequencia = self._construir_proximo_passo(FrequenciaPlanoAutomatico)
        frequencia._manipular_payload(tipo_frequencia)
        return frequencia


class UltimoPasso(PassoDePlanoRecorrente):
    def criar_no_pagseguro(self) -> 'PlanoAutomaticoRecorrente':
        """
        Cria um plano automático na conta do pagseguro
        :return: código do plano criado
        """
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/vnd.pagseguro.com.br.v3+json;charset=ISO-8859-1'
        }
        response = requests.post(self._config.construir_url('/pre-approvals/request'), json=self._main_data,
                                 headers=headers)
        codigo_data = response.json()
        dt = datetime.fromisoformat(codigo_data['date']).astimezone(pytz.UTC)
        return PlanoAutomaticoRecorrente(codigo_data['code'], dt)

    def limite_de_uso(self, quantidade: int) -> 'LimiteDeUso':
        """
        Defina a quantidade máxima de consumidores que podem aderir ao plano automático (Opcional)
        :param quantidade: limite de adesões
        :return: LimiteDeUso
        """
        limite = self._construir_proximo_passo(LimiteDeUso)
        limite._manipular_payload(quantidade)
        return limite

    def trial(self, dias: int) -> 'Trial':
        """Defina um período de testes, em dias (Opcional)"""
        trial = self._construir_proximo_passo(Trial)
        trial._manipular_payload(dias)
        return trial

    def urls_gancho(self, redirecionamento_url: str = None, revisao_url: str = None,
                    cancelamento_url: str = None) -> 'UrlsGancho':
        """Defina URLs de redirecionamento (Opcional)"""
        urls = self._construir_proximo_passo(UrlsGancho)
        urls._manipular_payload(redirecionamento_url, revisao_url, cancelamento_url)
        return urls


class FrequenciaPlanoAutomatico(UltimoPasso):
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    BIMONTHLY = 'BIMONTHLY'
    SEMIANNUALLY = 'SEMIANNUALLY'
    YEARLY = 'YEARLY'

    def _manipular_payload(self, frequencia: str):
        self._pre_approval['period'] = frequencia


class LimiteDeUso(UltimoPasso):
    def _manipular_payload(self, quantidade: int):
        self._main_data['maxUses'] = quantidade


class Trial(UltimoPasso):
    def _manipular_payload(self, dias: int):
        self._pre_approval['trialPeriodDuration'] = dias


class UrlsGancho(UltimoPasso):
    def _manipular_payload(self, redirecionamento_url: str = None, revisao_url: str = None,
                           cancelamento_url: str = None):
        if cancelamento_url:
            self._pre_approval['cancelURL'] = cancelamento_url
        if redirecionamento_url:
            self._main_data['redirectURL'] = redirecionamento_url
        if revisao_url:
            self._main_data['reviewURL'] = revisao_url


class PlanoAutomaticoRecorrente:
    def __init__(self, codigo: str, criacao: datetime):
        self.codigo = codigo
        self.criacao = criacao
