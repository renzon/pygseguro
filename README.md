# pygseguro
Projeto para construir um Wrapper Python para a API do [Pagseguro versão 3](https://dev.pagseguro.uol.com.br/reference#ambiente-de-testes)

[![Build Status](https://travis-ci.org/renzon/pygseguro.svg?branch=master)](https://travis-ci.org/renzon/pygseguro)
[![codecov](https://codecov.io/gh/renzon/pygseguro/branch/master/graph/badge.svg)](https://codecov.io/gh/renzon/pygseguro)
[![Updates](https://pyup.io/repos/github/renzon/pygseguro/shield.svg)](https://pyup.io/repos/github/renzon/pygseguro/)
[![Python 3](https://pyup.io/repos/github/renzon/pygseguro/python-3-shield.svg)](https://pyup.io/repos/github/renzon/pygseguro/)

Projeto escrito com Python 3. A linguagem utilizada também para codificar será o português por duas razões:

1. O Pagseguro em si é um Gateway brasileiro com sua documentação em português
1. Essa lib está sendo desenvolvida como projeto prático da turma Luciano Ramalho do curso [Python Pro](https://www.python.pro.br)

# Contribuidores

Renzo Nuccitelli (@renzon)
Tânio Scherer (@taniodev)

# Instalação

Instale o pipenv:

```
pip install pipenv
```

Para instalar a lib com pipenv:
```
pipenv install pygseguro
```

# Como usar

## Configuração Padrão

Utilize essa configuração se as chamadas costumam usar sempre a mesma configuração
```python

>>> from pygseguro import set_config_padrao, get_config_padrao, ConfigConta
>>> get_config_padrao()
>>> cfg = ConfigConta(email='foo@bar.com', token='blah')
>>> set_config_padrao(cfg)
>>> get_config_padrao()
ConfigConta(email='foo@bar.com', token='****')
>>> cfg.construir_url('/caminho')
'https://ws.pagseguro.uol.com.br/caminho?email=foo@bar.com&token=blah'


```

Você pode usar uma configuração por appId e appToken:

```python

>>> from pygseguro import ConfigApp
>>> cfg_app = ConfigApp(app_id='1234', app_key='xpto', )
>>> set_config_padrao(cfg_app)
>>> get_config_padrao()
ConfigApp(app_id='1234', app_key='****')
>>> cfg_app.construir_url('/outro_caminho')
'https://ws.pagseguro.uol.com.br/outro_caminho?appID=1234&appKey=xpto'


```


# Criando planos de [pagamento recorrente automático](https://dev.pagseguro.uol.com.br/reference#api-pagamento-recorrente-criacao-do-plano)

## Forma com passos intermediários:

```python
>>> from pygseguro import SANDBOX, CriadorPlanoRecorrente
>>> from datetime import datetime
>>> from decimal import Decimal
>>> set_config_padrao(ConfigConta('renzo@python.pro.br', '396FC29DE4A54967BF6DCADE65100E88', SANDBOX))
>>> criador = CriadorPlanoRecorrente()
>>> plano_identificacao = criador.plano_automatico_idenficacao(
...     'SEU_CODIGO_DE_REFERENCIA',
...     'Plano Turma de Curso de Python',
...     'Plano de pagamento da turma Luciano Ramalho',
...     'renzo@python.pro.br')
>>> expiracao = plano_identificacao.expiracao_em_meses(meses=10)
>>> valores_automaticos = expiracao.valores_automaticos(Decimal('180.00'), Decimal('30.39'))
>>> freq_mensal = valores_automaticos.frequencia_mensal()
>>> trial = freq_mensal.trial(dias=2)
>>> limite_de_uso = trial.limite_de_uso(100)
>>> urls_gancho = limite_de_uso.urls_gancho(
...     'https://seusite.com.br/obrigado', 'https://seusite.com.br/revisar', 'https://seusite.com.br/cancelar'
... )
>>> plano_recorrente=urls_gancho.criar_no_pagseguro()
>>> isinstance(plano_recorrente.codigo, str)
True
>>> isinstance(plano_recorrente.criacao, datetime)
True

```


## Forma direta:

```python
>>> plano_recorrente = CriadorPlanoRecorrente().plano_automatico_idenficacao(
...     'SEU_CODIGO_DE_REFERENCIA',
...     'Plano Turma de Curso de Python',
...     'Plano de pagamento da turma Luciano Ramalho',
...     'renzo@python.pro.br'
... ).expiracao_em_meses(meses=10).valores_automaticos(
...     Decimal('180.00'), Decimal('30.39')
... ).frequencia_mensal().trial(dias=2).limite_de_uso(100).urls_gancho(
...     'https://seusite.com.br/obrigado', 'https://seusite.com.br/revisar', 'https://seusite.com.br/cancelar'
... ).criar_no_pagseguro()
>>> isinstance(plano_recorrente.codigo, str)
True
>>> isinstance(plano_recorrente.criacao, datetime)
True

```


# Como contribuir

Todo código segue a [PEP8](https://www.python.org/dev/peps/pep-0008/), com exceção do tamanho da linha, que aceita 120 caracteres.
Toda função/classe/método/módulo deve possuir docstrings
Toda função/método deve ter annotations

1. Faça o fork do projeto e clone or projeto: `git clone git@github.com:<seu_usuario>/pygseguro.git`
1. Instale o pipenv: `pip install pipenv`
1. Instale as dependências de dev: `pipenv install -d`
1. Desenvolva a feature com testes
1. Rode os teste localmente: `pipenv run pytest`
1. Envie o pull request com teste em um só commit
1. Envie o PR para revisão
1. Depois de revisado e corrigido, o PR será aceito e a lib postada no PyPi
1. Coloque seu nome e username na porção contribuidores

