import json
from datetime import datetime
from decimal import Decimal

import pytest
import pytz
import responses

from pygseguro import ConfigConta, CriadorPlanoRecorrente, SANDBOX, set_config_padrao
from pygseguro.exceptions import PagseguroException


@pytest.fixture
def valores_automaticos():
    set_config_padrao(ConfigConta('renzo@python.pro.br', '396FC29DE4A54967BF6DCADE65100E88', SANDBOX))
    criador = CriadorPlanoRecorrente()
    plano_identificacao = criador.plano_automatico_idenficacao(
        'SEU_CODIGO_DE_REFERENCIA',
        'Plano Turma de Curso de Python',
        'Plano de pagamento da turma Luciano Ramalho',
        'renzo@python.pro.br')
    expiracao = plano_identificacao.expiracao_em_meses(meses=10)
    return expiracao.valores_automaticos(Decimal('180.00'), Decimal('30.39'))


@pytest.fixture
def gerador_plano_recorrente_automatico(valores_automaticos):
    freq_mensal = valores_automaticos.frequencia_mensal()
    limite_de_uso = freq_mensal.limite_de_uso(100)
    trial = limite_de_uso.trial(dias=2)
    urls_gancho = trial.urls_gancho('https://seusite.com.br/obrigado', 'https://seusite.com.br/revisar',
                                    'https://seusite.com.br/cancelar')
    return urls_gancho


@pytest.fixture
def expected():
    return {
        'reference': 'SEU_CODIGO_DE_REFERENCIA',
        'preApproval': {
            'charge': 'AUTO', 'name': 'Plano Turma de Curso de Python',
            'details': 'Plano de pagamento da turma Luciano Ramalho', 'amountPerPayment': '180.00',
            'membershipFee': '30.39', 'period': 'MONTHLY',
            'expiration': {
                'value': 10, 'unit': 'MONTHS'
            }
        },
        'receiver': {'email': 'renzo@python.pro.br'}
    }


@responses.activate
def test_criar_plano_no_pagseguro(gerador_plano_recorrente_automatico):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    plano = gerador_plano_recorrente_automatico.criar_no_pagseguro()
    assert (plano.codigo, plano.criacao) == (
        '5CDF6542C6C6D5F114674FB885E40FC0', datetime(2019, 4, 30, 0, 38, 4, tzinfo=pytz.UTC))


@responses.activate
def test_criar_plano_no_pagseguro_headers(gerador_plano_recorrente_automatico):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    gerador_plano_recorrente_automatico.criar_no_pagseguro()
    dct = responses.calls[0].request.headers
    assert dct['Content-Type'] == 'application/json;charset=UTF-8'
    assert dct['Accept'] == 'application/vnd.pagseguro.com.br.v3+json;charset=ISO-8859-1'


@responses.activate
def test_criar_plano_no_pagseguro_payload(gerador_plano_recorrente_automatico, expected):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    gerador_plano_recorrente_automatico.criar_no_pagseguro()

    expected['maxUses'] = 100
    expected['preApproval']['trialPeriodDuration'] = 2
    expected['redirectURL'] = 'https://seusite.com.br/obrigado'
    expected['reviewURL'] = 'https://seusite.com.br/revisar'
    expected['preApproval']['cancelURL'] = 'https://seusite.com.br/cancelar'

    payload = responses.calls[0].request.body
    decodec_payload = json.loads(payload, encoding='UTF-8')
    assert expected == decodec_payload


@responses.activate
def test_criar_plano_sem_urls_gancho(valores_automaticos, expected):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    valores_automaticos.frequencia_mensal().limite_de_uso(100).trial(2).criar_no_pagseguro()

    expected['maxUses'] = 100
    expected['preApproval']['trialPeriodDuration'] = 2

    payload = responses.calls[0].request.body
    decodec_payload = json.loads(payload, encoding='UTF-8')
    assert expected == decodec_payload


@responses.activate
def test_criar_plano_com_limite_de_uso(valores_automaticos, expected):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    valores_automaticos.frequencia_mensal().limite_de_uso(100).criar_no_pagseguro()
    expected['maxUses'] = 100
    payload = responses.calls[0].request.body
    decodec_payload = json.loads(payload, encoding='UTF-8')
    assert expected == decodec_payload


@responses.activate
def test_criar_plano_com_trial(valores_automaticos, expected):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    valores_automaticos.frequencia_mensal().trial(2).criar_no_pagseguro()
    expected['preApproval']['trialPeriodDuration'] = 2
    payload = responses.calls[0].request.body
    decodec_payload = json.loads(payload, encoding='UTF-8')
    assert expected == decodec_payload


@responses.activate
def test_criar_plano_com_urls_gancho(valores_automaticos, expected):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    valores_automaticos.frequencia_mensal().urls_gancho(
        'https://seusite.com.br/obrigado', 'https://seusite.com.br/revisar', 'https://seusite.com.br/cancelar'
    ).criar_no_pagseguro()

    expected['redirectURL'] = 'https://seusite.com.br/obrigado'
    expected['reviewURL'] = 'https://seusite.com.br/revisar'
    expected['preApproval']['cancelURL'] = 'https://seusite.com.br/cancelar'

    payload = responses.calls[0].request.body
    decodec_payload = json.loads(payload, encoding='UTF-8')
    assert expected == decodec_payload


@responses.activate
@pytest.mark.parametrize(
    'funcao_tipo_frequencia, tipo_frequencia',
    [
        ('frequencia_semanal', 'WEEKLY'),
        ('frequencia_mensal', 'MONTHLY'),
        ('frequencia_bimestral', 'BIMONTHLY'),
        ('frequencia_semestral', 'SEMIANNUALLY'),
        ('frequencia_anual', 'YEARLY'),
    ]
)
def test_criar_plano_com_tipos_de_frequencias(valores_automaticos, expected, funcao_tipo_frequencia, tipo_frequencia):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    frequencia = getattr(valores_automaticos, funcao_tipo_frequencia)
    frequencia().criar_no_pagseguro()
    expected['preApproval']['period'] = tipo_frequencia

    payload = responses.calls[0].request.body
    decodec_payload = json.loads(payload, encoding='UTF-8')
    assert expected == decodec_payload


@responses.activate
def test_erro_em_dado():
    response_content = {'error': True, 'errors': {'11003': 'receiverEmail invalid value.'}}
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json=response_content, status=400)
    set_config_padrao(ConfigConta('renzo@python.pro.br', '396FC29DE4A54967BF6DCADE65100E88', SANDBOX))
    criador = CriadorPlanoRecorrente()
    plano_identificacao = criador.plano_automatico_idenficacao(
        'SEU_CODIGO_DE_REFERENCIA',
        'Plano Turma de Curso de Python',
        'Plano de pagamento da turma Luciano Ramalho',
        'renzo.python.pro.br')
    expiracao = plano_identificacao.expiracao_em_meses(meses=10)
    freq = expiracao.valores_automaticos(Decimal('180.00'), Decimal('30.39')).frequencia_mensal()
    with pytest.raises(PagseguroException):
        freq.criar_no_pagseguro()
