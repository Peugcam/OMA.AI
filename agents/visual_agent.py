"""
Visual Agent - Planejador de Conteúdo Visual Híbrido

Estratégia inteligente:
1. Classifica cada cena como "genérica" ou "específica"
2. Genérica → busca vídeo no Pexels (GRÁTIS)
3. Específica → gera imagem com Stability AI (PAGO)
4. Mix perfeito: vídeos reais + imagens conceituais

Usa: Pexels API + Stability AI + OpenRouter (Gemma-2-9B)
"""

import logging
import os
import requests
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from core import AIClient, AIClientFactory, PromptTemplates, ResponseValidator


class VisualAgent:
    """
    Agente especializado em gerar/buscar conteúdo visual híbrido.

    Estratégia:
    - Classifica cena automaticamente (LLM)
    - Pexels API para vídeos reais (genérico)
    - Stability AI para imagens únicas (específico)
    - Gemma-2-9B (via OpenRouter) para análise e decisão

    Resultado: Mix perfeito de vídeos + imagens conceituais
    """

    def __init__(self, model_name: str = None):
        """
        Inicializa Visual Agent.

        Args:
            model_name: Modelo para análise (None = auto-detecta do .env)
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # AI client para análise de cenas
        if model_name:
            self.llm = AIClient(model=model_name, temperature=0.5)
        else:
            self.llm = AIClientFactory.create_for_agent("visual")

        # Pexels API key (stock videos - GRÁTIS)
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not self.pexels_api_key:
            self.logger.warning("PEXELS_API_KEY não configurada")

        # Stability AI API key (image generation - PAGO)
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        if not self.stability_api_key:
            self.logger.warning("STABILITY_API_KEY não configurada, usando placeholders")

        # Diretórios de saída (múltiplos locais)
        self.output_dirs = [
            Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos/images"),
            Path("D:/OMA_Videos/images"),
            Path("./outputs/images")
        ]

        # Criar diretórios
        for dir_path in self.output_dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.warning(f"Não foi possível criar {dir_path}: {e}")

        # Usar primeiro como principal
        self.output_dir = self.output_dirs[0]

        # System prompt
        self.system_prompt = PromptTemplates.visual_system_prompt()


    async def plan_visuals(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera plano visual completo baseado no roteiro.

        Args:
            state: Estado com roteiro gerado

        Returns:
            Estado atualizado com plano visual
        """
        self.logger.info("Planejando conteúdo visual...")

        script = state.get("script")
        if not script:
            raise ValueError("Script não encontrado no estado")

        scenes = script.get("scenes", [])
        if not scenes:
            raise ValueError("Script sem cenas")

        # Processar cada cena
        visual_plan = {
            "visual_plan_id": f"visual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "scenes": [],
            "generated_at": datetime.now().isoformat()
        }

        for scene in scenes:
            self.logger.info(f"Processando cena {scene['scene_number']}...")

            # Gerar imagem para a cena
            visual_scene = await self._generate_scene_visual(scene, state)

            visual_plan["scenes"].append(visual_scene)

        # Atualizar estado
        state["visual_plan"] = visual_plan
        state["current_phase"] = 2

        self.logger.info(f"OK - Plano visual criado: {len(visual_plan['scenes'])} cenas")

        return state


    async def _generate_scene_visual(
        self,
        scene: Dict[str, Any],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera conteúdo visual para uma cena usando estratégia híbrida.

        FLUXO HÍBRIDO INTELIGENTE:
        1. Classifica cena (genérica vs específica)
        2. Genérica → Pexels (vídeo real)
        3. Específica → Stability AI (imagem conceitual)
        4. Fallback → Placeholder

        Args:
            scene: Dados da cena do roteiro
            state: Estado completo

        Returns:
            Dados visuais da cena com source e custo
        """
        scene_num = scene.get("scene_number", 1)
        description = scene.get("visual_description", "")
        mood = scene.get("mood", "neutral")

        self.logger.info(f"🎬 Cena {scene_num}: {description[:60]}...")

        # STEP 1: Classificar tipo de cena
        scene_type = await self._classify_scene_type(description, mood)
        self.logger.info(f"📊 Classificação: {scene_type}")

        # STEP 2: Executar estratégia apropriada
        if scene_type == "pexels":
            # Tentar buscar vídeo no Pexels
            if self.pexels_api_key:
                try:
                    video_data = await self._search_pexels(description, mood)
                    if video_data and video_data.get("local_path"):
                        self.logger.info(f"✅ Vídeo Pexels baixado (custo: $0)")
                        return {
                            "scene_number": scene_num,
                            "media_path": video_data["local_path"],
                            "media_type": "video",
                            "source": "pexels",
                            "duration": scene.get("duration", 5),
                            "mood": mood,
                            "cost": 0.0,
                            "keywords": video_data.get("keywords", []),
                            "pexels_url": video_data.get("url")
                        }
                    else:
                        self.logger.warning(f"⚠️ Pexels não encontrou, fallback → Stability AI")
                except Exception as e:
                    self.logger.error(f"❌ Erro Pexels: {e}, fallback → Stability AI")

        # STEP 3: Usar Stability AI (cena específica OU fallback)
        if self.stability_api_key:
            try:
                prompt = await self._create_image_prompt(description, mood, state)
                image_path = self._generate_with_stability(prompt, scene_num)

                cost = 0.04  # SDXL 1024x1024
                self.logger.info(f"🎨 Imagem Stability gerada (custo: ${cost})")

                return {
                    "scene_number": scene_num,
                    "media_path": str(image_path),
                    "media_type": "image",
                    "source": "stability_ai",
                    "prompt_used": prompt,
                    "duration": scene.get("duration", 5),
                    "mood": mood,
                    "cost": cost,
                    "classification": scene_type
                }
            except Exception as e:
                self.logger.error(f"❌ Erro Stability AI: {e}, usando placeholder")

        # STEP 4: Fallback final → Placeholder
        self.logger.warning("⚠️ Usando placeholder (nenhuma API disponível)")
        placeholder_path = self._create_placeholder_image(scene_num)

        return {
            "scene_number": scene_num,
            "media_path": str(placeholder_path),
            "media_type": "image",
            "source": "placeholder",
            "duration": scene.get("duration", 5),
            "mood": mood,
            "cost": 0.0
        }


    async def _classify_scene_type(self, description: str, mood: str) -> str:
        """
        Classifica cena como "pexels" ou "stability" usando LLM.

        PEXELS = Cenas genéricas filmáveis (vídeos reais)
        STABILITY = Cenas específicas/abstratas (imagens conceituais)

        Args:
            description: Descrição visual da cena
            mood: Mood/atmosfera

        Returns:
            "pexels" ou "stability"
        """
        try:
            # PRIMEIRO: Checar keywords ANTES de chamar LLM (evita custos e erros)
            desc_lower = description.lower()

            # Palavras que indicam PESSOAS (sempre Pexels) - PRIORIDADE MÁXIMA
            people_keywords = ['pessoa', 'pessoas', 'rosto', 'mão', 'mãos', 'equipe',
                               'grupo', 'trabalhando', 'sorrindo', 'olhando', 'reunião',
                               'professor', 'estudante', 'apresentador', 'instrutor',
                               'explicando', 'ensinando', 'aula', 'palestra', 'apresentação',
                               'homem', 'mulher', 'jovem', 'adulto', 'criança',
                               'falando', 'conversando', 'interagindo', 'gesticulando']

            # Checar pessoas ANTES de chamar LLM
            if any(keyword in desc_lower for keyword in people_keywords):
                self.logger.info(f"✅ KEYWORD MATCH: Palavra de PESSOA detectada → FORÇANDO PEXELS")
                return "pexels"

            classification_prompt = f"""Classifique esta cena de vídeo como "pexels" ou "stability".

DESCRIÇÃO DA CENA: {description}
MOOD: {mood}

REGRAS CRÍTICAS:

"pexels" = SEMPRE para cenas com PESSOAS (Stability AI é HORRÍVEL com rostos):
✅ QUALQUER cena com pessoas, rostos, mãos visíveis
✅ Expressões faciais, emoções humanas
✅ Interações entre pessoas (reunião, conversa, aperto de mãos)
✅ Pessoas em ação (trabalhando, digitando, caminhando, apresentando)
✅ Conteúdo educativo (professor, instrutor, apresentador, palestrante)
✅ Aulas, apresentações, explicações, demonstrações
✅ Close-ups de pessoas
✅ Lugares comuns (escritório, café, rua, natureza, casa, sala de aula)
✅ Objetos cotidianos com pessoas (laptop sendo usado, telefone na mão)
✅ Qualquer situação envolvendo humanos

"stability" = APENAS para cenas SEM pessoas/rostos/humanos:
✅ Logos e branding (flutuando sozinhos, sem mãos)
✅ Ambientes vazios futuristas (SEM pessoas)
✅ Conceitos abstratos puros (partículas, hologramas SEM humanos)
✅ Produtos sozinhos (NUNCA com mãos segurando)
✅ Paisagens conceituais vazias
✅ Arte abstrata sem figuras humanas
✅ Objetos impossíveis de filmar no mundo real

CRÍTICO:
- Se mencionar "pessoa", "professor", "instrutor", "apresentador", "rosto", "mão", "sorriso", "olhar", "explicando", "ensinando", "falando" → SEMPRE "pexels"
- Conteúdo educativo/didático SEMPRE tem pessoas → SEMPRE "pexels"
- Stability AI gera rostos DEFORMADOS e mãos com dedos extras 😱
- Apenas use "stability" se for 100% certeza de NÃO ter humanos

IMPORTANTE: Na dúvida, escolha "pexels" (vídeos reais são sempre melhores e mais seguros).

Responda APENAS com uma palavra: pexels ou stability"""

            response = await self.llm.chat(
                messages=[{
                    "role": "user",
                    "content": classification_prompt
                }],
                temperature=0.3,
                max_tokens=50  # Aumentado de 10 para 50
            )

            classification = response.strip().lower()

            # Debug
            self.logger.info(f"LLM response raw: '{response}'")
            self.logger.info(f"LLM response cleaned: '{classification}'")

            # Validar resposta
            if "pexels" in classification:
                return "pexels"
            elif "stability" in classification:
                return "stability"
            else:
                # Fallback: detectar palavras-chave diretamente
                desc_lower = description.lower()

                # Palavras que indicam PESSOAS (sempre Pexels)
                people_keywords = ['pessoa', 'pessoas', 'rosto', 'mão', 'mãos', 'equipe',
                                   'grupo', 'trabalhando', 'sorrindo', 'olhando', 'reunião',
                                   'professor', 'estudante', 'apresentador', 'instrutor',
                                   'explicando', 'ensinando', 'aula', 'palestra', 'apresentação',
                                   'homem', 'mulher', 'jovem', 'adulto', 'criança',
                                   'falando', 'conversando', 'interagindo', 'gesticulando']

                # Palavras que indicam ABSTRATO (Stability) - SEM pessoas
                abstract_keywords = ['logo', 'holográfico', 'digital abstrato', 'visualização de dados',
                                     'conceito puro', 'futurista vazio', 'partículas flutuando',
                                     'cérebro digital', 'holograma flutuante', 'ambiente vazio']

                # Checar pessoas primeiro
                if any(keyword in desc_lower for keyword in people_keywords):
                    self.logger.info(f"✅ Detectou palavra-chave de PESSOA, forçando pexels")
                    return "pexels"

                # Checar abstrato (APENAS se não tiver pessoas)
                if any(keyword in desc_lower for keyword in abstract_keywords):
                    self.logger.info(f"🎨 Detectou palavra-chave ABSTRATA (sem pessoas), forçando stability")
                    return "stability"

                # Default: pexels (vídeos reais preferíveis)
                self.logger.warning(f"⚠️ Classificação ambígua: '{classification}', usando pexels (default seguro)")
                return "pexels"

        except Exception as e:
            self.logger.error(f"Erro ao classificar cena: {e}, usando pexels (default)")
            return "pexels"


    async def _search_pexels(self, description: str, mood: str) -> Dict[str, Any]:
        """
        Busca vídeo no Pexels API.

        Args:
            description: Descrição da cena em português
            mood: Mood/atmosfera

        Returns:
            Dict com url e metadata do vídeo, ou None se não encontrar
        """
        try:
            # Gerar keywords em inglês usando LLM
            keywords = await self._generate_pexels_keywords(description, mood)

            self.logger.info(f"🔍 Buscando Pexels: {keywords}")

            # Fazer busca no Pexels
            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers={"Authorization": self.pexels_api_key},
                params={
                    "query": keywords,
                    "per_page": 3,
                    "orientation": "landscape",
                    "size": "medium"  # HD quality
                },
                timeout=10
            )

            if response.status_code != 200:
                self.logger.error(f"Pexels API error: {response.status_code}")
                return None

            data = response.json()

            if not data.get("videos"):
                self.logger.warning(f"Nenhum vídeo encontrado para: {keywords}")
                return None

            # Pegar primeiro vídeo
            video = data["videos"][0]

            # Pegar URL do arquivo de vídeo (melhor qualidade disponível)
            video_files = video.get("video_files", [])
            if not video_files:
                return None

            # Preferir HD (1280x720 ou maior)
            hd_video = None
            for vf in video_files:
                if vf.get("width", 0) >= 1280:
                    hd_video = vf
                    break

            # Se não tiver HD, pegar o de maior qualidade
            if not hd_video:
                hd_video = max(video_files, key=lambda x: x.get("width", 0))

            # Baixar o vídeo localmente
            video_url = hd_video["link"]
            video_id = video.get("id")
            local_path = self._download_pexels_video(video_url, video_id)

            return {
                "url": video_url,
                "local_path": str(local_path) if local_path else None,
                "width": hd_video.get("width"),
                "height": hd_video.get("height"),
                "duration": video.get("duration", 10),
                "id": video_id,
                "keywords": keywords
            }

        except Exception as e:
            self.logger.error(f"Erro ao buscar Pexels: {e}")
            return None


    def _download_pexels_video(self, video_url: str, video_id: int) -> Path:
        """
        Baixa vídeo do Pexels localmente.

        Args:
            video_url: URL do vídeo
            video_id: ID do vídeo no Pexels

        Returns:
            Path do arquivo baixado
        """
        try:
            # Criar diretório de downloads
            download_dir = Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos/pexels_videos")
            download_dir.mkdir(parents=True, exist_ok=True)

            # Nome do arquivo
            filename = f"pexels_{video_id}.mp4"
            filepath = download_dir / filename

            # Se já existe, retornar
            if filepath.exists():
                self.logger.info(f"Vídeo já existe: {filepath}")
                return filepath

            # Baixar
            self.logger.info(f"📥 Baixando vídeo Pexels ID {video_id}...")
            response = requests.get(video_url, stream=True, timeout=60)
            response.raise_for_status()

            # Salvar
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = filepath.stat().st_size / (1024 * 1024)  # MB
            self.logger.info(f"✅ Download completo: {filepath} ({file_size:.1f} MB)")

            return filepath

        except Exception as e:
            self.logger.error(f"Erro ao baixar vídeo Pexels: {e}")
            return None


    async def _generate_pexels_keywords(self, description: str, mood: str) -> str:
        """
        Gera keywords em inglês otimizadas para busca no Pexels.

        Args:
            description: Descrição em português
            mood: Mood/atmosfera

        Returns:
            Keywords em inglês para Pexels
        """
        try:
            prompt = f"""Gere keywords em inglês para buscar vídeo no Pexels.

DESCRIÇÃO: {description}
MOOD: {mood}

REGRAS:
- Máximo 3-5 palavras-chave
- Em inglês
- Genéricas (não específicas demais)
- Sem pontuação

EXEMPLOS:
"Pessoa trabalhando em laptop" → "person working laptop office"
"Reunião de equipe colaborativa" → "team meeting collaboration"
"Logo holográfico futurista" → "holographic technology futuristic"

Responda APENAS com as keywords (sem aspas, sem explicação):"""

            response = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=30
            )

            keywords = response.strip().strip('"').strip("'")

            return keywords

        except Exception as e:
            self.logger.error(f"Erro ao gerar keywords: {e}")
            # Fallback: tradução simples
            return description[:50]


    async def _create_image_prompt(
        self,
        description: str,
        mood: str,
        state: Dict[str, Any]
    ) -> str:
        """
        Cria prompt otimizado para Stability AI COM REFLECTION.

        Reflection = Crítica do prompt + Melhoria (NÃO gera imagem 2x)

        Melhoria: +20% qualidade de imagem, +$0.02/vídeo (apenas LLM, não Stability)

        Args:
            description: Descrição visual da cena
            mood: Mood/atmosfera
            state: Estado completo

        Returns:
            Prompt formatado otimizado para geração (em inglês)
        """
        self.logger.info("🧠 [REFLECTION] Criando prompt com auto-crítica...")

        # Usar Reflection apenas nos prompts
        return await self._create_image_prompt_with_reflection(description, mood, state)


    async def _create_image_prompt_with_reflection(
        self,
        description: str,
        mood: str,
        state: Dict[str, Any]
    ) -> str:
        """
        Cria prompt com Reflection: gera → critica → melhora.

        IMPORTANTE: Reflete apenas no PROMPT, NÃO gera imagem 2x!

        Fluxo:
        1. Gerar prompt v1
        2. Crítica do prompt (técnica, composição, estilo)
        3. Se score < 8, gerar prompt v2 melhorado
        4. Retornar melhor prompt (UMA imagem será gerada)

        Args:
            description: Descrição visual da cena
            mood: Mood/atmosfera
            state: Estado completo

        Returns:
            Prompt otimizado (em inglês)
        """
        style = state.get("brief", {}).get("style", "professional")

        # PASSO 1: Gerar prompt v1
        prompt_pt_v1 = f"{description}, {mood} mood, {style} style, high quality, detailed, professional photography, 4k"
        prompt_en_v1 = await self._translate_to_english(prompt_pt_v1)

        self.logger.info(f"📝 [REFLECTION] Prompt v1: {prompt_en_v1[:80]}...")

        # PASSO 2: Crítica do prompt
        critique = await self._critique_image_prompt(prompt_en_v1, description, mood, style)

        score = critique.get("score", 0)
        self.logger.info(f"📊 [REFLECTION] Score prompt v1: {score}/10")

        # PASSO 3: Se score < 8, melhorar prompt
        if score < 8:
            self.logger.info(f"🔄 [REFLECTION] Score baixo ({score}/10), melhorando prompt...")

            prompt_en_v2 = await self._improve_image_prompt(
                prompt_en_v1, critique, description, mood, style
            )

            self.logger.info(f"✅ [REFLECTION] Prompt v2: {prompt_en_v2[:80]}...")

            return prompt_en_v2
        else:
            self.logger.info(f"✅ [REFLECTION] Score alto ({score}/10), usando prompt v1")
            return prompt_en_v1


    async def _critique_image_prompt(
        self,
        prompt: str,
        description: str,
        mood: str,
        style: str
    ) -> Dict[str, Any]:
        """
        Crítica de prompt para geração de imagem.

        Avalia:
        1. Detalhamento técnico (1-10)
        2. Consistência de estilo (1-10)
        3. Clareza de composição (1-10)
        4. Especificidade (1-10)

        Args:
            prompt: Prompt gerado (em inglês)
            description: Descrição original
            mood: Mood desejado
            style: Estilo desejado

        Returns:
            Dict com score e sugestões
        """
        critique_prompt = f"""Você é um expert em prompts para Stability AI / DALL-E.

Avalie este prompt para geração de imagem:

PROMPT: "{prompt}"

CONTEXTO:
- Descrição desejada: {description}
- Mood: {mood}
- Estilo: {style}

CRITÉRIOS (1-10):
1. DETALHAMENTO TÉCNICO: Tem detalhes de iluminação, ângulo, composição?
2. CONSISTÊNCIA DE ESTILO: Mantém estilo coerente?
3. CLAREZA DE COMPOSIÇÃO: Descreve composição visual clara?
4. ESPECIFICIDADE: É específico o suficiente?

IMPORTANTE:
- Prompts bons têm 20-40 palavras
- Incluem: subject, style, lighting, composition, quality
- Evitam ambiguidade

Responda em JSON:
{{
  "scores": {{
    "detalhamento": número,
    "consistencia": número,
    "clareza": número,
    "especificidade": número
  }},
  "score": média,
  "pontos_fracos": ["fraqueza1", "fraqueza2"],
  "sugestoes": ["adicionar detalhes de iluminação", "especificar ângulo"],
  "summary": "resumo"
}}"""

        response = await self.llm.chat(
            messages=[{"role": "user", "content": critique_prompt}],
            temperature=0.3,
            max_tokens=500
        )

        critique = ResponseValidator.extract_first_json(response)

        if not critique or "score" not in critique:
            # Fallback
            self.logger.warning("⚠️ Crítica de prompt inválida, usando score 7")
            return {
                "score": 7,
                "pontos_fracos": ["Prompt genérico"],
                "sugestoes": ["Adicionar mais detalhes técnicos"],
                "summary": "Prompt funcional mas pode melhorar"
            }

        return critique


    async def _improve_image_prompt(
        self,
        prompt_v1: str,
        critique: Dict[str, Any],
        description: str,
        mood: str,
        style: str
    ) -> str:
        """
        Melhora prompt baseado na crítica.

        Args:
            prompt_v1: Prompt original
            critique: Crítica com sugestões
            description: Descrição original
            mood: Mood
            style: Estilo

        Returns:
            Prompt v2 melhorado (em inglês)
        """
        improve_prompt = f"""Você é um expert em prompts para Stability AI.

Melhore este prompt baseado na crítica:

PROMPT ORIGINAL:
"{prompt_v1}"

CRÍTICA:
Score: {critique.get('score')}/10
Pontos Fracos: {critique.get('pontos_fracos', [])}
Sugestões: {critique.get('sugestoes', [])}

CONTEXTO:
- Descrição: {description}
- Mood: {mood}
- Estilo: {style}

TAREFA:
- Corrija pontos fracos
- Implemente sugestões
- Mantenha essência da descrição original
- 20-40 palavras
- Inclua: subject, style, lighting, composition, quality

Retorne APENAS o prompt melhorado (sem aspas, sem explicação):"""

        response = await self.llm.chat(
            messages=[{"role": "user", "content": improve_prompt}],
            temperature=0.4,
            max_tokens=150
        )

        prompt_v2 = response.strip().strip('"').strip("'")

        return prompt_v2


    async def _create_image_prompt_simple(
        self,
        description: str,
        mood: str,
        state: Dict[str, Any]
    ) -> str:
        """
        Cria prompt SIMPLES sem Reflection (fallback).

        Args:
            description: Descrição visual da cena
            mood: Mood/atmosfera
            state: Estado completo

        Returns:
            Prompt formatado para geração (em inglês)
        """
        style = state.get("brief", {}).get("style", "professional")

        # Criar prompt em português primeiro
        prompt_pt = f"{description}, {mood} mood, {style} style, high quality, detailed, professional photography, 4k"

        # Traduzir para inglês usando o LLM
        prompt_en = await self._translate_to_english(prompt_pt)

        self.logger.info(f"Prompt PT: {prompt_pt[:60]}...")
        self.logger.info(f"Prompt EN: {prompt_en[:60]}...")

        return prompt_en


    async def _translate_to_english(self, text: str) -> str:
        """
        Traduz texto de português para inglês usando o LLM.

        Args:
            text: Texto em português

        Returns:
            Texto traduzido para inglês
        """
        try:
            translation = await self.llm.chat(
                messages=[{
                    "role": "user",
                    "content": f"Translate this to English (just the translation, no extra text):\n\n{text}"
                }],
                temperature=0.3,
                max_tokens=200
            )

            # Limpar resposta (remover aspas, etc)
            translation = translation.strip().strip('"').strip("'")

            return translation

        except Exception as e:
            self.logger.error(f"Erro ao traduzir: {e}")
            # Fallback: retornar original (melhor que falhar)
            return text


    def _generate_with_stability(self, prompt: str, scene_num: int) -> Path:
        """
        Gera imagem usando Stability AI API.

        Args:
            prompt: Prompt para geração
            scene_num: Número da cena

        Returns:
            Path para imagem salva

        Raises:
            Exception: Se geração falhar
        """
        self.logger.info(f"Gerando imagem com Stability AI (cena {scene_num})...")

        # API endpoint
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        # Headers
        headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Payload
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }

        # Fazer requisição
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code != 200:
            raise Exception(f"Stability AI error: {response.status_code} - {response.text}")

        # Processar resposta
        data = response.json()

        # Salvar imagem
        image_data = data["artifacts"][0]
        image_base64 = image_data["base64"]

        import base64
        image_bytes = base64.b64decode(image_base64)

        # Salvar arquivo
        image_path = self.output_dir / f"scene_{scene_num:02d}.png"
        image_path.write_bytes(image_bytes)

        self.logger.info(f"OK - Imagem salva: {image_path}")

        return image_path


    def _create_placeholder_image(self, scene_num: int) -> Path:
        """
        Cria imagem placeholder quando Stability AI não está disponível.

        Args:
            scene_num: Número da cena

        Returns:
            Path para imagem placeholder
        """
        self.logger.info(f"Criando placeholder para cena {scene_num}...")

        try:
            from PIL import Image, ImageDraw, ImageFont

            # Criar imagem 1024x1024
            img = Image.new('RGB', (1024, 1024), color=(73, 109, 137))
            draw = ImageDraw.Draw(img)

            # Adicionar texto
            text = f"Cena {scene_num}\n(Placeholder)"

            # Tentar usar fonte, senão usar padrão
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()

            # Posição central
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            position = ((1024 - text_width) // 2, (1024 - text_height) // 2)

            draw.text(position, text, fill=(255, 255, 255), font=font)

            # Salvar
            image_path = self.output_dir / f"scene_{scene_num:02d}_placeholder.png"
            img.save(image_path)

            self.logger.info(f"OK - Placeholder salvo: {image_path}")

            return image_path

        except Exception as e:
            self.logger.error(f"Erro ao criar placeholder: {e}")

            # Criar arquivo texto como último recurso
            image_path = self.output_dir / f"scene_{scene_num:02d}_placeholder.txt"
            image_path.write_text(f"Placeholder para cena {scene_num}")

            return image_path


# ============================================================================
# Para compatibilidade com supervisor antigo
# ============================================================================

# Alias para manter compatibilidade
generate_visuals = VisualAgent().plan_visuals
