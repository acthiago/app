import requests
from selectolax.parser import HTMLParser
from .base import BaseExtractor

class AliExpressExtractor(BaseExtractor):
    def __init__(self, url: str):
        super().__init__(url)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def resolve_url(self) -> str:
        response = requests.get(self.url, headers=self.headers, allow_redirects=True, timeout=10)
        return response.url

    def extract(self) -> dict:
        final_url = self.resolve_url()
        r = requests.get(final_url, headers=self.headers, timeout=15)
        html = HTMLParser(r.text)

        title_tag = html.css_first("meta[property='og:title']")
        price_tag = html.css_first("meta[property='product:price:amount']")
        currency_tag = html.css_first("meta[property='product:price:currency']")
        image_tag = html.css_first("meta[property='og:image']")
        desc_tag = html.css_first("meta[property='og:description']")
        
        # Extrair múltiplas imagens
        images = []
        
        # 1. Imagem principal do og:image
        if image_tag:
            main_image = image_tag.attributes.get("content", "")
            if main_image:
                images.append(main_image)
        
        # 2. Buscar imagens do produto (AliExpress usa classes específicas)
        product_images = html.css("img.magnifier-image, div.images-view-item img")
        for img in product_images:
            img_src = img.attributes.get("src", "") or img.attributes.get("data-src", "")
            if img_src and img_src not in images and not img_src.startswith("data:"):
                images.append(img_src)
        
        # Limitar a 10 imagens
        images = images[:10]

        # AliExpress usa renderização client-side, então meta tags são limitadas
        # O título e imagem funcionam, mas o preço precisa ser inserido manualmente
        data = {
            "url": final_url,
            "source": "AliExpress",
            "title": title_tag.attributes.get("content", "") if title_tag else "",
            "price": price_tag.attributes.get("content", "") if price_tag else "",
            "original_price": "",
            "discount": "",
            "installments": "",
            "currency": currency_tag.attributes.get("content", "USD") if currency_tag else "USD",
            "image": images[0] if images else "",  # Primeira imagem (compatibilidade)
            "images": images,  # Lista completa de imagens
            "description": desc_tag.attributes.get("content", "") if desc_tag else "",
            "note": "AliExpress: preço pode estar vazio devido à renderização dinâmica. Adicione manualmente se necessário."
        }
        return data
