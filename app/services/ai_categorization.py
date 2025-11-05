"""
Serviço de categorização automática com IA
"""
import os
from typing import Optional, List
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Categorias disponíveis
CATEGORIES = [
    "Eletrônicos",
    "Celulares e Telefonia",
    "Computadores e Informática",
    "Games e Consoles",
    "Casa e Eletrodomésticos",
    "Esportes e Fitness",
    "Moda e Beleza",
    "Livros e Papelaria",
    "Brinquedos e Hobbies",
    "Automotivo",
    "Alimentos e Bebidas",
    "Saúde e Cuidados Pessoais",
    "Ferramentas e Construção",
    "Jardim e Piscina",
    "Pet Shop",
    "Outros"
]

def init_ai():
    """Inicializa cliente OpenAI"""
    global client
    if OPENAI_API_KEY:
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI configurada")
    else:
        print("⚠️  OPENAI_API_KEY não configurada. Categorização automática desabilitada.")


async def categorize_offer(title: str, description: Optional[str] = None) -> str:
    """
    Categoriza uma oferta automaticamente usando IA
    
    Args:
        title: Título da oferta
        description: Descrição da oferta (opcional)
    
    Returns:
        Categoria sugerida
    """
    if not client:
        return "Outros"
    
    try:
        # Construir prompt
        text = f"Título: {title}"
        if description:
            text += f"\nDescrição: {description}"
        
        prompt = f"""Você é um sistema de categorização de produtos. Analise o produto abaixo e escolha UMA categoria mais apropriada da lista.

{text}

Categorias disponíveis:
{', '.join(CATEGORIES)}

Responda APENAS com o nome exato da categoria, sem explicações."""

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em categorizar produtos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        category = response.choices[0].message.content.strip()
        
        # Validar se a categoria está na lista
        if category in CATEGORIES:
            return category
        
        # Tentar encontrar categoria similar
        for cat in CATEGORIES:
            if cat.lower() in category.lower() or category.lower() in cat.lower():
                return cat
        
        return "Outros"
        
    except Exception as e:
        print(f"Erro na categorização com IA: {e}")
        return "Outros"


def categorize_by_keywords(title: str) -> str:
    """
    Categorização simples baseada em palavras-chave (fallback quando IA não está disponível)
    """
    title_lower = title.lower()
    
    keywords_map = {
        "Celulares e Telefonia": ["celular", "smartphone", "iphone", "samsung galaxy", "telefone", "fone"],
        "Computadores e Informática": ["notebook", "computador", "pc", "teclado", "mouse", "monitor", "ssd", "hd"],
        "Games e Consoles": ["playstation", "xbox", "nintendo", "ps5", "ps4", "console", "jogo", "game"],
        "Casa e Eletrodomésticos": ["geladeira", "fogão", "microondas", "ar condicionado", "ventilador", "tv", "televisão"],
        "Moda e Beleza": ["roupa", "camisa", "calça", "vestido", "sapato", "tênis", "perfume", "maquiagem"],
        "Esportes e Fitness": ["bicicleta", "esteira", "musculação", "bola", "raquete", "fitness"],
        "Livros e Papelaria": ["livro", "caderno", "caneta", "papel"],
        "Brinquedos e Hobbies": ["brinquedo", "boneca", "carrinho", "lego"],
        "Automotivo": ["carro", "moto", "pneu", "óleo", "bateria"],
        "Pet Shop": ["pet", "cachorro", "gato", "ração", "animal"],
        "Ferramentas e Construção": ["furadeira", "parafusadeira", "martelo", "serra", "ferramenta"],
    }
    
    for category, keywords in keywords_map.items():
        if any(keyword in title_lower for keyword in keywords):
            return category
    
    return "Outros"


async def generate_tags(title: str, description: Optional[str] = None, category: Optional[str] = None) -> List[str]:
    """
    Gera tags relevantes para uma oferta usando IA
    
    Args:
        title: Título da oferta
        description: Descrição da oferta (opcional)
        category: Categoria da oferta (opcional)
    
    Returns:
        Lista de tags (máximo 5)
    """
    if not client:
        return generate_tags_by_keywords(title)
    
    try:
        # Construir contexto
        text = f"Título: {title}"
        if description:
            text += f"\nDescrição: {description}"
        if category:
            text += f"\nCategoria: {category}"
        
        prompt = f"""Você é um sistema de geração de tags para produtos. Analise o produto abaixo e gere de 3 a 5 tags relevantes.

{text}

Gere tags que sejam:
- Palavras-chave descritivas do produto
- Características importantes (marca, modelo, especificações)
- Termos que usuários podem buscar
- Curtas e objetivas (1-3 palavras cada)

Responda APENAS com as tags separadas por vírgula, sem numeração ou explicações.
Exemplo: smartphone, 5g, samsung, 128gb, android"""

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em gerar tags para produtos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=100
        )
        
        tags_text = response.choices[0].message.content.strip()
        
        # Processar tags
        tags = [tag.strip().lower() for tag in tags_text.split(',')]
        
        # Limitar a 5 tags e remover vazias
        tags = [tag for tag in tags if tag and len(tag) > 1][:5]
        
        return tags
        
    except Exception as e:
        print(f"Erro na geração de tags com IA: {e}")
        return generate_tags_by_keywords(title)


def generate_tags_by_keywords(title: str) -> List[str]:
    """
    Geração simples de tags baseada em palavras-chave (fallback)
    """
    # Palavras comuns a ignorar
    stop_words = {
        'de', 'da', 'do', 'com', 'para', 'em', 'a', 'o', 'e', 'ou', 
        'kit', 'c/', 'pc', 'un', 'cx', 'cor', 'cm', 'mm', 'kg', 'g'
    }
    
    # Extrair palavras do título
    words = title.lower().split()
    
    # Filtrar palavras relevantes
    tags = []
    for word in words:
        # Remover pontuação
        word = ''.join(c for c in word if c.isalnum() or c in ['-', '_'])
        
        # Adicionar se for relevante
        if (len(word) > 2 and 
            word not in stop_words and 
            not word.isdigit()):
            tags.append(word)
    
    # Limitar a 5 tags únicas
    return list(dict.fromkeys(tags))[:5]
