from app.services.offer_extractor.factory import get_extractor
import json

url = "https://s.shopee.com.br/4LB5jw9niZ"
print(f"Testando: {url}")

try:
    extractor = get_extractor(url)
    result = extractor.extract()
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Erro: {e}")