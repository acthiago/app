import asyncio
from app.services.offer_extractor.factory import get_extractor

async def test_kabum():
    # Link fornecido pelo usuário
    url = "https://tidd.ly/4ozNo1J"
    
    print(f"\n🔍 Testando extração da Kabum...")
    print(f"📎 URL: {url}\n")
    
    try:
        extractor = get_extractor(url)
        print(f"✅ Extrator identificado: {extractor.__class__.__name__}")
        
        data = extractor.extract()
        
        print("\n📦 Dados extraídos:")
        print("=" * 80)
        print(f"🏪 Loja: {data.get('source')}")
        print(f"🔗 URL Final: {data.get('url')}")
        print(f"📝 Título: {data.get('title')}")
        print(f"💰 Preço: R$ {data.get('price')}")
        print(f"💸 Preço Original: R$ {data.get('original_price')}")
        print(f"🏷️ Desconto: {data.get('discount')}")
        print(f"💳 Parcelamento: {data.get('installments')}")
        print(f"📷 Imagens: {len(data.get('images', []))} imagens")
        print(f"⭐ Avaliação: {data.get('rating')}")
        print(f"💬 Avaliações: {data.get('reviews_count')}")
        print(f"📦 Disponibilidade: {data.get('availability')}")
        print(f"🗂️ Categoria: {data.get('category')}")
        print(f"🏷️ Marca: {data.get('brand')}")
        print(f"🆔 SKU: {data.get('sku')}")
        print(f"📄 Descrição: {data.get('description')[:100]}..." if data.get('description') else "📄 Descrição: N/A")
        
        if data.get('images'):
            print(f"\n🖼️ URLs das Imagens:")
            for i, img in enumerate(data['images'], 1):
                # Mostrar apenas nome do arquivo
                filename = img.split('/')[-1]
                print(f"  {i}. {filename}")
        
        print("\n" + "=" * 80)
        
        if data.get('error'):
            print(f"❌ Erro: {data['error']}")
        else:
            print("✅ Extração concluída com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao processar: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kabum())
