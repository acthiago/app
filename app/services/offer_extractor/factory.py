from urllib.parse import urlparse
from .mercadolivre import MercadoLivreExtractor
from .aliexpress import AliExpressExtractor
from .shopee import ShopeeExtractor
from .amazon import AmazonExtractor
from .kabum import KabumExtractor

def get_extractor(url: str):
    domain = urlparse(url).netloc.lower()

    if "mercadolivre" in domain or "mercadolibre" in domain:
        return MercadoLivreExtractor(url)
    elif "aliexpress" in domain:
        return AliExpressExtractor(url)
    elif "shopee" in domain:
        return ShopeeExtractor(url)
    elif "amazon" in domain or "amzn.to" in domain:
        return AmazonExtractor(url)
    elif "kabum.com.br" in domain or "tidd.ly" in domain:
        return KabumExtractor(url)
    else:
        raise ValueError(f"Domínio não suportado: {domain}")
