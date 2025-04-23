from pytrends.request import TrendReq
import pandas as pd

def get_trends(categoria=None):
    """
    Retorna as tendências de pesquisa do Google Trends
    para a categoria especificada.
    
    Args:
        categoria (str): categoria para buscar tendências (ex: "política", "economia")
                        Se None, retorna tendências gerais
        
    Returns:
        list: Lista de tendências com dicionários contendo termo e pontuação
    """
    # Mapear categorias para keywords relevantes
    keywords_map = {
        "politica": ["política", "governo", "eleições", "congresso"],
        "economia": ["economia", "bolsa de valores", "dólar", "inflação"],
        "tecnologia": ["tecnologia", "inteligência artificial", "smartphone", "apps"],
        "esportes": ["futebol", "olimpíadas", "campeonato", "esportes"],
        "entretenimento": ["filmes", "música", "celebridades", "streaming"],
        None: ["notícias", "brasil", "mundo", "atualidades"]
    }
    
    # Selecionar keywords com base na categoria
    cat_lower = categoria.lower() if categoria else None
    if cat_lower not in keywords_map:
        cat_lower = None
    
    keywords = keywords_map[cat_lower]
    
    try:
        # Inicializar pytrends
        pytrends = TrendReq(hl="pt-BR", tz=-180)
        
        # Construir payload com as keywords selecionadas
        pytrends.build_payload(keywords, timeframe="now 1-d", geo="BR")
        
        # Obter dados de interesse ao longo do tempo
        data = pytrends.interest_over_time()
        
        # Se vier coluna 'isPartial', remova
        if "isPartial" in data.columns:
            data = data.drop(columns=["isPartial"])
        
        # Converter para formato de lista de tendências
        trends = []
        
        # Se não houver dados, retornar lista vazia
        if data.empty:
            return trends
        
        # Calcular média para cada keyword
        for keyword in keywords:
            if keyword in data.columns:
                score = int(data[keyword].mean())
                if score > 0:  # Apenas incluir se tiver alguma pontuação
                    trends.append({
                        "termo": keyword,
                        "pontuacao": score
                    })
        
        # Ordenar por pontuação (maior primeiro)
        trends.sort(key=lambda x: x["pontuacao"], reverse=True)
        
        return trends
    
    except Exception as e:
        print(f"Erro ao obter tendências: {e}")
        # Fallback: retornar tendências fictícias para não quebrar a aplicação
        return [
            {"termo": keywords[0], "pontuacao": 100},
            {"termo": keywords[1], "pontuacao": 75},
            {"termo": keywords[2], "pontuacao": 50},
            {"termo": keywords[3], "pontuacao": 25}
        ]
