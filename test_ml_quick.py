from app.services.offer_extractor.factory import get_extractor
import json

url = "https://mercadolivre.com/sec/2kCwBRi"
extractor = get_extractor(url)
result = extractor.extract()

print(json.dumps(result, indent=2, ensure_ascii=False))
