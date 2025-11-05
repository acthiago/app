import requests
from selectolax.parser import HTMLParser
from .base import BaseExtractor
import logging

logger = logging.getLogger(__name__)

class MercadoLivreExtractor(BaseExtractor):
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
        r = requests.get(final_url, headers=self.headers, timeout=10)
        html = HTMLParser(r.text)

        title_tag = html.css_first("meta[property='og:title']")
        price_tag = html.css_first("meta[property='product:price:amount']")
        currency_tag = html.css_first("meta[property='product:price:currency']")
        image_tag = html.css_first("meta[property='og:image']")
        desc_tag = html.css_first("meta[name='description']")
        
        # Extrair múltiplas imagens
        images = []
        
        # 1. Imagem principal do og:image
        if image_tag:
            main_image = image_tag.attributes.get("content", "")
            if main_image:
                images.append(main_image)
        
        # 2. Buscar galeria de imagens (thumbnails e imagens grandes)
        # Mercado Livre usa diferentes estruturas, vamos tentar várias
        
        # Tentar pegar imagens da galeria principal
        gallery_images = html.css("figure.ui-pdp-gallery__figure img")
        for img in gallery_images:
            img_src = img.attributes.get("src", "") or img.attributes.get("data-src", "")
            if img_src and img_src not in images and not img_src.startswith("data:"):
                # Substituir thumbnail por imagem grande
                img_src = img_src.replace("-I.jpg", "-O.jpg").replace("-F.jpg", "-O.jpg").replace("-I.webp", "-O.webp").replace("-F.webp", "-O.webp")
                images.append(img_src)
        
        # Tentar pegar do carrossel de thumbnails
        thumbnail_images = html.css("img.ui-pdp-thumbnail__image")
        for img in thumbnail_images:
            img_src = img.attributes.get("src", "") or img.attributes.get("data-src", "")
            if img_src and img_src not in images and not img_src.startswith("data:"):
                # Substituir thumbnail por imagem grande
                img_src = img_src.replace("-I.jpg", "-O.jpg").replace("-F.jpg", "-O.jpg").replace("-I.webp", "-O.webp").replace("-F.webp", "-O.webp")
                images.append(img_src)
        
        # Tentar pegar de outras classes comuns do ML
        if len(images) <= 1:
            # Buscar imagens em diferentes seletores
            ml_images = html.css("img.ui-pdp-image, img[class*='gallery'], img[class*='carousel']")
            for img in ml_images:
                img_src = img.attributes.get("src", "") or img.attributes.get("data-src", "") or img.attributes.get("data-zoom", "")
                if img_src and img_src not in images and not img_src.startswith("data:") and "mlstatic.com" in img_src:
                    img_src = img_src.replace("-I.jpg", "-O.jpg").replace("-F.jpg", "-O.jpg").replace("-I.webp", "-O.webp").replace("-F.webp", "-O.webp")
                    images.append(img_src)
        
        # Buscar no HTML todas as imagens do mlstatic (fallback)
        if len(images) <= 1:
            all_ml_imgs = html.css("img[src*='mlstatic.com']")
            for img in all_ml_imgs:
                img_src = img.attributes.get("src", "")
                # Filtrar apenas imagens de produtos (que tem NQ_NP no path)
                if img_src and "NQ_NP" in img_src and img_src not in images:
                    img_src = img_src.replace("-I.jpg", "-O.jpg").replace("-F.jpg", "-O.jpg").replace("-I.webp", "-O.webp").replace("-F.webp", "-O.webp")
                    images.append(img_src)
        
        # Limitar a 10 imagens para não sobrecarregar
        images = list(dict.fromkeys(images))  # Remove duplicatas mantendo ordem
        images = images[:10]
        
        # Log para debug
        logger.info(f"Mercado Livre: Extraídas {len(images)} imagens do produto")

        # Extrair preço e informações adicionais
        price = price_tag.attributes.get("content", "") if price_tag else ""
        original_price = ""
        discount = ""
        installments = ""
        
        if not price:
            # Buscar preço atual no HTML (dentro de poly-price__current)
            current_price_div = html.css_first("div.poly-price__current")
            if current_price_div:
                price_fraction = current_price_div.css_first("span.andes-money-amount__fraction")
                price_cents = current_price_div.css_first("span.andes-money-amount__cents")
                if price_fraction:
                    price = price_fraction.text().strip()
                    if price_cents:
                        price = f"{price}.{price_cents.text().strip()}"
            
            # Buscar preço original (antes do desconto)
            original_price_span = html.css_first("s.andes-money-amount--previous")
            if original_price_span:
                orig_fraction = original_price_span.css_first("span.andes-money-amount__fraction")
                orig_cents = original_price_span.css_first("span.andes-money-amount__cents")
                if orig_fraction:
                    original_price = orig_fraction.text().strip()
                    if orig_cents:
                        original_price = f"{original_price}.{orig_cents.text().strip()}"
            
            # Buscar desconto
            discount_tag = html.css_first("span.andes-money-amount__discount")
            if discount_tag:
                discount = discount_tag.text().strip()
            
            # Buscar parcelamento
            installments_tag = html.css_first("span.poly-price__installments")
            if installments_tag:
                installments = installments_tag.text().strip()

        data = {
            "url": final_url,
            "source": "Mercado Livre",
            "title": title_tag.attributes.get("content", "") if title_tag else "",
            "price": price,
            "original_price": original_price,
            "discount": discount,
            "installments": installments,
            "currency": currency_tag.attributes.get("content", "BRL") if currency_tag else "BRL",
            "image": images[0] if images else "",  # Primeira imagem (compatibilidade)
            "images": images,  # Lista completa de imagens
            "description": desc_tag.attributes.get("content", "") if desc_tag else ""
        }
        return data
