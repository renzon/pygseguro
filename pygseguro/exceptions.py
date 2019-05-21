from typing import Dict


class PagseguroException(Exception):
    def __init__(self, payload: Dict, status_code: int) -> None:
        super().__init__(payload)
        self.status_code = status_code
        self.erros = payload['errors']
