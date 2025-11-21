"""
MCP Visual Server - Integração com OpenRouter para Tool Calling
Permite que LLMs escolham automaticamente entre Pexels e Stability
"""

import logging
import json
from typing import Dict, Any, List, Optional

from core.ai_client_mcp import AIClientMCP
from .tools import search_pexels_video, generate_stability_image, generate_hybrid_visual, AVAILABLE_TOOLS
from .schemas import VisualResult, PexelsSearchResult, StabilityImageResult, HybridVisualResult


logger = logging.getLogger(__name__)


class MCPVisualServer:
    """
    MCP Server para Visual Agent.

    Fornece tool calling estruturado para LLMs escolherem
    automaticamente entre Pexels e Stability AI.

    Elimina necessidade de:
    - Classificação manual (string matching)
    - Múltiplas chamadas LLM
    - Parsing frágil de respostas
    """

    def __init__(self, model_name: str = "openai/gpt-4o-mini-2024-07-18"):
        """
        Inicializa MCP server.

        Args:
            model_name: Modelo LLM para tool calling (via OpenRouter)
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # AI client MCP com suporte a tool calling
        self.llm = AIClientMCP(model=model_name, use_local=False)

        # Tool functions
        self.tool_functions = {
            "search_pexels_video": search_pexels_video,
            "generate_stability_image": generate_stability_image,
            "generate_hybrid_visual": generate_hybrid_visual
        }

        self.logger.info(f"MCP Visual Server inicializado (modelo: {model_name}, MCP enabled)")


    async def get_visual_for_scene(
        self,
        description: str,
        mood: str,
        style: Optional[str] = None
    ) -> VisualResult:
        """
        Obtém conteúdo visual para uma cena usando tool calling.

        O LLM escolhe automaticamente entre Pexels e Stability
        baseado na descrição da cena.

        Args:
            description: Descrição visual da cena
            mood: Mood/atmosfera (energetic, calm, professional, etc)
            style: Estilo visual opcional (modern, tech, cinematic, etc)

        Returns:
            PexelsSearchResult OU StabilityImageResult (tipo garantido)

        Example:
            >>> result = await server.get_visual_for_scene(
            ...     description="Person working on laptop in modern office",
            ...     mood="professional"
            ... )
            >>> # result é PexelsSearchResult (LLM escolheu Pexels automaticamente)
            >>> video_path = result.local_path
        """
        self.logger.info(f"MCP: Obtendo visual para: '{description[:60]}...'")

        # Criar prompt que guia o LLM a escolher a tool correta
        prompt = self._create_tool_selection_prompt(description, mood, style)

        # Preparar tools no formato OpenRouter
        tools = self._format_tools_for_openrouter()

        try:
            # Chamar LLM com tool calling
            response = await self.llm.chat_with_tools(
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                tool_choice="auto",  # LLM escolhe automaticamente
                temperature=0.3,  # Baixa temperatura para decisões consistentes
                system_prompt=self._get_system_prompt()
            )

            # Processar resposta do tool calling
            result = self._process_tool_call_response(response)

            self.logger.info(f"OK - Visual obtido via {result.source}")

            return result

        except Exception as e:
            self.logger.error(f"Erro no MCP tool calling: {e}")
            # Fallback: tentar Pexels
            return self._fallback_to_pexels(description)


    def _create_tool_selection_prompt(
        self,
        description: str,
        mood: str,
        style: Optional[str] = None
    ) -> str:
        """
        Cria prompt otimizado para tool selection.

        Args:
            description: Descrição da cena
            mood: Mood
            style: Estilo opcional

        Returns:
            Prompt formatado
        """
        style_text = f", {style} style" if style else ""

        return f"""Get visual content for this video scene:

SCENE DESCRIPTION: {description}
MOOD: {mood}{style_text}

IMPORTANT RULES:
1. If scene has PEOPLE (faces, hands, humans) → use search_pexels_video
2. If scene is LOGO/ABSTRACT/FUTURISTIC (no people) → use generate_stability_image

Stability AI generates DEFORMED people - NEVER use it for humans.

Choose the appropriate tool and execute it."""


    def _get_system_prompt(self) -> str:
        """
        System prompt para guiar decisões de tool calling.

        Returns:
            System prompt otimizado
        """
        return """You are a visual content expert specializing in choosing the right media source.

Your task: Analyze scene descriptions and choose between THREE tools:

1. search_pexels_video: For real-world footage (people, actions, places)
   - ALWAYS use for scenes with people, faces, hands, human actions
   - Examples: "person working", "team meeting", "teacher explaining"

2. generate_stability_image: For conceptual visuals (logos, abstract, futuristic)
   - ONLY use for scenes WITHOUT any people/humans
   - Examples: "floating logo", "abstract data visualization", "empty futuristic city"

3. generate_hybrid_visual: For scenes with BOTH people AND digital elements
   - Use when scene combines real humans with abstract/digital overlay
   - Examples: "person presenting chart", "team with company logo", "office with hologram"

KEY RULES:
- NEVER use Stability for people/faces - it generates DEFORMED humans
- When in doubt, use Pexels (real footage is safer)
- Use hybrid when scene clearly needs both real video AND digital overlay

Make your choice and execute the appropriate tool immediately."""


    def _format_tools_for_openrouter(self) -> List[Dict[str, Any]]:
        """
        Formata tools no formato esperado pelo OpenRouter.

        Returns:
            Lista de tools formatadas
        """
        formatted_tools = []

        for tool_name, tool_info in AVAILABLE_TOOLS.items():
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": tool_info["parameters"]
                }
            })

        return formatted_tools


    def _process_tool_call_response(self, response: str) -> VisualResult:
        """
        Processa resposta do LLM com tool calling.

        Args:
            response: Resposta do LLM (pode conter tool calls)

        Returns:
            VisualResult (Pexels ou Stability)

        Raises:
            Exception: Se não houver tool call válido
        """
        # Tentar extrair tool call do response
        # OpenRouter retorna tool calls em formato JSON

        try:
            # Se response é JSON com tool_calls
            if isinstance(response, str) and "{" in response:
                data = json.loads(response)
                if "tool_calls" in data:
                    tool_call = data["tool_calls"][0]
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])

                    # Executar tool
                    return self._execute_tool(tool_name, tool_args)

            # Fallback: procurar por padrões no texto
            if "search_pexels_video" in response.lower():
                # Extrair keywords do response
                keywords = self._extract_keywords_from_response(response)
                return search_pexels_video(keywords=keywords)

            elif "generate_stability_image" in response.lower():
                # Extrair prompt do response
                prompt = self._extract_prompt_from_response(response)
                return generate_stability_image(prompt=prompt)

            else:
                raise Exception("Nenhum tool call detectado no response")

        except Exception as e:
            self.logger.error(f"Erro ao processar tool call: {e}")
            raise


    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> VisualResult:
        """
        Executa tool escolhido pelo LLM.

        Args:
            tool_name: Nome do tool
            tool_args: Argumentos do tool

        Returns:
            Resultado do tool (validado)
        """
        self.logger.info(f"Executando tool: {tool_name}")
        self.logger.info(f"Argumentos: {tool_args}")

        if tool_name == "search_pexels_video":
            return search_pexels_video(**tool_args)
        elif tool_name == "generate_stability_image":
            return generate_stability_image(**tool_args)
        else:
            raise ValueError(f"Tool desconhecido: {tool_name}")


    def _extract_keywords_from_response(self, response: str, context: str = "") -> str:
        """
        Extrai keywords de response de fallback COM CONTEXTO.

        Args:
            response: Resposta do LLM
            context: Descricao original da cena para contexto

        Returns:
            Keywords relevantes para Pexels
        """
        # Mapeamento PT -> EN para keywords comuns
        pt_to_en = {
            'pessoa': 'person', 'pessoas': 'people', 'trabalhando': 'working',
            'escritorio': 'office', 'reuniao': 'meeting', 'equipe': 'team',
            'laptop': 'laptop', 'computador': 'computer', 'apresentando': 'presenting',
            'professor': 'teacher', 'estudante': 'student', 'aula': 'classroom',
            'tecnologia': 'technology', 'negocio': 'business', 'corporativo': 'corporate',
            'moderno': 'modern', 'profissional': 'professional', 'digital': 'digital'
        }

        # Usar contexto se disponivel
        text = context if context else response

        # Extrair palavras e traduzir
        words = text.lower().split()
        keywords = []

        for word in words:
            # Remover pontuacao
            clean_word = ''.join(c for c in word if c.isalnum())
            if clean_word in pt_to_en:
                keywords.append(pt_to_en[clean_word])
            elif len(clean_word) > 3 and clean_word.isascii():
                keywords.append(clean_word)

        # Limitar a 5 keywords
        if keywords:
            return ' '.join(keywords[:5])

        # Fallback baseado em padroes comuns
        if any(p in text.lower() for p in ['pessoa', 'trabalhando', 'equipe']):
            return "person working office professional"
        elif any(p in text.lower() for p in ['tecnologia', 'digital', 'dados']):
            return "technology digital modern business"
        else:
            return "business professional modern"


    def _extract_prompt_from_response(self, response: str, context: str = "") -> str:
        """
        Extrai prompt de response de fallback COM CONTEXTO.

        Args:
            response: Resposta do LLM
            context: Descricao original da cena para contexto

        Returns:
            Prompt relevante para Stability
        """
        # Usar contexto se disponivel
        text = context if context else response

        # Detectar tipo de conteudo abstrato
        if any(p in text.lower() for p in ['logo', 'marca', 'brand']):
            return "modern minimalist logo, professional design, blue gradient, clean lines, high quality, 4k"
        elif any(p in text.lower() for p in ['holograma', 'hologram', 'digital']):
            return "holographic display, futuristic technology, glowing blue particles, sci-fi style, high quality"
        elif any(p in text.lower() for p in ['dados', 'data', 'grafico', 'chart']):
            return "abstract data visualization, flowing particles, blue and cyan colors, modern tech style, 4k"
        elif any(p in text.lower() for p in ['futurista', 'futuristic', 'espacial']):
            return "futuristic empty environment, sci-fi architecture, blue lighting, no people, cinematic"
        else:
            return "modern abstract concept, professional design, blue tones, high quality, 4k"


    def _fallback_to_pexels(self, description: str) -> PexelsSearchResult:
        """
        Fallback contextual: usa Pexels quando tool calling falha.

        Usa contexto da descricao para gerar keywords relevantes.

        Args:
            description: Descricao original da cena

        Returns:
            PexelsSearchResult
        """
        self.logger.warning(f"Usando fallback contextual para Pexels (desc: {description[:50]}...)")

        # Gerar keywords baseadas no contexto
        keywords = self._extract_keywords_from_response("", context=description)

        self.logger.info(f"Keywords de fallback: '{keywords}'")

        try:
            return search_pexels_video(keywords=keywords)
        except Exception as e:
            self.logger.error(f"Fallback Pexels falhou: {e}")
            raise


    def _fallback_to_stability(self, description: str) -> StabilityImageResult:
        """
        Fallback contextual: usa Stability quando Pexels falha para cenas abstratas.

        Args:
            description: Descricao original da cena

        Returns:
            StabilityImageResult
        """
        self.logger.warning(f"Usando fallback contextual para Stability (desc: {description[:50]}...)")

        # Gerar prompt baseado no contexto
        prompt = self._extract_prompt_from_response("", context=description)

        self.logger.info(f"Prompt de fallback: '{prompt[:60]}...'")

        try:
            return generate_stability_image(prompt=prompt)
        except Exception as e:
            self.logger.error(f"Fallback Stability falhou: {e}")
            raise


# ============================================================================
# HELPER: Traduzir descrição PT → EN para keywords
# ============================================================================

async def translate_description_to_keywords(
    description: str,
    llm_client: AIClientMCP
) -> str:
    """
    Traduz descrição em português para keywords em inglês.

    Args:
        description: Descrição em português
        llm_client: Cliente LLM para tradução

    Returns:
        Keywords em inglês
    """
    prompt = f"""Convert this scene description to English search keywords (3-5 words):

DESCRIPTION: {description}

Output ONLY the keywords, no explanation:"""

    response = await llm_client.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=30
    )

    keywords = response.strip().strip('"').strip("'")
    return keywords
