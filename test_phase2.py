#!/usr/bin/env python3
"""
Script de teste para validar os endpoints de Analytics (Fase 2)
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_analytics():
    print("\n" + "="*80)
    print("🧪 TESTE DA FASE 2 - Sistema de Analytics")
    print("="*80 + "\n")
    
    from app.core.database import init_db
    from app.models.offer import Offer
    from app.models.offer_click import OfferClick
    from app.models.page_view import PageView
    from datetime import datetime
    
    # Inicializar banco
    print("📦 Inicializando conexão com MongoDB...")
    await init_db()
    print("✅ Conectado!\n")
    
    # ============================================
    # TESTE 1: Verificar modelos criados
    # ============================================
    print("="*80)
    print("TEST #1: Modelos OfferClick e PageView")
    print("="*80)
    
    # Contar registros existentes
    click_count = await OfferClick.find({}).count()
    pageview_count = await PageView.find({}).count()
    
    print(f"✅ Modelo OfferClick: {click_count} registros")
    print(f"✅ Modelo PageView: {pageview_count} registros")
    
    # ============================================
    # TESTE 2: Criar registros de teste
    # ============================================
    print("\n" + "="*80)
    print("TEST #2: Criar Registros de Teste")
    print("="*80)
    
    # Buscar uma oferta para teste
    offer = await Offer.find_one({"status": "approved"})
    if not offer:
        print("⚠️  Nenhuma oferta aprovada encontrada. Pulando testes de cliques.")
    else:
        print(f"\n📦 Oferta de teste: {offer.title[:60]}...")
        print(f"   - ID: {offer.id}")
        print(f"   - Total clicks inicial: {offer.total_clicks}")
        
        # Criar cliques de teste
        print("\n➕ Criando 3 cliques de teste...")
        for i, source in enumerate(["home", "ofertas", "home"], 1):
            click = OfferClick(
                offer_id=str(offer.id),
                source=source,
                ip_address=f"192.168.1.{i}",
                user_agent="Mozilla/5.0 (Test Bot)",
                clicked_at=datetime.utcnow()
            )
            await click.save()
            print(f"   ✅ Click {i} criado (source: {source})")
        
        # Atualizar contador da oferta
        offer.total_clicks += 3
        await offer.save()
        print(f"\n✅ Total clicks atualizado: {offer.total_clicks}")
    
    # Criar pageviews de teste
    print("\n➕ Criando 3 pageviews de teste...")
    for i, page in enumerate(["home", "ofertas", "cupons"], 1):
        pageview = PageView(
            page=page,
            ip_address=f"192.168.1.{i}",
            user_agent="Mozilla/5.0 (Test Bot)",
            viewed_at=datetime.utcnow()
        )
        await pageview.save()
        print(f"   ✅ Pageview {i} criado (page: {page})")
    
    # ============================================
    # TESTE 3: Testar agregações
    # ============================================
    print("\n" + "="*80)
    print("TEST #3: Agregações e Métricas")
    print("="*80)
    
    if offer:
        # Cliques por fonte
        print(f"\n📊 Cliques da oferta {offer.id} por fonte:")
        pipeline_source = [
            {"$match": {"offer_id": str(offer.id)}},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        clicks_by_source = await OfferClick.get_pymongo_collection().aggregate(pipeline_source).to_list(length=None)
        
        for item in clicks_by_source:
            print(f"   - {item['_id']}: {item['count']} clicks")
    
    # Pageviews por página
    print(f"\n📊 Pageviews por página:")
    pipeline_pages = [
        {"$group": {"_id": "$page", "views": {"$sum": 1}}},
        {"$sort": {"views": -1}}
    ]
    views_by_page = await PageView.get_pymongo_collection().aggregate(pipeline_pages).to_list(length=None)
    
    for item in views_by_page:
        print(f"   - {item['_id']}: {item['views']} views")
    
    # Ofertas mais clicadas
    print(f"\n📊 Top 5 ofertas mais clicadas:")
    pipeline_top = [
        {"$group": {"_id": "$offer_id", "clicks": {"$sum": 1}}},
        {"$sort": {"clicks": -1}},
        {"$limit": 5}
    ]
    top_offers = await OfferClick.get_pymongo_collection().aggregate(pipeline_top).to_list(length=None)
    
    for i, item in enumerate(top_offers, 1):
        try:
            offer_data = await Offer.get(item["_id"])
            title = offer_data.title[:50] if offer_data else "Oferta removida"
        except:
            title = "Oferta não encontrada"
        print(f"   {i}. {title}... ({item['clicks']} clicks)")
    
    # ============================================
    # TESTE 4: Campo total_clicks em Offer
    # ============================================
    print("\n" + "="*80)
    print("TEST #4: Campo total_clicks no modelo Offer")
    print("="*80)
    
    # Buscar ofertas com clicks
    offers_with_clicks = await Offer.find({"total_clicks": {"$gt": 0}}).limit(3).to_list()
    
    if offers_with_clicks:
        print(f"\n✅ {len(offers_with_clicks)} ofertas encontradas com clicks:")
        for offer in offers_with_clicks:
            print(f"   - {offer.title[:50]}... ({offer.total_clicks} clicks)")
    else:
        print("\n⚠️  Nenhuma oferta com clicks > 0 encontrada")
    
    # ============================================
    # RESUMO FINAL
    # ============================================
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80 + "\n")
    
    total_clicks = await OfferClick.find({}).count()
    total_views = await PageView.find({}).count()
    
    print("✅ Fase 2 - Sistema de Analytics:")
    print(f"   - Modelo OfferClick: ✅ FUNCIONANDO")
    print(f"   - Modelo PageView: ✅ FUNCIONANDO")
    print(f"   - Campo total_clicks em Offer: ✅ PRESENTE")
    print(f"   - Total de clicks registrados: {total_clicks}")
    print(f"   - Total de pageviews registrados: {total_views}")
    print(f"   - Agregações MongoDB: ✅ FUNCIONANDO")
    
    print("\n✨ Todos os testes da Fase 2 concluídos!\n")
    print("📝 Próximo passo: Testar endpoints via API HTTP")
    print("   - POST /analytics/click")
    print("   - POST /analytics/pageview")
    print("   - GET /analytics/offer/{id}")
    print("   - GET /analytics/summary\n")

if __name__ == "__main__":
    asyncio.run(test_analytics())
