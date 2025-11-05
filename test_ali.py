import requests
from selectolax.parser import HTMLParser
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

url = 'https://pt.aliexpress.com/item/1005009256294309.html?aff_fcid=aa36b20ce60f4376818eefa70ccc1d15-1761585292767-01653-_c3F69NvN&tt=CPS_NORMAL&aff_fsk=_c3F69NvN&aff_platform=shareComponent-detail&sk=_c3F69NvN&aff_trace_key=aa36b20ce60f4376818eefa70ccc1d15-1761585292767-01653-_c3F69NvN&terminal_id=51b8bf72e95a430ab175c6a25d562d7f&afSmartRedirect=y&gatewayAdapt=glo2bra'

print('Buscando URL...')
r = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
print(f'URL final: {r.url[:100]}...')
print(f'Status: {r.status_code}')
print()

html = HTMLParser(r.text)

# Meta tags
print('=== Meta tags og: ===')
metas = html.css('meta[property^="og:"]')
print(f'Encontradas: {len(metas)}')
for meta in metas[:5]:
    prop = meta.attributes.get('property', '')
    content = meta.attributes.get('content', '')[:100]
    print(f'  {prop}: {content}')

print()
print('=== Meta tags product: ===')
metas_product = html.css('meta[property^="product:"]')
print(f'Encontradas: {len(metas_product)}')
for meta in metas_product[:5]:
    prop = meta.attributes.get('property', '')
    content = meta.attributes.get('content', '')[:100]
    print(f'  {prop}: {content}')

# Buscar JSON com dados do produto
print()
print('=== Buscando preço em diferentes formas ===')

# Método 1: Buscar em script com window.runParams ou data
scripts = html.css('script')
for idx, script in enumerate(scripts):
    text = script.text()
    if '"minActivityAmount"' in text or '"formattedPrice"' in text or '"actMinValue"' in text:
        print(f'\n--- Script {idx} com dados de preço ---')
        # Buscar padrões de preço
        price_patterns = [
            r'"formattedPrice"\s*:\s*"([^"]+)"',
            r'"actMinValue"\s*:\s*"([^"]+)"',
            r'"minActivityAmount"\s*:\s*{[^}]*"value"\s*:\s*"([^"]+)"',
            r'"discountPrice"\s*:\s*"([^"]+)"',
        ]
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                print(f'  Padrão {pattern[:30]}: {matches[:3]}')
        
        if idx < 3:  # Mostrar apenas primeiros 3 scripts
            print(f'  Trecho: {text[:500]}')

# Método 2: Tentar extrair de window.runParams completo
print('\n=== Procurando window.runParams mais completo ===')
for script in scripts:
    text = script.text()
    if 'window.runParams' in text and len(text) > 1000:
        # Extrair tudo entre window.runParams = { até };
        match = re.search(r'window\.runParams\s*=\s*({[^;]+});', text, re.DOTALL)
        if match:
            json_str = match.group(1)
            print(f'Tamanho do JSON: {len(json_str)} chars')
            try:
                data = json.loads(json_str)
                print(f'Keys no runParams: {list(data.keys())[:10]}')
                if 'data' in data:
                    print(f'Keys em data: {list(data.get("data", {}).keys())[:10]}')
            except Exception as e:
                print(f'Erro ao parsear: {e}')
        break
