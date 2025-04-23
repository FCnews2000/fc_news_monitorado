# monitorizacao_noticias.py
import requests
import json
import os
import sys
import time
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

class MonitorizacaoNoticias:
    def __init__(self, config_file=None):
        """
        Inicializa o sistema de monitorização de notícias

        Args:
            config_file (str): Caminho para o arquivo de configuração (opcional)
        """
        # Fontes agrupadas por tema
        self.fontes_noticias = {
            "gerais": [
                "https://globo.com",
                "https://uol.com.br",
                "https://yahoo.com",
                "https://cnnbrasil.com.br",
                "https://terra.com.br",
                "https://metropoles.com",
                "https://estadao.com.br"
            ],
            "economia": [
                "https://economia.uol.com.br",
                "https://economia.estadao.com.br",
                "https://exame.com"
            ],
            "politica": [
                "https://politica.estadao.com.br",
                "https://veja.abril.com.br/politica",
                "https://epoca.globo.com/politica"
            ],
            "esportes": [
                "https://ge.globo.com",
                "https://uol.com.br/esporte",
                "https://espn.com.br"
            ]
        }

        # Horários para agrupamento de posts
        self.horarios_posts = {
            "manha":   {"inicio": "00:00", "fim": "06:00", "post": "06:00"},
            "tarde":   {"inicio": "06:00", "fim": "12:00", "post": "12:00"},
            "noite":   {"inicio": "12:00", "fim": "18:00", "post": "18:00"},
            "madrugada":{"inicio": "18:00", "fim": "23:59", "post": "00:00"}
        }

        # Onde salvamos CSVs/JSONs
        self.diretorio_dados = os.path.join(os.path.dirname(__file__), "dados")
        os.makedirs(self.diretorio_dados, exist_ok=True)

        self.noticias_coletadas = []
        self.noticias_selecionadas = []

        # Se passou um config JSON, carrega
        if config_file and os.path.exists(config_file):
            self._carregar_configuracao(config_file)

    def _carregar_configuracao(self, config_file):
        """Carrega fontes/horários de um JSON externo."""
        with open(config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        if "fontes_noticias" in cfg:
            self.fontes_noticias = cfg["fontes_noticias"]
        if "horarios_posts" in cfg:
            self.horarios_posts = cfg["horarios_posts"]

    def _obter_periodo_atual(self):
        """Determina em qual janela de horário estamos."""
        agora = datetime.now().time()
        for nome, info in self.horarios_posts.items():
            inicio = datetime.strptime(info["inicio"], "%H:%M").time()
            fim    = datetime.strptime(info["fim"], "%H:%M").time()
            if inicio <= agora <= fim:
                return nome, info
        return "indefinido", {}

    def coletar_noticias(self, categoria=None):
        """
        Coleta manchetes de todas as fontes (ou de uma categoria).
        Retorna lista de dicts: {titulo, fonte, categoria, link, data_coleta}
        """
        resultados = []
        categorias = [categoria] if categoria else self.fontes_noticias.keys()

        for cat in categorias:
            for url in self.fontes_noticias.get(cat, []):
                try:
                    resp = requests.get(url, timeout=10, headers={
                        "User-Agent": "Mozilla/5.0"
                    })
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "html.parser")

                    # Exemplo: procura <a class="feed-post-link">
                    elems = soup.find_all("a", class_="feed-post-link") or \
                            soup.find_all(["h1","h2","h3"])
                    for e in elems[:5]:
                        texto = e.get_text(strip=True)
                        if not texto or len(texto)<20:
                            continue
                        link = e.get("href")
                        if link and link.startswith("/"):
                            base = "/".join(url.split("/")[:3])
                            link = base + link
                        resultados.append({
                            "titulo": texto,
                            "fonte": url,
                            "categoria": cat,
                            "link": link,
                            "data_coleta": datetime.now().isoformat()
                        })
                except Exception as e:
                    print(f"[!] Erro ao coletar {url}: {e}")

        self.noticias_coletadas = resultados
        self._salvar_noticias_coletadas()
        return resultados

    def _salvar_noticias_coletadas(self):
        """Grava CSV com tudo o que foi coletado."""
        if not self.noticias_coletadas: return
        nome = datetime.now().strftime("noticias_%Y%m%d_%H%M%S.csv")
        caminho = os.path.join(self.diretorio_dados, nome)
        pd.DataFrame(self.noticias_coletadas).to_csv(caminho, index=False, encoding="utf-8-sig")
        print(f"[+] Salvou CSV em {caminho}")

    def selecionar_noticia_relevante(self):
        """Retorna a primeira notícia (pode evoluir para algo mais sofisticado)."""
        if not self.noticias_coletadas:
            return None
        sel = self.noticias_coletadas[0]
        self.noticias_selecionadas.append(sel)
        return sel

    def gerar_perspectivas(self, noticia):
        """
        Insere dois campos no dict:
          - perspectiva_capetinha
          - perspectiva_anjinho
        """
        if not noticia:
            return None
        t = noticia["titulo"]
        noticia["perspectiva_capetinha"] = f"😈 Crítica: {t}..."
        noticia["perspectiva_anjinho"]   = f"😇 Positiva: {t}..."
        return noticia

    def _salvar_noticia_processada(self, noticia, periodo):
        """Grava JSON da notícia final."""
        nome = datetime.now().strftime(f"noticia_{periodo}_%Y%m%d_%H%M%S.json")
        caminho = os.path.join(self.diretorio_dados, nome)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(noticia, f, ensure_ascii=False, indent=2)
        print(f"[+] Salvou JSON em {caminho}")

    def executar_ciclo_monitorizacao(self):
        """Coleta → seleciona → gera perspectivas → grava JSON → retorna o dict."""
        periodo, info = self._obter_periodo_atual()
        print(f"[+] Período: {periodo}")
        self.coletar_noticias()
        ni = self.selecionar_noticia_relevante()
        if not ni:
            return None
        ni = self.gerar_perspectivas(ni)
        self._salvar_noticia_processada(ni, periodo)
        return ni

    def executar_monitorizacao_continua(self, interval_min=30):
        """Roda em loop, aguardando `interval_min` minutos entre ciclos."""
        try:
            while True:
                print("\n----- Novo ciclo:", datetime.now(), "-----")
                self.executar_ciclo_monitorizacao()
                time.sleep(interval_min * 60)
        except KeyboardInterrupt:
            print("[!] Monitorização interrompida")

if __name__ == "__main__":
    # Uso:
    #   python monitorizacao_noticias.py [config.json] [continuo] [intervalo_minutos]
    cfg = sys.argv[1] if len(sys.argv)>1 else None
    modo = sys.argv[2] if len(sys.argv)>2 else None
    intervalo = int(sys.argv[3]) if len(sys.argv)>3 else 30

    monitor = MonitorizacaoNoticias(config_file=cfg)
    if modo == "continuo":
        monitor.executar_monitorizacao_continua(intervalo)
    else:
        resultado = monitor.executar_ciclo_monitorizacao()
        print("Resultado final:", resultado)
