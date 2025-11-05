"""
Script para limpar extract_url das ofertas existentes.
Isso permite que elas sejam recadastradas com o extract_url correto.
"""
import asyncio
from app.core.database import init_db
from app.models.offer import Offer

async def clear_extract_urls():
    await init_db()
    
    # Buscar todas ofertas
    offers = await Offer.find_all().to_list()
    
    if not offers:
        print("✅ Nenhuma oferta encontrada.")
        return
    
    print(f"🔧 Encontradas {len(offers)} ofertas")
    print("⚠️  Deseja limpar o extract_url de TODAS as ofertas? (s/n): ", end="")
    
    # Para execução automática, remova o input abaixo e descomente a linha seguinte
    # resposta = "s"
    resposta = input().strip().lower()
    
    if resposta != "s":
        print("❌ Operação cancelada.")
        return
    
    cleared_count = 0
    for offer in offers:
        offer.extract_url = None
        await offer.save()
        cleared_count += 1
        print(f"🧹 Limpada: {offer.title[:50]}... (ID: {offer.id})")
    
    print(f"\n✨ Total de ofertas limpas: {cleared_count}")
    print("💡 Agora você pode recadastrar as ofertas com extract_url correto.")

if __name__ == "__main__":
    asyncio.run(clear_extract_urls())
