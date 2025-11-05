from urllib.parse import urlparse
from .mercadolivre import MercadoLivreExtractor
from .aliexpress import AliExpressExtractor
from .shopee import ShopeeExtractor

def get_extractor(url: str):
    domain = urlparse(url).netloc.lower()

    if "mercadolivre" in domain:
        return MercadoLivreExtractor(url)
    elif "aliexpress" in domain:
        return AliExpressExtractor(url)
    elif "shopee" in domain:
        return ShopeeExtractor(url)
    else:
        raise ValueError(f"Domínio não suportado: {domain}")
