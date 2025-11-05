import requests
from selectolax.parser import HTMLParser
from .base import BaseExtractor
import time

class ShopeeExtractor(BaseExtractor):
    def __init__(self, url: str):
        super().__init__(url)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    def resolve_url(self) -> str:
        response = requests.get(self.url, headers=self.headers, allow_redirects=True, timeout=15)
        return response.url

    def extract(self) -> dict:
        final_url = self.resolve_url()
        
        # Pequeno delay para evitar detecção
        time.sleep(1)
        
        r = requests.get(final_url, headers=self.headers, timeout=15)
        html = HTMLParser(r.text)

        # Verificar se houve CAPTCHA ou bloqueio
        page_content = r.text.lower()
        note = ""
        if 'captcha' in page_content:
            note = "Shopee: CAPTCHA detectado. Tente acessar manualmente ou aguarde."
        elif 'robot' in page_content or 'access denied' in page_content:
            note = "Shopee: Detecção de bot. Use o link diretamente no navegador."
        elif len(r.text) < 1000:
            note = "Shopee: Página com conteúdo limitado. Dados podem estar incompletos."
        else:
            note = "Shopee: preço pode estar vazio devido à renderização dinâmica. Adicione manualmente se necessário."

        # Tentar extrair dados básicos
        title_tag = html.css_first("meta[property='og:title']")
        image_tag = html.css_first("meta[property='og:image']")
        desc_tag = html.css_first("meta[name='description']")
        
        # Extrair múltiplas imagens
        images = []
        
        # 1. Imagem principal do og:image
        if image_tag:
            main_image = image_tag.attributes.get("content", "")
            if main_image:
                images.append(main_image)
        
        # 2. Buscar outras imagens do produto (Shopee usa JSON embarcado)
        # Tentar pegar imagens de elementos img
        product_images = html.css("div._2JJaD7 img, div.shopee-image-viewer img")
        for img in product_images:
            img_src = img.attributes.get("src", "") or img.attributes.get("data-src", "")
            if img_src and img_src not in images and not img_src.startswith("data:"):
                images.append(img_src)
        
        # Limitar a 10 imagens
        images = images[:10]
        
        # Se meta tags OG não funcionarem, tentar outras abordagens
        title = ""
        if title_tag:
            title = title_tag.attributes.get("content", "")
        else:
            # Tentar extrair título do HTML
            title_elem = html.css_first('title')
            if title_elem:
                title = title_elem.text().strip()

        data = {
            "url": final_url,
            "source": "Shopee",
            "title": title,
            "price": "",
            "original_price": "",
            "discount": "",
            "installments": "",
            "currency": "BRL",
            "image": images[0] if images else "",  # Primeira imagem (compatibilidade)
            "images": images,  # Lista completa de imagens
            "description": desc_tag.attributes.get("content", "") if desc_tag else "",
            "note": note
        }
        return data
