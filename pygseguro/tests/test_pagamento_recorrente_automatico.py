import json
from datetime import datetime
from decimal import Decimal

import pytest
import pytz
import responses

from pygseguro import ConfigConta, CriadorPlanoRecorrente, SANDBOX, set_config_padrao


@pytest.fixture
def valores_automaticos():
    set_config_padrao(ConfigConta('renzo@python.pro.br', '396FC29DE4A54967BF6DCADE65100E88', SANDBOX))
    criador = CriadorPlanoRecorrente()
    plano_identificacao = criador.plano_automatico_idenficacao(
        'SEU_CODIGO_DE_REFERENCIA',
        'Plano Turma de Curso de Python',
        'Plano de pagamento da turma Luciano Ramalho',
        'renzo@python.pro.br')
    freq_mensal = plano_identificacao.frequencia_mensal()
    expiracao = freq_mensal.expiracao_em_meses(meses=10)
    return expiracao.trial(dias=2).limite_de_uso(100).valores_automaticos(Decimal('180.00'), Decimal('30.39'))


@pytest.fixture
def gerador_plano_recorrente_automatico(valores_automaticos):
    urls_gancho = valores_automaticos.urls_gancho('https://seusite.com.br/obrigado', 'https://seusite.com.br/revisar',
                                                  'https://seusite.com.br/cancelar')
    return urls_gancho


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
def test_criar_plano_no_pagseguro_payload(gerador_plano_recorrente_automatico):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    gerador_plano_recorrente_automatico.criar_no_pagseguro()

    expected = {
        'reference': 'SEU_CODIGO_DE_REFERENCIA', 'maxUses': 100, 'redirectURL': 'https://seusite.com.br/obrigado',
        'reviewURL': 'https://seusite.com.br/revisar',
        'preApproval': {
            'charge': 'AUTO', 'name': 'Plano Turma de Curso de Python',
            'details': 'Plano de pagamento da turma Luciano Ramalho', 'amountPerPayment': '180.00',
            'trialPeriodDuration': 2, 'membershipFee': '30.39', 'period': 'MONTHLY',
            'cancelURL': 'https://seusite.com.br/cancelar',
            'expiration': {
                'value': 10, 'unit': 'MONTHS'
            }
        },
        'receiver': {'email': 'renzo@python.pro.br'}
    }
    payload = responses.calls[0].request.body
    decodec_payload = json.loads(payload, encoding='UTF-8')
    assert expected == decodec_payload


@responses.activate
def test_criar_plano_sem_urls_gancho(valores_automaticos):
    responses.add(responses.POST, 'https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request',
                  json={'code': '5CDF6542C6C6D5F114674FB885E40FC0', 'date': '2019-04-29T21:38:04-03:00'}, status=200)
    valores_automaticos.criar_no_pagseguro()

    expected = {
        'reference': 'SEU_CODIGO_DE_REFERENCIA', 'maxUses': 100,
        'preApproval': {
            'charge': 'AUTO', 'name': 'Plano Turma de Curso de Python',
            'details': 'Plano de pagamento da turma Luciano Ramalho', 'amountPerPayment': '180.00',
            'trialPeriodDuration': 2, 'membershipFee': '30.39', 'period': 'MONTHLY',
            'expiration': {
                'value': 10, 'unit': 'MONTHS'
            }
        },
        'receiver': {'email': 'renzo@python.pro.br'}
    }
    payload = responses.calls[0].request.body
    decodec_payload = json.loads(payload, encoding='UTF-8')
    assert expected == decodec_payload
