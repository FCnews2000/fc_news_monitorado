# trends.py
from pytrends.request import TrendReq

def get_trends(category, 
               timeframe: str = "now 1-d", 
               geo: str = "BR"):
    """
    Puxa do Google Trends o interesse ao longo do tempo
    para o termo ou lista de termos informados.
    
    Args:
        category (str | list[str]): termo ou lista de termos a consultar.
        timeframe (str): período (ex: "now 1-d", "today 1-m").
        geo (str): código do país (ex: "BR").
    
    Returns:
        list[dict]: cada dict tem as colunas: 'date' e a(s) keyword(s).
    """
    # monta a lista de palavras-chave
    if isinstance(category, str):
        kw_list = [category]
    else:
        kw_list = list(category)

    pytrends = TrendReq(hl="pt-BR", tz=-180)
    pytrends.build_payload(kw_list, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()

    # se vier vazio ou só com isPartial, retorna lista vazia
    if df is None or df.empty:
        return []

    # remove a coluna isPartial, se existir
    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])

    # transforma o índice (data) em coluna e devolve records
    df = df.reset_index().rename(columns={"date": "timestamp"})
    return df.to_dict(orient="records")
