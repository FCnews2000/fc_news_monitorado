# scraping.py — coleta de manchetes por site

import requests
from bs4 import BeautifulSoup

# lista de fontes que quer monitorar
SITES = {
    "Globo":         "https://g1.globo.com/",
    "UOL":           "https://www.uol.com.br/",
    "Yahoo":         "https://www.yahoo.com/",
    "CNN Brasil":    "https://www.cnnbrasil.com.br/",
    "Terra":         "https://www.terra.com.br/",
    "Metrópoles":    "https://www.metropoles.com/",
    "Estadão":       "https://www.estadao.com.br/"
}

def get_latest_headlines():
    """
    Retorna uma lista de dicionários com as últimas manchetes de cada site:
    [
      {"titulo": "...", "fonte": "Globo",      "link": "..."},
      {"titulo": "...", "fonte": "UOL",        "link": "..."},
      ...
    ]
    """
    headlines = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for fonte, url in SITES.items():
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # tenta encontrar a primeira manchete
            # cada site tem sua estrutura; aqui damos exemplos genéricos:
            a = soup.find("a", href=True, text=True)
            if a and a.text.strip():
                link = a["href"]
                if link.startswith("/"):
                    # converte link relativo em absoluto
                    base = "/".join(url.split("/")[:3])
                    link = base + link
                headlines.append({
                    "titulo": a.text.strip(),
                    "fonte": fonte,
                    "link": link
                })
        except Exception:
            # se falhar, pula sem interromper todo o scraping
            continue

    return headlines
