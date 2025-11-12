import requests
from selectolax.parser import HTMLParser
from .base import BaseExtractor
import logging
import re
import json

logger = logging.getLogger(__name__)

class AmazonExtractor(BaseExtractor):
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
        """Resolve shortened URLs (amzn.to) and redirects to full Amazon URL"""
        try:
            response = requests.get(self.url, headers=self.headers, allow_redirects=True, timeout=15)
            return response.url
        except Exception as e:
            logger.error(f"Erro ao resolver URL da Amazon: {e}")
            return self.url

    def extract(self) -> dict:
        """Extract product data from Amazon"""
        try:
            final_url = self.resolve_url()
            logger.info(f"Amazon URL resolvida: {final_url}")
            
            r = requests.get(final_url, headers=self.headers, timeout=15)
            html = HTMLParser(r.text)

            # Extrair título
            title = ""
            title_tag = html.css_first("#productTitle")
            if title_tag:
                title = title_tag.text().strip()
            else:
                # Tentar meta tag
                meta_title = html.css_first("meta[property='og:title']")
                if meta_title:
                    title = meta_title.attributes.get("content", "")

            # Extrair preço
            price = ""
            original_price = ""
            discount = ""
            
            # === PREÇO ATUAL (com desconto) ===
            # Método 1: Buscar no elemento principal de preço (mais confiável)
            price_elem = html.css_first("span.a-price[data-a-size='xl'] span.a-offscreen, span.priceToPay span.a-offscreen")
            if price_elem:
                price_text = price_elem.text().strip()
                price = re.sub(r'[^\d,.]', '', price_text).replace(",", ".")
            
            # Método 2: Buscar por a-price-whole e a-price-fraction (fallback)
            if not price:
                price_whole = html.css_first("span.a-price:not(.a-text-price) span.a-price-whole")
                price_fraction = html.css_first("span.a-price:not(.a-text-price) span.a-price-fraction")
                if price_whole:
                    price = price_whole.text().strip().replace(".", "").replace(",", ".")
                    if price_fraction:
                        fraction = price_fraction.text().strip()
                        if fraction and fraction != "00":
                            price = price.rstrip(".")
                            price = f"{price}.{fraction}"
            
            # === PREÇO ORIGINAL (antes do desconto) ===
            # Método 1: Buscar "De: R$ XXX" com texto riscado
            de_elements = html.css("span.a-text-strike")
            for elem in de_elements:
                strike_text = elem.text().strip()
                # Extrair apenas números
                potential_original = re.sub(r'[^\d,.]', '', strike_text).replace(",", ".")
                try:
                    if potential_original and (not price or float(potential_original) > float(price)):
                        original_price = potential_original
                        break  # Pegar o primeiro que encontrar (geralmente é o do produto principal)
                except ValueError:
                    continue
            
            # Método 2: Buscar em span.a-price.a-text-price (fallback)
            if not original_price:
                text_price_elements = html.css("span.a-price.a-text-price")
                for elem in text_price_elements:
                    offscreen = elem.css_first("span.a-offscreen")
                    if offscreen:
                        original_text = offscreen.text().strip()
                        potential_original = re.sub(r'[^\d,.]', '', original_text).replace(",", ".")
                        try:
                            if potential_original and (not price or float(potential_original) > float(price)):
                                original_price = potential_original
                                break
                        except ValueError:
                            continue
            
            # Método 3: Buscar basisPrice (outro fallback)
            if not original_price:
                de_price = html.css_first("span.basisPrice span.a-offscreen")
                if de_price:
                    de_text = de_price.text().strip()
                    potential_original = re.sub(r'[^\d,.]', '', de_text).replace(",", ".")
                    try:
                        if potential_original and (not price or float(potential_original) > float(price)):
                            original_price = potential_original
                    except ValueError:
                        pass
            
            # === DESCONTO PERCENTUAL ===
            # Método 1: span.savingsPercentage
            discount_elem = html.css_first("span.savingsPercentage")
            if discount_elem:
                discount = discount_elem.text().strip()
            
            # Método 2: Calcular manualmente se temos ambos os preços
            if not discount and price and original_price:
                try:
                    price_float = float(price)
                    original_float = float(original_price)
                    if original_float > price_float:
                        discount_pct = ((original_float - price_float) / original_float) * 100
                        discount = f"-{int(discount_pct)}%"
                except ValueError:
                    pass
            
            # Extrair descrição
            description = ""
            # Tentar meta description
            meta_desc = html.css_first("meta[name='description']")
            if meta_desc:
                description = meta_desc.attributes.get("content", "")
            
            # Se não encontrou, tentar feature bullets
            if not description:
                feature_bullets = html.css("#feature-bullets ul.a-unordered-list li span.a-list-item")
                if feature_bullets:
                    features = [bullet.text().strip() for bullet in feature_bullets if bullet.text().strip()]
                    description = " | ".join(features[:3])  # Primeiras 3 features

            # Extrair imagens - sistema aprimorado para evitar duplicatas
            images = []
            image_ids = set()  # Para rastrear IDs únicos de imagens (parte do nome do arquivo)
            
            def extract_image_id(url):
                """Extrai ID único da imagem Amazon (ex: 51abc123.jpg -> 51abc123)"""
                # Buscar padrão de ID de imagem: letras/números antes da extensão
                match = re.search(r'/([A-Z0-9+\-]{10,})[\._]', url)
                if match:
                    return match.group(1)
                # Fallback: pegar o nome do arquivo
                match = re.search(r'/([^/]+)\.(jpg|jpeg|png|gif|webp)', url, re.IGNORECASE)
                return match.group(1) if match else url
            
            def add_image(img_url):
                """Adiciona imagem se não for duplicata"""
                if not img_url or not img_url.startswith("http"):
                    return False
                
                # Filtrar imagens inválidas (gifs transparentes, play buttons, etc)
                lower_url = img_url.lower()
                invalid_patterns = ['transparent-pixel', 'play-button', 'pkplay-button', '.gif']
                if any(pattern in lower_url for pattern in invalid_patterns):
                    return False
                
                # Normalizar para alta qualidade (todas as variações de tamanho → _SL1500_)
                # Padrões comuns da Amazon:
                # ._SS100_ ._AC_US100_ ._AC_UL348_SR348,348_ ._AC_SR38,50_ ._AC_SX425_ -> ._SL1500_
                img_url = re.sub(r'\._(?:SS|AC_(?:US|UL|SL|SR|SX|SY))\d+(?:_SR\d+,\d+|,\d+)?_', '._SL1500_', img_url)
                
                # Remover sufixos .SS\d+ sem underscore
                img_url = re.sub(r'\.SS\d+_', '._SL1500_', img_url)
                
                # Verificar se já temos essa imagem (por ID)
                img_id = extract_image_id(img_url)
                if img_id in image_ids:
                    return False
                
                image_ids.add(img_id)
                images.append(img_url)
                return True
            
            # 1. Imagem principal do og:image
            og_image = html.css_first("meta[property='og:image']")
            if og_image:
                main_image = og_image.attributes.get("content", "")
                if main_image:
                    add_image(main_image)
            
            # 2. Imagens do atributo data-a-dynamic-image (mais confiável)
            dynamic_images = html.css("img.a-dynamic-image")
            for img in dynamic_images:
                # Priorizar data-old-hires (imagem grande)
                img_src = img.attributes.get("data-old-hires", "")
                if img_src:
                    add_image(img_src)
                    continue
                
                # Tentar data-a-dynamic-image (JSON com múltiplas resoluções)
                img_data = img.attributes.get("data-a-dynamic-image", "")
                if img_data and img_data.startswith("{"):
                    try:
                        img_dict = json.loads(img_data)
                        # Pegar a maior resolução (primeira chave geralmente)
                        if img_dict:
                            largest_url = max(img_dict.keys(), key=lambda k: int(img_dict[k][0]) * int(img_dict[k][1]))
                            add_image(largest_url)
                            continue
                    except:
                        pass
                
                # Fallback: src normal
                img_src = img.attributes.get("src", "")
                if img_src:
                    add_image(img_src)
            
            # 3. Imagens do carousel/thumbnails
            carousel_images = html.css("#altImages ul li img, .imageThumbnail img")
            for img in carousel_images:
                img_src = img.attributes.get("src", "")
                if img_src:
                    add_image(img_src)
            
            # 4. Buscar no JSON de scripts (fallback adicional)
            if len(images) < 5:
                scripts = html.css("script[type='text/javascript']")
                for script in scripts:
                    script_text = script.text()
                    if "'colorImages'" in script_text or '"colorImages"' in script_text:
                        try:
                            # Buscar URLs de imagens no padrão Amazon
                            image_urls = re.findall(r'https://m\.media-amazon\.com/images/I/[A-Z0-9+\-]+\._[A-Z]{2}\d+_\.jpg', script_text)
                            for img_url in image_urls:
                                if add_image(img_url):
                                    if len(images) >= 15:
                                        break
                        except Exception as e:
                            logger.warning(f"Erro ao extrair imagens do JSON: {e}")
            
            logger.info(f"Amazon: Extraídas {len(images)} imagens únicas do produto")

            # Extrair avaliação
            rating = ""
            rating_span = html.css_first("span.a-icon-alt")
            if rating_span:
                rating_text = rating_span.text().strip()
                # Extrair número (ex: "4,5 de 5 estrelas" -> "4.5")
                rating_match = re.search(r'([\d,]+)', rating_text)
                if rating_match:
                    rating = rating_match.group(1).replace(",", ".")
            
            # Número de avaliações
            reviews_count = ""
            reviews_span = html.css_first("#acrCustomerReviewText")
            if reviews_span:
                reviews_text = reviews_span.text().strip()
                # Extrair número
                reviews_match = re.search(r'([\d.]+)', reviews_text.replace(".", ""))
                if reviews_match:
                    reviews_count = reviews_match.group(1)

            # Disponibilidade
            availability = ""
            availability_span = html.css_first("#availability span")
            if availability_span:
                availability = availability_span.text().strip()

            # Categoria
            category = ""
            breadcrumb = html.css("#wayfinding-breadcrumbs_feature_div ul li a")
            if breadcrumb:
                categories = [item.text().strip() for item in breadcrumb if item.text().strip()]
                category = categories[-1] if categories else ""

            data = {
                "url": final_url,
                "source": "Amazon",
                "title": title,
                "price": price,
                "original_price": original_price,
                "discount": discount,
                "currency": "BRL",  # Assumir BRL para amazon.com.br
                "image": images[0] if images else "",  # Compatibilidade
                "images": images,  # Lista completa
                "description": description,
                "rating": rating,
                "reviews_count": reviews_count,
                "availability": availability,
                "category": category
            }
            
            logger.info(f"Amazon: Dados extraídos com sucesso - {title[:50]}...")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da Amazon: {e}")
            return {
                "url": self.url,
                "source": "Amazon",
                "title": "",
                "price": "",
                "error": str(e)
            }
