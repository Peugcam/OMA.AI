"""
📢 PRODUCT AD AGENT - Gerador de Anúncios de Produtos
======================================================

Especializado em criar anúncios profissionais de produtos.

Workflow:
1. Recebe imagem do produto + informações
2. Analisa produto com visão AI (GPT-4 Vision)
3. Pesquisa melhores abordagens de venda do produto (WebSearch)
4. Analisa concorrentes e estratégias de marketing eficazes
5. Cria copy persuasivo otimizado com insights de mercado
6. Gera vídeo com HeyGen Avatar apresentando
7. Adiciona imagem do produto com transições
8. Output: Anúncio profissional pronto para publicar

Estratégia de Anúncio:
- Abertura: Hook chamativo (3s)
- Apresentação: Avatar mostra produto (15s)
- Benefícios: Destaca features principais (10s)
- CTA: Call-to-action claro (2s)

Total: 30s de anúncio otimizado
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import httpx
import base64

from core import AIClient, AIClientFactory


class ProductCategory:
    """Categorias de produtos para afiliados físicos"""

    # Categorias principais para afiliados
    BEAUTY = "beauty"                    # Cosméticos, maquiagem
    FEMININE_HYGIENE = "feminine_hygiene"  # Higiene feminina
    PERFUMES = "perfumes"                # Perfumaria
    ELECTRONICS = "electronics"          # Eletrônicos, gadgets

    # Subcategorias de beleza
    SKINCARE = "skincare"               # Cuidados com a pele
    HAIRCARE = "haircare"               # Cuidados com cabelo
    MAKEUP = "makeup"                   # Maquiagem

    # Subcategorias eletrônicos
    GADGETS = "gadgets"                 # Gadgets, acessórios
    HOME_ELECTRONICS = "home_electronics"  # Eletrônicos para casa

    GENERIC = "generic"                 # Outros


class ProductAdAgent:
    """
    Agent especializado em criar anúncios de produtos.

    Custo estimado por anúncio:
    - Análise de imagem (GPT-4V): $0.01
    - Copy generation (GPT-4): $0.001
    - Avatar video (HeyGen): $0.05
    - Backgrounds (Flux): $0.06
    - Total: ~$0.12 por anúncio de 30s
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # AI client para análise e copy
        self.llm = AIClientFactory.create_for_agent("supervisor")

        # API keys
        self.heygen_key = os.getenv("HEYGEN_API_KEY")
        self.fal_key = os.getenv("FAL_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        # Output directory
        self.output_dir = Path("./outputs/product_ads")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # HTTP client
        self.client = httpx.AsyncClient(timeout=300.0)

    async def create_product_ad(
        self,
        product_info: Dict[str, Any],
        product_image_path: str
    ) -> Dict[str, Any]:
        """
        Cria anúncio completo do produto.

        Args:
            product_info: {
                'name': Nome do produto,
                'description': Descrição breve,
                'price': Preço (opcional),
                'category': Categoria (opcional),
                'target_audience': Público-alvo (opcional),
                'unique_selling_points': [lista de diferenciais] (opcional)
            }
            product_image_path: Caminho para imagem do produto

        Returns:
            {
                'ad_video_path': Caminho do vídeo final,
                'script': Script usado,
                'cost': Custo total,
                'generation_time': Tempo de geração
            }
        """
        start_time = datetime.now()
        self.logger.info(f"🎬 Creating ad for product: {product_info.get('name')}")

        try:
            # 1. Analisar imagem do produto com GPT-4 Vision
            analysis = await self._analyze_product_image(
                product_image_path,
                product_info
            )

            # 2. Determinar categoria e estratégia
            category = product_info.get('category') or analysis.get('category', ProductCategory.GENERIC)
            strategy = self._get_ad_strategy(category)

            # 3. Pesquisar melhores abordagens de venda do mercado
            market_research = await self._research_market_approaches(
                product_info,
                analysis,
                category
            )

            # 4. Gerar copy persuasivo otimizado com insights de mercado
            ad_copy = await self._generate_ad_copy(
                product_info,
                analysis,
                strategy,
                market_research
            )

            # 5. Gerar vídeo do avatar apresentando
            avatar_video = await self._generate_avatar_presentation(
                ad_copy['script']
            )

            # 6. Gerar backgrounds contextuais
            backgrounds = await self._generate_backgrounds(
                product_info,
                analysis,
                category
            )

            # 7. Compor vídeo final com FFmpeg
            final_video = await self._compose_final_ad(
                avatar_video_path=avatar_video['path'],
                product_image_path=product_image_path,
                backgrounds=backgrounds,
                ad_copy=ad_copy
            )

            # Calcular métricas
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()

            total_cost = (
                analysis.get('cost', 0.01) +
                ad_copy.get('cost', 0.001) +
                avatar_video.get('cost', 0.05) +
                sum(bg.get('cost', 0.02) for bg in backgrounds)
            )

            result = {
                'ad_video_path': final_video,
                'script': ad_copy['script'],
                'hooks': ad_copy['hooks'],
                'cta': ad_copy['cta'],
                'cost': total_cost,
                'generation_time': generation_time,
                'category': category,
                'analysis': analysis
            }

            self.logger.info(f"✅ Ad created! Cost: ${total_cost:.3f}, Time: {generation_time:.1f}s")
            return result

        except Exception as e:
            self.logger.error(f"❌ Error creating ad: {e}")
            raise

    async def _analyze_product_image(
        self,
        image_path: str,
        product_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analisa imagem do produto usando GPT-4 Vision.
        """
        self.logger.info("🔍 Analyzing product image...")

        # Encode image to base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Prompt para análise
        prompt = f"""
Analise esta imagem de produto e forneça:

Produto: {product_info.get('name', 'Não especificado')}
Descrição inicial: {product_info.get('description', 'Não fornecida')}

Por favor, identifique:
1. **Categoria**: tech/fashion/food/beauty/home/fitness/services/generic
2. **Características visuais**: cores, formato, estilo, qualidade aparente
3. **Público-alvo sugerido**: baseado na aparência do produto
4. **Pontos de venda visual**: o que mais se destaca na imagem
5. **Emoção evocada**: sentimento que o produto transmite
6. **Cenário de uso**: onde/quando seria usado
7. **Elementos de destaque**: partes do produto que chamam atenção

Responda em JSON format:
{{
    "category": "categoria",
    "visual_features": ["feature1", "feature2"],
    "target_audience": "descrição do público",
    "visual_selling_points": ["ponto1", "ponto2"],
    "emotion": "emoção principal",
    "use_case": "cenário de uso",
    "highlights": ["destaque1", "destaque2"],
    "quality_perception": "alta/média/baixa",
    "price_perception": "premium/médio/acessível"
}}
"""

        try:
            # Call OpenAI Vision API
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500
                }
            )

            result = response.json()
            analysis_text = result['choices'][0]['message']['content']

            # Parse JSON from response
            import json
            # Extract JSON from markdown code blocks if present
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]

            analysis = json.loads(analysis_text.strip())
            analysis['cost'] = 0.01  # GPT-4V cost

            self.logger.info(f"✅ Product analyzed as: {analysis.get('category')}")
            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
            # Fallback analysis
            return {
                'category': ProductCategory.GENERIC,
                'visual_features': ['produto'],
                'target_audience': 'público geral',
                'visual_selling_points': ['qualidade'],
                'emotion': 'confiança',
                'use_case': 'uso diário',
                'highlights': ['produto completo'],
                'quality_perception': 'média',
                'price_perception': 'médio',
                'cost': 0.0
            }

    async def _research_market_approaches(
        self,
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """
        Pesquisa as melhores abordagens de venda do produto no mercado.
        Analisa concorrentes, estratégias eficazes e tendências.
        """
        self.logger.info("🔎 Researching market approaches...")

        product_name = product_info.get('name', '')
        product_desc = product_info.get('description', '')

        # Construir query de pesquisa
        search_query = f"melhores estratégias venda marketing {product_name} {category} anúncios eficazes"

        try:
            # Pesquisa 1: Estratégias de venda do produto/categoria
            research_prompt = f"""
Pesquise e analise as melhores estratégias de marketing e venda para:

PRODUTO: {product_name}
CATEGORIA: {category}
DESCRIÇÃO: {product_desc}

Retorne em formato JSON:
{{
    "selling_points": ["ponto de venda 1", "ponto de venda 2", "ponto de venda 3"],
    "effective_hooks": ["hook 1 que funciona", "hook 2 que funciona", "hook 3 que funciona"],
    "common_objections": ["objeção 1", "objeção 2"],
    "counter_arguments": ["contra-argumento 1", "contra-argumento 2"],
    "emotional_triggers": ["gatilho emocional 1", "gatilho emocional 2"],
    "competitor_approaches": ["abordagem concorrente 1", "abordagem concorrente 2"],
    "best_practices": ["prática 1", "prática 2", "prática 3"],
    "target_pain_points": ["dor do cliente 1", "dor do cliente 2"],
    "value_propositions": ["proposta de valor 1", "proposta de valor 2"],
    "social_proof_elements": ["elemento prova social 1", "elemento prova social 2"],
    "urgency_tactics": ["tática urgência 1", "tática urgência 2"],
    "pricing_psychology": "insights sobre precificação",
    "recommended_cta": "call-to-action recomendado",
    "ad_format_tips": ["dica formato 1", "dica formato 2"]
}}
"""

            # Usar AI client para fazer pesquisa inteligente
            response = await self.ai_client.generate(
                model="gpt-4",
                messages=[{"role": "user", "content": research_prompt}],
                temperature=0.3
            )

            market_insights = response.get('content', '{}')

            # Parse JSON
            import json
            if '```json' in market_insights:
                market_insights = market_insights.split('```json')[1].split('```')[0]
            elif '```' in market_insights:
                market_insights = market_insights.split('```')[1].split('```')[0]

            research_data = json.loads(market_insights.strip())

            self.logger.info(f"✅ Market research completed: {len(research_data.get('selling_points', []))} selling points found")

            return {
                **research_data,
                'cost': 0.002  # Research cost
            }

        except Exception as e:
            self.logger.warning(f"⚠️ Market research failed: {e}. Using fallback strategies.")
            # Fallback: estratégias genéricas baseadas na categoria
            return self._get_fallback_market_research(category)

    def _get_fallback_market_research(self, category: str) -> Dict[str, Any]:
        """Estratégias de fallback caso a pesquisa falhe"""

        fallback_strategies = {
            ProductCategory.TECH: {
                "selling_points": ["Inovação tecnológica", "Facilidade de uso", "Compatibilidade"],
                "effective_hooks": ["Cansado de tecnologia complicada?", "O futuro chegou"],
                "emotional_triggers": ["Estar à frente", "Simplicidade", "Poder"],
                "target_pain_points": ["Tecnologia ultrapassada", "Complexidade"],
                "value_propositions": ["Tecnologia de ponta acessível", "Facilita sua vida"],
                "recommended_cta": "Adquira já e entre no futuro"
            },
            ProductCategory.FASHION: {
                "selling_points": ["Estilo único", "Qualidade premium", "Tendência atual"],
                "effective_hooks": ["Vista-se como nunca antes", "Destaque-se na multidão"],
                "emotional_triggers": ["Confiança", "Beleza", "Exclusividade"],
                "target_pain_points": ["Roupas sem personalidade", "Baixa qualidade"],
                "value_propositions": ["Estilo que define você", "Qualidade que dura"],
                "recommended_cta": "Vista sua melhor versão hoje"
            },
            ProductCategory.FOOD: {
                "selling_points": ["Sabor incomparável", "Ingredientes selecionados", "Experiência única"],
                "effective_hooks": ["Prepare-se para uma explosão de sabor", "Você nunca provou nada assim"],
                "emotional_triggers": ["Prazer", "Nostalgia", "Indulgência"],
                "target_pain_points": ["Comida sem graça", "Baixa qualidade"],
                "value_propositions": ["Sabor autêntico", "Qualidade garantida"],
                "recommended_cta": "Prove agora e se surpreenda"
            },
            ProductCategory.BEAUTY: {
                "selling_points": ["Resultados visíveis", "Ingredientes naturais", "Dermatologicamente testado"],
                "effective_hooks": ["Revele sua beleza natural", "Transforme sua pele em 7 dias"],
                "emotional_triggers": ["Autoestima", "Juventude", "Confiança"],
                "target_pain_points": ["Problemas de pele", "Baixa autoestima"],
                "value_propositions": ["Beleza sem complicação", "Resultados comprovados"],
                "recommended_cta": "Comece sua transformação hoje"
            },
            ProductCategory.HOME: {
                "selling_points": ["Conforto excepcional", "Design elegante", "Durabilidade"],
                "effective_hooks": ["Transforme sua casa em um lar", "O conforto que você merece"],
                "emotional_triggers": ["Aconchego", "Orgulho", "Bem-estar"],
                "target_pain_points": ["Casa desconfortável", "Móveis sem estilo"],
                "value_propositions": ["Conforto duradouro", "Estilo atemporal"],
                "recommended_cta": "Leve para casa hoje mesmo"
            },
            ProductCategory.FITNESS: {
                "selling_points": ["Resultados rápidos", "Fácil de usar", "Comprovado cientificamente"],
                "effective_hooks": ["Alcance seu corpo dos sonhos", "30 dias para transformação"],
                "emotional_triggers": ["Superação", "Saúde", "Vitalidade"],
                "target_pain_points": ["Falta de energia", "Corpo fora de forma"],
                "value_propositions": ["Saúde ao seu alcance", "Transformação garantida"],
                "recommended_cta": "Inicie sua jornada fitness agora"
            },
            ProductCategory.SERVICES: {
                "selling_points": ["Profissionais experientes", "Rapidez", "Garantia de qualidade"],
                "effective_hooks": ["Resolva seu problema em minutos", "Especialistas à sua disposição"],
                "emotional_triggers": ["Confiança", "Segurança", "Tranquilidade"],
                "target_pain_points": ["Falta de tempo", "Serviços de baixa qualidade"],
                "value_propositions": ["Excelência em serviço", "Sua satisfação garantida"],
                "recommended_cta": "Solicite já seu orçamento"
            }
        }

        return {
            **fallback_strategies.get(category, fallback_strategies[ProductCategory.TECH]),
            "common_objections": ["Preço", "Qualidade"],
            "counter_arguments": ["Custo-benefício incomparável", "Garantia de qualidade"],
            "competitor_approaches": ["Desconto agressivo", "Foco em features"],
            "best_practices": ["Mostre benefícios reais", "Use prova social", "Crie urgência"],
            "social_proof_elements": ["Depoimentos", "Avaliações 5 estrelas"],
            "urgency_tactics": ["Oferta limitada", "Estoque baixo"],
            "pricing_psychology": "Enfatize valor, não preço",
            "ad_format_tips": ["Vídeo curto e dinâmico", "Mostre o produto em uso"],
            "cost": 0.0
        }

    def _get_ad_strategy(self, category: str) -> Dict[str, Any]:
        """
        Estratégias otimizadas para conversão de afiliados.
        Foco em nichos: Beleza, Higiene Feminina, Perfumaria, Eletrônicos.
        """
        strategies = {
            # BELEZA & COSMÉTICOS
            ProductCategory.BEAUTY: {
                'tone': 'íntimo e transformador',
                'focus': 'resultados visíveis + autoestima',
                'emotion': 'confiança e empoderamento feminino',
                'hook_style': 'problema de beleza + solução imediata',
                'cta_style': 'Garanta o seu com desconto',
                'urgency': 'Estoque limitado - aproveite hoje',
                'social_proof': 'Mais de 10.000 mulheres já transformaram sua pele'
            },
            ProductCategory.SKINCARE: {
                'tone': 'científico mas acessível',
                'focus': 'ingredientes + resultados em X dias',
                'emotion': 'juventude e cuidado pessoal',
                'hook_style': 'revele sua melhor pele em 7 dias',
                'cta_style': 'Experimente com garantia de 30 dias',
                'urgency': 'Oferta especial termina em breve',
                'social_proof': 'Dermatologicamente testado - 98% de aprovação'
            },
            ProductCategory.HAIRCARE: {
                'tone': 'luxuoso e profissional',
                'focus': 'cabelo dos sonhos + tratamento profissional em casa',
                'emotion': 'beleza e autoconfiança',
                'hook_style': 'cabelo de salão em casa',
                'cta_style': 'Transforme seu cabelo hoje',
                'urgency': 'Promoção exclusiva - últimas unidades',
                'social_proof': 'Aprovado por cabeleireiros profissionais'
            },
            ProductCategory.MAKEUP: {
                'tone': 'moderno e fashion',
                'focus': 'look perfeito + longa duração',
                'emotion': 'destaque e glamour',
                'hook_style': 'destaque-se em qualquer ocasião',
                'cta_style': 'Arrase com essa make',
                'urgency': 'Novo lançamento - garanta já',
                'social_proof': 'Favorito das influencers de beleza'
            },

            # HIGIENE FEMININA
            ProductCategory.FEMININE_HYGIENE: {
                'tone': 'discreto e empoderador',
                'focus': 'conforto + proteção + confiança',
                'emotion': 'liberdade e bem-estar',
                'hook_style': 'viva sem preocupações todos os dias',
                'cta_style': 'Experimente o melhor para você',
                'urgency': 'Kit promocional - economize 30%',
                'social_proof': 'Recomendado por ginecologistas'
            },

            # PERFUMARIA
            ProductCategory.PERFUMES: {
                'tone': 'sofisticado e sedutor',
                'focus': 'essência única + longa duração',
                'emotion': 'elegância e sedução',
                'hook_style': 'deixe sua marca por onde passar',
                'cta_style': 'Descubra sua fragrância perfeita',
                'urgency': 'Edição limitada - não perca',
                'social_proof': 'Fragrância mais vendida do ano'
            },

            # ELETRÔNICOS
            ProductCategory.ELECTRONICS: {
                'tone': 'inovador mas descomplicado',
                'focus': 'tecnologia + facilidade de uso + custo-benefício',
                'emotion': 'praticidade e modernidade',
                'hook_style': 'facilite sua vida com tecnologia',
                'cta_style': 'Compre agora com frete grátis',
                'urgency': 'Black Friday antecipada - só hoje',
                'social_proof': '5.000+ avaliações 5 estrelas'
            },
            ProductCategory.GADGETS: {
                'tone': 'entusiasta e prático',
                'focus': 'inovação + resolver problemas do dia a dia',
                'emotion': 'curiosidade e satisfação',
                'hook_style': 'o gadget que você não sabia que precisava',
                'cta_style': 'Garanta o seu antes que acabe',
                'urgency': 'Estoque reduzido - últimas unidades',
                'social_proof': 'Tendência viral - visto na TV'
            },
            ProductCategory.HOME_ELECTRONICS: {
                'tone': 'familiar e confiável',
                'focus': 'casa inteligente + economia de tempo',
                'emotion': 'conforto e praticidade',
                'hook_style': 'transforme sua casa em um lar inteligente',
                'cta_style': 'Leve para casa com desconto',
                'urgency': 'Oferta especial - parcele sem juros',
                'social_proof': 'Mais de 50.000 lares já transformados'
            },

            ProductCategory.GENERIC: {
                'tone': 'conversacional e direto',
                'focus': 'benefício principal + valor',
                'emotion': 'satisfação e confiança',
                'hook_style': 'solução para seu problema',
                'cta_style': 'Aproveite essa oferta',
                'urgency': 'Promoção por tempo limitado',
                'social_proof': 'Milhares de clientes satisfeitos'
            }
        }

        return strategies.get(category, strategies[ProductCategory.GENERIC])

    async def _generate_ad_copy(
        self,
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        strategy: Dict[str, Any],
        market_research: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera copy persuasivo para o anúncio otimizado com insights de mercado.
        """
        self.logger.info("✍️ Generating ad copy with market insights...")

        # Construir contexto
        usps = product_info.get('unique_selling_points', [])
        if isinstance(usps, list):
            usps_text = '\n'.join(f"- {usp}" for usp in usps)
        else:
            usps_text = usps

        # Preparar insights de mercado
        selling_points = '\n'.join(f"- {sp}" for sp in market_research.get('selling_points', [])[:5])
        effective_hooks = '\n'.join(f"- {h}" for h in market_research.get('effective_hooks', [])[:3])
        emotional_triggers = ', '.join(market_research.get('emotional_triggers', [])[:3])
        pain_points = '\n'.join(f"- {pp}" for pp in market_research.get('target_pain_points', [])[:3])
        value_props = '\n'.join(f"- {vp}" for vp in market_research.get('value_propositions', [])[:3])

        prompt = f"""
Você é um copywriter especialista em anúncios de produtos com base em pesquisa de mercado.

PRODUTO:
- Nome: {product_info.get('name')}
- Descrição: {product_info.get('description', 'Não fornecida')}
- Preço: {product_info.get('price', 'Consulte')}
- Público-alvo: {product_info.get('target_audience') or analysis.get('target_audience')}

ANÁLISE VISUAL:
- Características: {', '.join(analysis.get('visual_features', []))}
- Pontos de venda: {', '.join(analysis.get('visual_selling_points', []))}
- Emoção evocada: {analysis.get('emotion')}
- Percepção de qualidade: {analysis.get('quality_perception')}

DIFERENCIAIS DO PRODUTO:
{usps_text}

PESQUISA DE MERCADO - INSIGHTS COMPROVADOS:

Pontos de Venda Eficazes:
{selling_points}

Hooks que Funcionam:
{effective_hooks}

Gatilhos Emocionais: {emotional_triggers}

Dores do Cliente:
{pain_points}

Propostas de Valor:
{value_props}

CTA Recomendado: {market_research.get('recommended_cta', 'Adquira agora')}

ESTRATÉGIA DE CONVERSÃO (AFILIADOS):
- Tom: {strategy['tone']}
- Foco: {strategy['focus']}
- Emoção: {strategy['emotion']}
- Estilo de hook: {strategy['hook_style']}
- CTA padrão: {strategy['cta_style']}
- Urgência: {strategy.get('urgency', 'Oferta limitada')}
- Prova social: {strategy.get('social_proof', 'Milhares de clientes satisfeitos')}

Crie um script de anúncio de 30 segundos OTIMIZADO PARA CONVERSÃO DE AFILIADOS:

1. **HOOK** (3s): Capte atenção imediata com problema/desejo do cliente
2. **APRESENTAÇÃO** (15s): Mostre o produto como solução definitiva + prova social
3. **BENEFÍCIOS** (10s): 2-3 benefícios que resolvam dores + gatilhos emocionais
4. **CTA + URGÊNCIA** (2s): CTA claro + elemento de urgência/escassez

ELEMENTOS OBRIGATÓRIOS PARA AFILIADOS:
✅ Mencione garantia/teste sem risco (se aplicável)
✅ Crie senso de urgência (estoque limitado, oferta temporária)
✅ Use prova social (avaliações, número de clientes)
✅ Benefícios > Features
✅ Link para compra mencionado naturalmente no final

REGRAS:
- Linguagem natural e conversacional
- Gatilhos emocionais sutis mas eficazes
- Foque em transformação/resultado
- Tom {strategy['tone']}
- Máximo 150 palavras
- IMPORTANTE: Mencione "link na descrição" ou "clique no link" no final

Responda em JSON:
{{
    "hook": "frase de hook impactante",
    "presentation": "texto da apresentação com prova social",
    "benefits": ["benefício 1", "benefício 2", "benefício 3"],
    "cta": "call to action com urgência",
    "urgency_element": "elemento de escassez usado",
    "social_proof_used": "prova social mencionada",
    "script": "script completo em parágrafo único para ser falado pelo avatar",
    "on_screen_text": {{
        "hook_text": "texto para aparecer na tela durante hook",
        "price_text": "texto de preço/oferta (se aplicável)",
        "cta_text": "texto para botão/tela final"
    }}
}}
"""

        try:
            response = await self.llm.generate(prompt)

            # Parse JSON
            import json
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]

            ad_copy = json.loads(response.strip())
            ad_copy['cost'] = 0.001

            self.logger.info(f"✅ Ad copy generated: {len(ad_copy['script'])} chars")
            return ad_copy

        except Exception as e:
            self.logger.error(f"Error generating copy: {e}")
            # Fallback copy
            return {
                'hook': f"Conheça {product_info.get('name')}!",
                'presentation': f"{product_info.get('description', 'Um produto incrível')}",
                'benefits': ['Alta qualidade', 'Preço justo', 'Entrega rápida'],
                'cta': 'Adquira já o seu!',
                'script': f"Conheça {product_info.get('name')}! {product_info.get('description', 'Um produto incrível')}. Alta qualidade, preço justo e entrega rápida. Adquira já o seu!",
                'cost': 0.0
            }

    async def _generate_avatar_presentation(
        self,
        script: str
    ) -> Dict[str, Any]:
        """
        Gera vídeo com avatar apresentando o produto.
        """
        self.logger.info("🎭 Generating avatar presentation...")

        if not self.heygen_key:
            self.logger.warning("HeyGen API key not configured")
            return {
                'path': None,
                'cost': 0.0,
                'duration': 0
            }

        try:
            # Create HeyGen video
            response = await self.client.post(
                "https://api.heygen.com/v2/video/generate",
                headers={
                    "X-Api-Key": self.heygen_key,
                    "Content-Type": "application/json"
                },
                json={
                    "video_inputs": [{
                        "character": {
                            "type": "avatar",
                            "avatar_id": "default",  # ou avatar específico
                            "avatar_style": "normal"
                        },
                        "voice": {
                            "type": "text",
                            "input_text": script,
                            "voice_id": "pt-BR-AntonioNeural"  # Voz masculina profissional
                        },
                        "background": {
                            "type": "color",
                            "value": "#FFFFFF"  # Fundo branco/neutro
                        }
                    }],
                    "dimension": {
                        "width": 1920,
                        "height": 1080
                    },
                    "aspect_ratio": "16:9"
                }
            )

            video_id = response.json()["data"]["video_id"]
            self.logger.info(f"📹 HeyGen video ID: {video_id}")

            # Poll for completion
            for attempt in range(180):  # Max 6 minutes
                await asyncio.sleep(2)

                status_response = await self.client.get(
                    f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
                    headers={"X-Api-Key": self.heygen_key}
                )

                status_data = status_response.json()["data"]

                if status_data["status"] == "completed":
                    # Download video
                    video_url = status_data["video_url"]
                    video_response = await self.client.get(video_url)

                    video_path = self.output_dir / f"avatar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                    with open(video_path, "wb") as f:
                        f.write(video_response.content)

                    duration = status_data.get("duration", 30)
                    cost = (duration / 60) * 0.096  # $0.096 per minute

                    self.logger.info(f"✅ Avatar video ready: {video_path}")
                    return {
                        'path': str(video_path),
                        'cost': cost,
                        'duration': duration
                    }

                elif status_data["status"] == "failed":
                    raise Exception(f"HeyGen failed: {status_data.get('error')}")

            raise TimeoutError("HeyGen generation timeout")

        except Exception as e:
            self.logger.error(f"Error generating avatar: {e}")
            return {
                'path': None,
                'cost': 0.0,
                'duration': 0
            }

    async def _generate_backgrounds(
        self,
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        category: str
    ) -> List[Dict[str, Any]]:
        """
        Gera backgrounds contextuais para o anúncio.
        """
        self.logger.info("🎨 Generating backgrounds...")

        if not self.fal_key:
            self.logger.warning("Fal.ai API key not configured")
            return []

        # Definir prompts baseados na categoria e análise
        background_prompts = self._get_background_prompts(
            product_info,
            analysis,
            category
        )

        backgrounds = []

        for i, prompt in enumerate(background_prompts[:3]):  # Max 3 backgrounds
            try:
                response = await self.client.post(
                    "https://fal.run/fal-ai/flux-pro",
                    headers={
                        "Authorization": f"Key {self.fal_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": prompt,
                        "image_size": "landscape_16_9",
                        "num_inference_steps": 28,
                        "guidance_scale": 3.5
                    }
                )

                result = response.json()
                image_url = result["images"][0]["url"]

                # Download image
                img_response = await self.client.get(image_url)
                image_path = self.output_dir / f"bg_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

                with open(image_path, "wb") as f:
                    f.write(img_response.content)

                backgrounds.append({
                    'path': str(image_path),
                    'prompt': prompt,
                    'cost': 0.03
                })

                self.logger.info(f"✅ Background {i+1}/3 generated")

            except Exception as e:
                self.logger.error(f"Error generating background {i}: {e}")

        return backgrounds

    def _get_background_prompts(
        self,
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        category: str
    ) -> List[str]:
        """
        Retorna prompts para backgrounds baseados no contexto.
        """
        use_case = analysis.get('use_case', 'uso moderno')
        emotion = analysis.get('emotion', 'confiança')

        category_contexts = {
            ProductCategory.TECH: [
                f"modern tech workspace, minimalist, {emotion}, professional lighting",
                "futuristic technology background, clean, innovation",
                "abstract digital patterns, blue and white tones"
            ],
            ProductCategory.FASHION: [
                f"elegant fashion background, {emotion}, luxury feel",
                "modern boutique interior, soft lighting",
                "abstract fabric textures, premium quality"
            ],
            ProductCategory.FOOD: [
                f"gourmet kitchen background, {emotion}, appetizing",
                "rustic food photography setup, natural lighting",
                "fresh ingredients backdrop, vibrant colors"
            ],
            ProductCategory.BEAUTY: [
                f"spa-like beauty environment, {emotion}, clean aesthetic",
                "modern bathroom vanity, soft lighting",
                "abstract beauty patterns, pastel tones"
            ],
            ProductCategory.HOME: [
                f"cozy home interior, {emotion}, warm lighting",
                "modern living room, comfortable atmosphere",
                "home decoration backdrop, inviting"
            ],
            ProductCategory.FITNESS: [
                f"modern gym environment, {emotion}, energetic",
                "outdoor fitness setting, motivational",
                "abstract active lifestyle, dynamic composition"
            ],
            ProductCategory.SERVICES: [
                f"professional office background, {emotion}, trustworthy",
                "modern business environment, clean",
                "abstract service concept, professional"
            ],
            ProductCategory.GENERIC: [
                f"modern commercial background, {emotion}, professional",
                "clean product showcase environment",
                "abstract elegant patterns, neutral tones"
            ]
        }

        return category_contexts.get(category, category_contexts[ProductCategory.GENERIC])

    async def _compose_final_ad(
        self,
        avatar_video_path: Optional[str],
        product_image_path: str,
        backgrounds: List[Dict[str, Any]],
        ad_copy: Dict[str, Any],
        aspect_ratio: str = "16:9"  # "16:9", "9:16", "1:1"
    ) -> str:
        """
        Compõe vídeo final do anúncio usando FFmpeg.

        Estrutura (30s):
        - 0-3s: Hook com produto em destaque + texto overlay
        - 3-18s: Avatar apresentando produto
        - 18-28s: Produto + benefícios em lista
        - 28-30s: CTA com urgência

        Formatos suportados:
        - 16:9 (1920x1080) - YouTube, Facebook
        - 9:16 (1080x1920) - Stories, Reels, TikTok
        - 1:1 (1080x1080) - Instagram Feed
        """
        self.logger.info(f"🎬 Composing final ad in {aspect_ratio} format...")

        output_path = self.output_dir / f"ad_{aspect_ratio.replace(':', 'x')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # Dimensões por aspect ratio
        dimensions = {
            "16:9": {"width": 1920, "height": 1080},
            "9:16": {"width": 1080, "height": 1920},
            "1:1": {"width": 1080, "height": 1080}
        }

        dim = dimensions.get(aspect_ratio, dimensions["16:9"])
        width, height = dim["width"], dim["height"]

        try:
            # Extrair textos do ad_copy
            on_screen = ad_copy.get('on_screen_text', {})
            hook_text = on_screen.get('hook_text', ad_copy.get('hook', ''))
            price_text = on_screen.get('price_text', '')
            cta_text = on_screen.get('cta_text', ad_copy.get('cta', ''))
            benefits = ad_copy.get('benefits', [])

            # Criar vídeo em etapas com FFmpeg

            # ETAPA 1: Hook (0-3s) - Produto em destaque com texto
            hook_segment = await self._create_hook_segment(
                product_image_path,
                hook_text,
                width,
                height,
                duration=3
            )

            # ETAPA 2: Avatar apresentando (3-18s)
            # Se avatar_video_path existe, usa ele. Senão, usa imagem do produto com narração
            if avatar_video_path and Path(avatar_video_path).exists():
                avatar_segment = avatar_video_path
            else:
                # Fallback: produto estático durante apresentação
                avatar_segment = await self._create_static_segment(
                    product_image_path,
                    width,
                    height,
                    duration=15
                )

            # ETAPA 3: Benefícios (18-28s) - Lista de benefícios com produto
            benefits_segment = await self._create_benefits_segment(
                product_image_path,
                benefits,
                width,
                height,
                duration=10
            )

            # ETAPA 4: CTA (28-30s) - Call-to-action com urgência
            cta_segment = await self._create_cta_segment(
                product_image_path,
                cta_text,
                price_text,
                width,
                height,
                duration=2
            )

            # CONCATENAR TODOS OS SEGMENTOS
            segments_file = self.output_dir / f"segments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            with open(segments_file, 'w') as f:
                f.write(f"file '{hook_segment}'\n")
                f.write(f"file '{avatar_segment}'\n")
                f.write(f"file '{benefits_segment}'\n")
                f.write(f"file '{cta_segment}'\n")

            # Concatenar com FFmpeg
            concat_cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(segments_file),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', '128k',
                str(output_path)
            ]

            import subprocess
            result = subprocess.run(concat_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"FFmpeg error: {result.stderr}")
                # Fallback: retorna avatar se existir
                return avatar_video_path if avatar_video_path else product_image_path

            # Limpar arquivos temporários
            Path(hook_segment).unlink(missing_ok=True)
            if not avatar_video_path or avatar_segment != avatar_video_path:
                Path(avatar_segment).unlink(missing_ok=True)
            Path(benefits_segment).unlink(missing_ok=True)
            Path(cta_segment).unlink(missing_ok=True)
            Path(segments_file).unlink(missing_ok=True)

            self.logger.info(f"✅ Ad composed successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"❌ Error composing ad: {e}")
            # Fallback: retorna avatar ou imagem
            return avatar_video_path if (avatar_video_path and Path(avatar_video_path).exists()) else product_image_path

    async def _create_hook_segment(
        self,
        product_image_path: str,
        hook_text: str,
        width: int,
        height: int,
        duration: int = 3
    ) -> str:
        """Cria segmento de hook com produto e texto chamativo"""
        output = self.output_dir / f"hook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # Escapar texto para FFmpeg
        hook_escaped = hook_text.replace("'", "'\\''").replace(":", "\\:")

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', product_image_path,
            '-f', 'lavfi', '-i', f'color=c=black:s={width}x{height}',
            '-filter_complex',
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,zoompan=z='min(zoom+0.001,1.5)':d={duration*25}:s={width}x{height}[v];"
            f"[v]drawtext=text='{hook_escaped}':fontsize=80:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-150[vout]",
            '-map', '[vout]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            str(output)
        ]

        import subprocess
        subprocess.run(cmd, capture_output=True)
        return str(output)

    async def _create_static_segment(
        self,
        image_path: str,
        width: int,
        height: int,
        duration: int = 15
    ) -> str:
        """Cria segmento estático com imagem do produto"""
        output = self.output_dir / f"static_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-filter_complex',
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2[vout]",
            '-map', '[vout]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            str(output)
        ]

        import subprocess
        subprocess.run(cmd, capture_output=True)
        return str(output)

    async def _create_benefits_segment(
        self,
        product_image_path: str,
        benefits: List[str],
        width: int,
        height: int,
        duration: int = 10
    ) -> str:
        """Cria segmento com lista de benefícios"""
        output = self.output_dir / f"benefits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # Criar texto de benefícios com checkmarks
        benefits_text = "\\n".join([f"✓ {b}" for b in benefits[:3]])
        benefits_escaped = benefits_text.replace("'", "'\\''").replace(":", "\\:")

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', product_image_path,
            '-filter_complex',
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,boxblur=10[bg];"
            f"[0:v]scale={int(width*0.4)}:-1[prod];"
            f"[bg][prod]overlay=(main_w-overlay_w)/2:100[v];"
            f"[v]drawbox=x=50:y=(h-400):w=(w-100):h=350:color=black@0.7:t=fill[v2];"
            f"[v2]drawtext=text='{benefits_escaped}':fontsize=50:fontcolor=white:x=100:y=(h-350)[vout]",
            '-map', '[vout]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            str(output)
        ]

        import subprocess
        subprocess.run(cmd, capture_output=True)
        return str(output)

    async def _create_cta_segment(
        self,
        product_image_path: str,
        cta_text: str,
        price_text: str,
        width: int,
        height: int,
        duration: int = 2
    ) -> str:
        """Cria segmento de CTA com urgência"""
        output = self.output_dir / f"cta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        cta_escaped = cta_text.replace("'", "'\\''").replace(":", "\\:")
        price_escaped = price_text.replace("'", "'\\''").replace(":", "\\:") if price_text else ""

        # CTA com produto e botão
        drawtext_filter = f"drawtext=text='{cta_escaped}':fontsize=70:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-250"

        if price_escaped:
            drawtext_filter += f":drawtext=text='{price_escaped}':fontsize=50:fontcolor=#FFD700:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-150"

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', product_image_path,
            '-filter_complex',
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2[v];"
            f"[v]{drawtext_filter}[vout]",
            '-map', '[vout]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            str(output)
        ]

        import subprocess
        subprocess.run(cmd, capture_output=True)
        return str(output)

    async def close(self):
        """Cleanup"""
        await self.client.aclose()
