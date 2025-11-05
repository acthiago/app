import requests
from selectolax.parser import HTMLParser
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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

url = 'https://s.shopee.com.br/4LB5jw9niZ'

print('Testando Shopee...')
r = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
print(f'URL final: {r.url}')
print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get("content-type", "N/A")}')
print()

html = HTMLParser(r.text)

# Meta tags
print('=== Meta tags og: ===')
metas = html.css('meta[property^="og:"]')
print(f'Encontradas: {len(metas)}')
for meta in metas:
    prop = meta.attributes.get('property', '')
    content = meta.attributes.get('content', '')[:150]
    print(f'  {prop}: {content}')

print()
print('=== Meta tags outras: ===')
other_metas = html.css('meta[name]')
print(f'Encontradas: {len(other_metas)}')
for meta in other_metas[:10]:
    name = meta.attributes.get('name', '')
    content = meta.attributes.get('content', '')[:100]
    if content:
        print(f'  {name}: {content}')

# Buscar dados estruturados
print()
print('=== JSON-LD ===')
json_scripts = html.css('script[type="application/ld+json"]')
print(f'Scripts JSON-LD: {len(json_scripts)}')
for script in json_scripts:
    try:
        data = json.loads(script.text())
        print(f'  Tipo: {data.get("@type", "N/A")}')
        if data.get("@type") == "Product":
            print(f'  Nome: {data.get("name", "N/A")[:100]}')
            offers = data.get("offers", {})
            if offers:
                print(f'  Preço: {offers.get("price", "N/A")} {offers.get("priceCurrency", "")}')
    except:
        print(f'  JSON inválido')

# Buscar no HTML
print()
print('=== Título no HTML ===')
title_selectors = [
    'h1',
    'title',
    '[data-testid*="title"]',
    '[class*="title"]',
    '.product-name',
    '.item-name'
]
for selector in title_selectors:
    elements = html.css(selector)
    if elements:
        for elem in elements[:2]:
            text = elem.text().strip()
            if text and len(text) > 10:
                print(f'  {selector}: {text[:100]}')

print()
print('=== Buscar dados em scripts ===')
scripts = html.css('script')
found_data = False
for script in scripts:
    text = script.text()
    if 'window.__INITIAL_STATE__' in text or '"item"' in text[:500] or '"product"' in text[:500]:
        print(f'Script com dados encontrado (tamanho: {len(text)})')
        
        # Tentar extrair dados do produto
        patterns = [
            r'"name"\s*:\s*"([^"]+)"',
            r'"title"\s*:\s*"([^"]+)"',
            r'"price"\s*:\s*"?([0-9.,]+)"?',
            r'"image"\s*:\s*"([^"]+)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                print(f'  {pattern[:20]}...: {matches[:3]}')
                found_data = True
        
        if found_data:
            break

# Verificar conteúdo da página
print()
print('=== Conteúdo da página (primeiros 1000 chars) ===')
print(r.text[:1000])
print('...')

print()
print('=== Verificar se é página de erro ou redirecionamento ===')
if 'captcha' in r.text.lower():
    print('  CAPTCHA detectado!')
elif 'robot' in r.text.lower():
    print('  Detecção de robot!')
elif 'access denied' in r.text.lower():
    print('  Acesso negado!')
elif len(r.text) < 1000:
    print(f'  Página muito pequena: {len(r.text)} chars')
else:
    print(f'  Página normal: {len(r.text)} chars')