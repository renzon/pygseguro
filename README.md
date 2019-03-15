# pygseguro
Projeto para construir um Wrapper Python para a API do Pagseguro

[![Build Status](https://travis-ci.org/renzon/pygseguro.svg?branch=master)](https://travis-ci.org/renzon/pygseguro)
[![codecov](https://codecov.io/gh/renzon/pygseguro/branch/master/graph/badge.svg)](https://codecov.io/gh/renzon/pygseguro)
[![Updates](https://pyup.io/repos/github/renzon/pygseguro/shield.svg)](https://pyup.io/repos/github/renzon/pygseguro/)
[![Python 3](https://pyup.io/repos/github/renzon/pygseguro/python-3-shield.svg)](https://pyup.io/repos/github/renzon/pygseguro/)

Projeto escrito com Python 3.

# Contribuidores

Renzo Nuccitelli (@renzon)

# Instalação

Instale o pipenv:

```
pip install pipenv
```

Para instalar a lib com pipenv:
```
pipenv install pygseguro
```

# Como contribuir

Todo código segue a [PEP8](https://www.python.org/dev/peps/pep-0008/), com exceção do tamanho da linha, que aceita 120 caracteres.
Toda função/classe/método/módulo deve possuir docstrings
Toda função/método deve ter annotations

1. Falça o fork do projeto e clone or projeto: `git clone git@github.com:<seu_usuario>/pygseguro.git`
1. Instale o pipenv: `pip install pipenv`
1. Instale as dependêncais de dev: `pipenv install -d`
1. Desenvolva a feature com testes
1. Rode os teste localmente: `pipenv run pytest`
1. Envie o pull request com teste e um só commmit
1. Envie o PR para revisão
1. Depois de revisado e corrigido, o PR será aceito e a lib postada no PyPi
1. Coloque seu nome e username na porção contribuidores

