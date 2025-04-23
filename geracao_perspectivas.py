import os
import random
import requests

class GeracaoPerspectivas:
    def __init__(self, api_key=None):
        """
        Inicializa o sistema de geração de perspectivas usando IA
        
        Args:
            api_key (str): Chave de API para serviço de IA (opcional)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
    
    def gerar_perspectivas_com_ia(self, noticia):
        """
        Gera perspectivas usando IA para uma notícia
        
        Args:
            noticia (dict): Notícia para gerar perspectivas
        
        Returns:
            dict: Notícia com perspectivas adicionadas
        """
        if not noticia:
            return None
        
        titulo = noticia.get('titulo', '')
        categoria = noticia.get('categoria', 'geral')
        
        # Instruções para o modelo de IA
        prompt_capetinha = f"""
        Gere uma perspectiva crítica e cética (estilo "capetinha") sobre a seguinte notícia:
        Título: {titulo}
        Categoria: {categoria}
        
        A perspectiva deve ser crítica, destacando possíveis problemas, consequências negativas ou 
        motivações questionáveis. Use tom cético mas mantenha-se factual. Máximo 3 frases, total de 280 caracteres.
        """
        
        prompt_anjinho = f"""
        Gere uma perspectiva otimista e favorável (estilo "anjinho") sobre a seguinte notícia:
        Título: {titulo}
        Categoria: {categoria}
        
        A perspectiva deve ser positiva, destacando benefícios potenciais, intenções nobres ou 
        consequências favoráveis. Use tom otimista mas mantenha-se factual. Máximo 3 frases, total de 280 caracteres.
        """
        
        # Se tiver API key configurada, usar serviço de IA
        if self.api_key:
            try:
                # Implementar chamada à API de IA aqui
                # Exemplo com OpenAI (ajustar conforme necessário)
                perspectiva_capetinha = self._chamar_api_ia(prompt_capetinha)
                perspectiva_anjinho = self._chamar_api_ia(prompt_anjinho)
            except Exception as e:
                print(f"Erro ao chamar API de IA: {e}")
                # Fallback para geração manual
                perspectiva_capetinha, perspectiva_anjinho = self._gerar_perspectivas_manuais(titulo, categoria)
        else:
            # Sem API key, usar geração manual
            perspectiva_capetinha, perspectiva_anjinho = self._gerar_perspectivas_manuais(titulo, categoria)
        
        # Adicionar perspectivas à notícia
        noticia['perspectiva_capetinha'] = perspectiva_capetinha
        noticia['perspectiva_anjinho'] = perspectiva_anjinho
        
        return noticia
    
    def _chamar_api_ia(self, prompt):
        """
        Chama API de IA para gerar texto
        
        Args:
            prompt (str): Prompt para a IA
        
        Returns:
            str: Texto gerado
        """
        # Implementação de exemplo para OpenAI
        # Ajustar conforme o serviço de IA utilizado
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                print(f"Erro na API: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"Erro ao chamar API: {e}")
            return None
    
    def _gerar_perspectivas_manuais(self, titulo, categoria):
        """
        Gera perspectivas manualmente baseadas em templates
        
        Args:
            titulo (str): Título da notícia
            categoria (str): Categoria da notícia
        
        Returns:
            tuple: (perspectiva_capetinha, perspectiva_anjinho)
        """
        # Templates por categoria
        templates = {
            "economia": {
                "capetinha": [
                    "Mais uma medida que beneficia apenas o grande capital, ignorando as necessidades reais da população.",
                    "Os números escondem a realidade: enquanto poucos comemoram, a maioria continua a sofrer com as consequências.",
                    "Decisão claramente influenciada por lobbies poderosos, sem considerar o impacto a longo prazo."
                ],
                "anjinho": [
                    "Uma iniciativa que promete trazer benefícios para toda a economia, gerando empregos e oportunidades.",
                    "Finalmente uma medida que olha para o futuro, com potencial para melhorar a vida de milhões de pessoas.",
                    "Os resultados positivos já começam a aparecer, mostrando que estamos no caminho certo."
                ]
            },
            "politica": {
                "capetinha": [
                    "Mais uma manobra política para desviar a atenção dos problemas reais que afetam o país.",
                    "Por trás do discurso bonito, esconde-se a mesma velha política de sempre.",
                    "Decisão que beneficia apenas um pequeno grupo, enquanto a maioria continua desassistida."
                ],
                "anjinho": [
                    "Um passo importante para fortalecer nossas instituições democráticas e garantir um futuro melhor.",
                    "Iniciativa que demonstra compromisso real com as necessidades da população.",
                    "Medida que finalmente coloca o país no rumo certo, após anos de políticas equivocadas."
                ]
            },
            "tecnologia": {
                "capetinha": [
                    "Mais uma tecnologia que promete revolucionar, mas que na prática aumentará desigualdades.",
                    "Por trás da inovação, esconde-se o risco de perda de privacidade e controle sobre nossas vidas.",
                    "Avanço que beneficiará principalmente grandes corporações, não o cidadão comum."
                ],
                "anjinho": [
                    "Uma inovação que tem potencial para melhorar significativamente a qualidade de vida das pessoas.",
                    "Tecnologia que democratiza o acesso a serviços essenciais, reduzindo desigualdades.",
                    "Avanço que coloca o país na vanguarda global, gerando oportunidades para todos."
                ]
            },
            "geral": {
                "capetinha": [
                    "A realidade por trás desta notícia é bem menos otimista do que parece à primeira vista.",
                    "Mais um caso onde interesses ocultos determinam o rumo dos acontecimentos.",
                    "Enquanto celebram esta notícia, ignoram os problemas estruturais que continuam sem solução."
                ],
                "anjinho": [
                    "Uma notícia que traz esperança e mostra que estamos no caminho certo.",
                    "Prova de que, quando há vontade, é possível fazer a diferença positivamente.",
                    "Um exemplo inspirador que deveria ser seguido em outros contextos."
                ]
            }
        }
        
        # Selecionar categoria mais próxima
        cat = categoria.lower() if categoria and categoria.lower() in templates else "geral"
        
        # Selecionar template aleatório para cada perspectiva
        capetinha = random.choice(templates[cat]["capetinha"])
        anjinho = random.choice(templates[cat]["anjinho"])
        
        return capetinha, anjinho
