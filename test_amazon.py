#!/usr/bin/env python3
"""
Script de teste para o extrator da Amazon
Testa tanto URLs completas quanto links encurtados (amzn.to)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.offer_extractor.amazon import AmazonExtractor
import json

def test_amazon_url(url: str):
    """Testa extração de uma URL da Amazon"""
    print(f"\n{'='*80}")
    print(f"🔍 Testando URL: {url}")
    print(f"{'='*80}\n")
    
    try:
        extractor = AmazonExtractor(url)
        
        # 1. Resolver URL (importante para amzn.to)
        print("1️⃣ Resolvendo URL...")
        resolved_url = extractor.resolve_url()
        print(f"   ✅ URL resolvida: {resolved_url}\n")
        
        # 2. Extrair dados
        print("2️⃣ Extraindo dados do produto...")
        data = extractor.extract()
        
        # 3. Exibir resultados
        print(f"\n{'='*80}")
        print("📦 DADOS EXTRAÍDOS:")
        print(f"{'='*80}\n")
        
        print(f"🏷️  Título: {data.get('title', 'N/A')}")
        print(f"💰 Preço: R$ {data.get('price', 'N/A')}")
        
        if data.get('original_price'):
            print(f"💸 Preço Original: R$ {data.get('original_price')}")
        
        if data.get('discount'):
            print(f"🎯 Desconto: {data.get('discount')}")
        
        if data.get('rating'):
            print(f"⭐ Avaliação: {data.get('rating')} estrelas")
        
        if data.get('reviews_count'):
            print(f"💬 Avaliações: {data.get('reviews_count')}")
        
        if data.get('availability'):
            print(f"📦 Disponibilidade: {data.get('availability')}")
        
        if data.get('category'):
            print(f"📂 Categoria: {data.get('category')}")
        
        print(f"\n📝 Descrição: {data.get('description', 'N/A')[:200]}...")
        
        # Imagens
        images = data.get('images', [])
        print(f"\n🖼️  Imagens encontradas: {len(images)}")
        for i, img in enumerate(images[:3], 1):
            print(f"   {i}. {img[:80]}...")
        if len(images) > 3:
            print(f"   ... e mais {len(images) - 3} imagens")
        
        print(f"\n🔗 URL Final: {data.get('url')}")
        print(f"🏪 Fonte: {data.get('source')}")
        
        # JSON completo
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
    # URLs de teste
    test_urls = [
        # Link encurtado (amzn.to)
        "https://amzn.to/4o1gJBf",
        
        # URLs completas da Amazon (exemplos)
        # "https://www.amazon.com.br/dp/B0XXXXXXXXX",
    ]
    
    # Se passou URL via argumento, usar ela
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    print("\n" + "="*80)
    print("🧪 TESTE DO EXTRATOR DA AMAZON")
    print("="*80)
    
    results = []
    for url in test_urls:
        result = test_amazon_url(url)
        results.append(result)
    
    # Resumo final
    print(f"\n\n{'='*80}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*80}\n")
    
    success_count = sum(1 for r in results if r and not r.get('error'))
    print(f"✅ Sucessos: {success_count}/{len(results)}")
    print(f"❌ Falhas: {len(results) - success_count}/{len(results)}")
    
    print("\n✨ Teste concluído!\n")
