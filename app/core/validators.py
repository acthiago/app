"""
Validadores Pydantic customizados
"""
from pydantic import validator, Field
from typing import Optional
import re

def validate_url(url: str) -> str:
    """Valida se a string é uma URL válida"""
    url_pattern = re.compile(
        r'^https?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domínio
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ou IP
        r'(?::\d+)?'  # porta opcional
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        raise ValueError('URL inválida. Deve começar com http:// ou https://')
    return url


def validate_password_strength(password: str) -> str:
    """Valida força da senha"""
    if len(password) < 8:
        raise ValueError('Senha deve ter no mínimo 8 caracteres')
    
    if not re.search(r'[A-Z]', password):
        raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
    
    if not re.search(r'[a-z]', password):
        raise ValueError('Senha deve conter pelo menos uma letra minúscula')
    
    if not re.search(r'\d', password):
        raise ValueError('Senha deve conter pelo menos um número')
    
    return password


def validate_text_length(text: str, max_length: int = 1000) -> str:
    """Valida tamanho máximo de texto"""
    if len(text) > max_length:
        raise ValueError(f'Texto excede o limite de {max_length} caracteres')
    return text


def validate_slug(slug: str) -> str:
    """Valida formato de slug"""
    slug_pattern = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    if not slug_pattern.match(slug):
        raise ValueError('Slug deve conter apenas letras minúsculas, números e hífens')
    return slug


# Tipos reutilizáveis
class URLStr(str):
    """String validada como URL"""
    @classmethod
    def __get_validators__(cls):
        yield validate_url


class StrongPassword(str):
    """String validada como senha forte"""
    @classmethod
    def __get_validators__(cls):
        yield validate_password_strength


class SlugStr(str):
    """String validada como slug"""
    @classmethod
    def __get_validators__(cls):
        yield validate_slug
