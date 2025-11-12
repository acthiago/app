import requests
from selectolax.parser import HTMLParser
from .base import BaseExtractor
import logging
import re
import json

logger = logging.getLogger(__name__)

class KabumExtractor(BaseExtractor):
    def __init__(self, url: str):
        super().__init__(url)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def resolve_url(self) -> str:
        """Resolve shortened URLs (tidd.ly) and redirects to full Kabum URL"""
        try:
            response = requests.get(self.url, headers=self.headers, allow_redirects=True, timeout=15)
            return response.url
        except Exception as e:
            logger.error(f"Erro ao resolver URL da Kabum: {e}")
            return self.url

    def extract(self) -> dict:
        """Extract product data from Kabum"""
        try:
            final_url = self.resolve_url()
            logger.info(f"Kabum URL resolvida: {final_url}")
            
            r = requests.get(final_url, headers=self.headers, timeout=15)
            html = HTMLParser(r.text)

            # Extrair dados do JSON-LD (fonte principal)
            json_ld_data = {}
            scripts = html.css("script[type='application/ld+json']")
            for script in scripts:
                try:
                    data = json.loads(script.text())
                    if isinstance(data, dict) and data.get("@type") == "Product":
                        json_ld_data = data
                        break
                except:
                    pass

            # Extrair título
            title = json_ld_data.get("name", "")
            if not title:
                title_tag = html.css_first("h1.finalPrice, h1[itemprop='name']")
                if title_tag:
                    title = title_tag.text().strip()
            
            # Fallback: tentar meta tag
            if not title:
                meta_title = html.css_first("meta[property='og:title']")
                if meta_title:
                    title = meta_title.attributes.get("content", "")

            # Extrair preço (priorizar JSON-LD)
            price = ""
            original_price = ""
            discount = ""
            
            # Método 1: JSON-LD (mais confiável)
            if "offers" in json_ld_data:
                offers = json_ld_data["offers"]
                if offers.get("price"):
                    price = str(offers["price"])
            
            # Método 2: Buscar preço HTML
            if not price:
                price_elem = html.css_first("h4.finalPrice")
                if price_elem:
                    price_text = price_elem.text().strip()
                    price = re.sub(r'[^\d,.]', '', price_text).replace(".", "").replace(",", ".")
            
            # Preço original (sem desconto)
            original_price_elem = html.css_first("span.oldPrice")
            if original_price_elem:
                original_text = original_price_elem.text().strip()
                original_price = re.sub(r'[^\d,.]', '', original_text).replace(".", "").replace(",", ".")
            
            # Calcular desconto se temos ambos os preços
            if price and original_price:
                try:
                    price_float = float(price)
                    original_float = float(original_price)
                    if original_float > price_float:
                        discount_pct = ((original_float - price_float) / original_float) * 100
                        discount = f"-{int(discount_pct)}%"
                except ValueError:
                    pass
            
            # Extrair parcelamento
            installments = ""
            installments_elem = html.css_first("p.regularPrice")
            if installments_elem:
                installments = installments_elem.text().strip()
            
            # Extrair descrição (priorizar JSON-LD)
            description = json_ld_data.get("description", "")
            
            # Fallback: meta description
            if not description:
                meta_desc = html.css_first("meta[name='description']")
                if meta_desc:
                    description = meta_desc.attributes.get("content", "")
            
            # Se não encontrou, tentar características principais
            if not description:
                features = html.css("div.sc-dcJsrY p")
                if features:
                    features_list = [feat.text().strip() for feat in features[:3] if feat.text().strip()]
                    description = " | ".join(features_list)
            
            # Limitar tamanho da descrição
            if description and len(description) > 500:
                description = description[:497] + "..."

            # Extrair imagens - buscar TODAS as imagens do produto
            images = []
            unique_images = set()
            
            # 1. Buscar todas as tags <img> da página
            all_imgs = html.css("img")
            for img in all_imgs:
                src = img.attributes.get("src", "")
                data_src = img.attributes.get("data-src", "")
                
                # Processar ambas as fontes
                for img_url in [src, data_src]:
                    if img_url and ("produto" in img_url or "fotos" in img_url or "sync_mirakl" in img_url):
                        # Normalizar para alta qualidade (_gg.jpg ou _g.jpg)
                        img_url = img_url.replace("_small", "").replace("_medium", "").replace("_m.jpg", "_g.jpg").replace("_p.jpg", "_gg.jpg")
                        
                        # Filtrar logos e ícones
                        if "logo-nulo" not in img_url and "logo" not in img_url.lower().split("/")[-1]:
                            unique_images.add(img_url)
            
            # 2. JSON-LD (garantir imagem principal)
            if "image" in json_ld_data:
                json_images = json_ld_data["image"]
                if isinstance(json_images, list):
                    for img in json_images:
                        if img.startswith("http"):
                            unique_images.add(img)
                elif isinstance(json_images, str) and json_images.startswith("http"):
                    unique_images.add(json_images)
            
            # 3. og:image como fallback
            if not unique_images:
                og_image = html.css_first("meta[property='og:image']")
                if og_image:
                    main_image = og_image.attributes.get("content", "")
                    if main_image and main_image.startswith("http"):
                        unique_images.add(main_image)
            
            # Converter para lista ordenada e limitar a 15 imagens
            images = sorted(list(unique_images))[:15]
            
            logger.info(f"Kabum: Extraídas {len(images)} imagens únicas do produto")

            # Extrair marca
            brand = ""
            if "brand" in json_ld_data:
                brand_data = json_ld_data["brand"]
                if isinstance(brand_data, dict):
                    brand = brand_data.get("name", "")
                elif isinstance(brand_data, str):
                    brand = brand_data

            # Extrair SKU
            sku = json_ld_data.get("sku", "")
            
            # Extrair avaliação do JSON-LD
            rating = ""
            reviews_count = ""
            if "aggregateRating" in json_ld_data:
                aggregate = json_ld_data["aggregateRating"]
                rating = str(aggregate.get("ratingValue", ""))
                reviews_count = str(aggregate.get("reviewCount", ""))
            
            # Fallback HTML
            if not rating:
                rating_elem = html.css_first("span[itemprop='ratingValue']")
                if rating_elem:
                    rating = rating_elem.text().strip()
            
            if not reviews_count:
                reviews_elem = html.css_first("span[itemprop='reviewCount']")
                if reviews_elem:
                    reviews_count = reviews_elem.text().strip()

            # Disponibilidade do JSON-LD
            availability = "Em estoque"
            if "offers" in json_ld_data:
                offers = json_ld_data["offers"]
                avail_url = offers.get("availability", "")
                if "InStock" in avail_url:
                    availability = "Em estoque"
                elif "OutOfStock" in avail_url:
                    availability = "Indisponível"
                elif "PreOrder" in avail_url:
                    availability = "Pré-venda"
            
            # Fallback HTML
            if not availability or availability == "Em estoque":
                availability_elem = html.css_first("span.availability")
                if availability_elem:
                    availability = availability_elem.text().strip()
                elif "indisponível" in r.text.lower() or "esgotado" in r.text.lower():
                    availability = "Indisponível"

            # Categoria
            category = ""
            breadcrumb = html.css("nav.breadcrumb a")
            if breadcrumb and len(breadcrumb) > 1:
                # Pegar a penúltima categoria (última antes do produto)
                category = breadcrumb[-1].text().strip() if breadcrumb else ""

            data = {
                "url": final_url,
                "source": "Kabum",
                "title": title,
                "price": price,
                "original_price": original_price,
                "discount": discount,
                "installments": installments,
                "currency": "BRL",
                "image": images[0] if images else "",
                "images": images,
                "description": description,
                "rating": rating,
                "reviews_count": reviews_count,
                "availability": availability,
                "category": category,
                "brand": brand,
                "sku": sku
            }
            
            logger.info(f"Kabum: Dados extraídos com sucesso - {title[:50]}...")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da Kabum: {e}")
            return {
                "url": self.url,
                "source": "Kabum",
                "title": "",
                "price": "",
                "error": str(e)
            }
