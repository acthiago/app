import requests
from selectolax.parser import HTMLParser
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

url = 'https://mercadolivre.com/sec/2kCwBRi'
r = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
print('URL final:', r.url)
print('Status:', r.status_code)
print()

html = HTMLParser(r.text)

# Procurar por preço no HTML
print('=== Buscando preço no HTML ===')

# Método 1: Schema.org JSON-LD
scripts = html.css('script[type="application/ld+json"]')
print(f'Scripts JSON-LD encontrados: {len(scripts)}')
for script in scripts:
    try:
        data = json.loads(script.text())
        if 'offers' in data:
            print(f'Preço (JSON-LD): {data.get("offers", {}).get("price", "N/A")}')
    except:
        pass

# Método 2: Procurar classes/atributos comuns de preço
price_selectors = [
    'span.andes-money-amount__fraction',
    'span[class*="price"]',
    'div[class*="price"]',
    'meta[itemprop="price"]',
]

for selector in price_selectors:
    elements = html.css(selector)
    if elements:
        print(f'\n{selector}: {len(elements)} encontrados')
        for elem in elements[:3]:
            text = elem.text().strip() if hasattr(elem, 'text') else ''
            attrs = dict(elem.attributes) if hasattr(elem, 'attributes') else {}
            print(f'  Texto: {text}')
            if attrs:
                print(f'  Atributos: {attrs}')

# Método 3: Procurar no texto do HTML
print('\n=== Padrões de preço no texto ===')
price_patterns = [
    r'R\$\s*[\d.,]+',
    r'"price":\s*"?[\d.,]+"?',
    r'"amount":\s*[\d.,]+',
]
for pattern in price_patterns:
    matches = re.findall(pattern, r.text)
    if matches:
        print(f'{pattern}: {matches[:5]}')
