#!/usr/bin/env python3
"""
Teste rápido de extração do Mercado Livre
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.offer_extractor.factory import get_extractor
import json

def test_url(url: str):
    """Testa extração de uma URL"""
    print(f"\n{'='*80}")
    print(f"🔍 Testando URL: {url}")
    print(f"{'='*80}\n")
    
    try:
        extractor = get_extractor(url)
        print(f"✅ Extrator detectado: {extractor.__class__.__name__}\n")
        
        print("⏳ Extraindo dados...")
        data = extractor.extract()
        
        print(f"\n{'='*80}")
        print("📦 RESULTADO:")
        print(f"{'='*80}\n")
        
        print(f"🏷️  Título: {data.get('title', 'N/A')}")
        print(f"💰 Preço: R$ {data.get('price', 'N/A')}")
        
        if data.get('original_price'):
            print(f"💸 Preço Original: R$ {data.get('original_price')}")
        
        if data.get('discount'):
            print(f"🎯 Desconto: {data.get('discount')}")
        
        if data.get('rating'):
            print(f"⭐ Avaliação: {data.get('rating')}")
        
        print(f"\n📝 Descrição: {data.get('description', 'N/A')[:150]}...")
        
        images = data.get('images', [])
        print(f"\n🖼️  Imagens: {len(images)} encontradas")
        
        print(f"\n🔗 URL: {data.get('url')}")
        print(f"🏪 Fonte: {data.get('source')}")
        
        if data.get('error'):
            print(f"\n❌ ERRO: {data.get('error')}")
        
        print(f"\n{'='*80}")
        print("📄 JSON COMPLETO:")
        print(f"{'='*80}\n")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        return data
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    url = "https://mercadolivre.com/sec/1JDfeRp"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    print("\n🧪 TESTE DE EXTRAÇÃO - MERCADO LIVRE")
    result = test_url(url)
    
    if result and not result.get('error'):
        print("\n✅ Extração bem-sucedida!\n")
    else:
        print("\n❌ Falha na extração\n")
