# trends.py
from pytrends.request import TrendReq

def get_trends(categoria=None):
    """
    Busca os top 10 termos em alta no Google Trends (Brasil).
    Se for passada uma categoria, poderia filtrar por palavra-chave,
    mas aqui só retornamos o geral.
    """
    pytrends = TrendReq(hl='pt-BR', tz=-180)
    # trending_searches devuelve Series; pegamos os 10 primeiros
    data = pytrends.trending_searches(pn='brazil')
    return data.head(10).tolist()
