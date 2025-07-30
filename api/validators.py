import re
from marshmallow import ValidationError

class CNPJValidator:
    """
    Valida CNPJ alfanumérico (novo padrão Febraban):
    - Apenas letras maiúsculas A-Z e dígitos 0-9
    - Comprimento entre 14 e 18 caracteres
    """
    def __call__(self, value):
        if not isinstance(value, str):
            raise ValidationError('CNPJ deve ser uma string')
        cnpj = value.strip().upper()
        # Valida formato alfanumérico
        if not re.fullmatch(r'[A-Z0-9]{14,18}', cnpj):
            raise ValidationError(
                'CNPJ inválido: deve conter apenas letras maiúsculas e dígitos, 14-18 caracteres'
            )
        # Se necessário, aplique aqui lógica adicional de verificação de dígitos
        return cnpj
