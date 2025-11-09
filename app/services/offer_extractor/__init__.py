from .factory import get_extractor
from .base import BaseExtractor
from .mercadolivre import MercadoLivreExtractor
from .aliexpress import AliExpressExtractor
from .shopee import ShopeeExtractor
from .amazon import AmazonExtractor

__all__ = [
    'get_extractor',
    'BaseExtractor',
    'MercadoLivreExtractor',
    'AliExpressExtractor',
    'ShopeeExtractor',
    'AmazonExtractor'
]
