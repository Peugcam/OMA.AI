"""
Scene Classifier - Classificacao Inteligente em 3 Niveis

Decide qual ferramenta usar (Pexels, Stability, ou ambos) de forma eficiente:
1. Nivel 1: Keywords deterministicas (sem LLM, instantaneo)
2. Nivel 2: Decisao "both" para cenas hibridas
3. Nivel 3: Tool calling MCP (LLM decide automaticamente)

Otimizacoes:
- 80% das cenas decididas no Nivel 1 (custo zero)
- 15% decididas no Nivel 2 (custo zero)
- 5% precisam de LLM (Nivel 3)
"""

import logging
from typing import Literal, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


# Tipo de classificacao
ClassificationType = Literal["pexels", "stability", "both", "unknown"]


@dataclass
class ClassificationResult:
    """Resultado da classificacao de cena"""
    tool: ClassificationType
    confidence: float  # 0.0 a 1.0
    level: int  # 1, 2 ou 3 (qual nivel decidiu)
    reason: str
    matched_keywords: list = field(default_factory=list)

    def __post_init__(self):
        # Validar confidence
        self.confidence = max(0.0, min(1.0, self.confidence))


class SceneClassifier:
    """
    Classificador inteligente de cenas para Visual Agent.

    Decide entre Pexels (video real), Stability (imagem gerada),
    ou Both (video + overlay de imagem) de forma eficiente.

    3 Niveis de Decisao:
    - Nivel 1: Keywords deterministicas (instantaneo, gratuito)
    - Nivel 2: Deteccao de cenas hibridas (instantaneo, gratuito)
    - Nivel 3: Tool calling MCP (usa LLM, pago)

    Performance esperada:
    - 80% decidido no Nivel 1
    - 15% decidido no Nivel 2
    - 5% precisa do Nivel 3
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # Keywords que SEMPRE indicam PESSOAS (Pexels obrigatorio)
        self.people_keywords = {
            # Pessoas diretamente
            'pessoa', 'pessoas', 'humano', 'humanos', 'gente',
            'homem', 'mulher', 'jovem', 'adulto', 'crianca', 'idoso',

            # Partes do corpo (Stability gera deformado)
            'rosto', 'rostos', 'face', 'faces', 'mao', 'maos',
            'olhos', 'olhar', 'sorriso', 'sorrindo', 'expressao',

            # Acoes humanas
            'trabalhando', 'digitando', 'escrevendo', 'lendo',
            'falando', 'conversando', 'apresentando', 'explicando',
            'ensinando', 'aprendendo', 'estudando', 'reuniao',
            'caminhando', 'correndo', 'sentado', 'sentada',
            'gesticulando', 'apontando', 'segurando',

            # Profissoes/papeis
            'professor', 'professora', 'instrutor', 'instrutora',
            'apresentador', 'apresentadora', 'palestrante',
            'estudante', 'aluno', 'aluna', 'funcionario',
            'medico', 'medica', 'enfermeiro', 'enfermeira',
            'engenheiro', 'engenheira', 'programador', 'programadora',

            # Grupos
            'equipe', 'time', 'grupo', 'familia', 'casal',
            'colegas', 'amigos', 'parceiros',

            # Interacoes
            'entrevista', 'dialogo', 'discussao', 'debate',
            'colaboracao', 'cooperacao', 'interacao',

            # Contextos educacionais (sempre tem pessoas)
            'aula', 'palestra', 'workshop', 'treinamento',
            'tutorial', 'demonstracao', 'explicacao',

            # Ingles (para briefs em ingles)
            'person', 'people', 'human', 'face', 'hand', 'hands',
            'working', 'talking', 'presenting', 'teaching',
            'team', 'group', 'meeting', 'interview'
        }

        # Keywords que indicam ABSTRATO/CONCEITUAL (Stability ideal)
        self.abstract_keywords = {
            # Logos e branding
            'logo', 'logotipo', 'marca', 'branding', 'icone',
            'simbolo', 'emblema', 'insignia',

            # Conceitos abstratos
            'abstrato', 'conceito', 'conceitual', 'metafora',
            'representacao', 'simbolico', 'alegorico',

            # Tecnologia abstrata (sem pessoas)
            'holograma', 'holografico', 'digital', 'virtual',
            'dados', 'visualizacao', 'grafico', 'diagrama',
            'particulas', 'ondas', 'energia', 'fluxo',
            'rede neural', 'inteligencia artificial', 'codigo',

            # Ambientes vazios
            'futurista', 'espacial', 'cosmico', 'galactico',
            'ambiente vazio', 'cenario abstrato', 'paisagem digital',

            # Arte
            'arte', 'artistico', 'ilustracao', 'design',
            'minimalista', 'geometrico', 'padrao',

            # Ingles
            'logo', 'hologram', 'abstract', 'concept',
            'digital', 'virtual', 'futuristic', 'particles',
            'data visualization', 'neural network'
        }

        # Keywords que indicam HIBRIDO (Pexels + Stability overlay)
        self.hybrid_indicators = {
            # Pessoa + elemento digital/grafico
            ('pessoa', 'holograma'), ('pessoa', 'digital'), ('pessoa', 'virtual'),
            ('pessoa', 'grafico'), ('pessoa', 'dados'), ('pessoa', 'logo'),
            ('trabalhando', 'dados'), ('trabalhando', 'grafico'),
            ('apresentando', 'logo'), ('apresentando', 'grafico'),
            ('apresentando', 'dados'), ('apresentando', 'resultados'),
            ('equipe', 'logo'), ('equipe', 'grafico'), ('equipe', 'dados'),
            ('reuniao', 'apresentacao'), ('reuniao', 'grafico'),

            # Ambiente real + elemento abstrato
            ('escritorio', 'holograma'), ('sala', 'digital'),
            ('mesa', 'dados'), ('tela', 'grafico'),

            # Ingles
            ('person', 'hologram'), ('team', 'logo'), ('team', 'chart'),
            ('working', 'data'), ('presenting', 'chart'), ('presenting', 'data'),

            # Combinacoes com "com" (portugues)
            ('pessoa', 'com'), ('equipe', 'com'), ('apresentando', 'com'),
        }

        # Metricas de classificacao
        self.stats = {
            "total": 0,
            "level_1": 0,
            "level_2": 0,
            "level_3": 0,
            "pexels": 0,
            "stability": 0,
            "both": 0,
            "unknown": 0
        }

        self.logger.info("SceneClassifier inicializado com 3 niveis de decisao")


    def classify(
        self,
        description: str,
        mood: str = "neutral",
        style: str = "professional"
    ) -> ClassificationResult:
        """
        Classifica cena de forma eficiente (3 niveis).

        Args:
            description: Descricao visual da cena
            mood: Mood/atmosfera (energetic, calm, professional, etc)
            style: Estilo visual (modern, tech, cinematic, etc)

        Returns:
            ClassificationResult com tool, confidence, level e reason

        Example:
            >>> classifier = SceneClassifier()
            >>> result = classifier.classify("Pessoa trabalhando no laptop")
            >>> result.tool  # "pexels"
            >>> result.level  # 1 (decidido por keywords)
        """
        self.stats["total"] += 1

        # Normalizar descricao
        desc_lower = description.lower()

        # NIVEL 2 PRIMEIRO: Deteccao de cenas hibridas (pessoas + digital)
        # Verificar hibrido ANTES de keywords simples
        result = self._level_2_hybrid(desc_lower, mood, style)
        if result.tool == "both":
            self.stats["level_2"] += 1
            self.stats[result.tool] += 1
            self.logger.info(
                f"[L2] {result.tool.upper()} (conf: {result.confidence:.0%}) - {result.reason}"
            )
            return result

        # NIVEL 1: Keywords deterministicas (pessoas OU abstratos puros)
        result = self._level_1_keywords(desc_lower)
        if result.tool != "unknown":
            self.stats["level_1"] += 1
            self.stats[result.tool] += 1
            self.logger.info(
                f"[L1] {result.tool.upper()} (conf: {result.confidence:.0%}) - {result.reason}"
            )
            return result

        # NIVEL 3: Retornar unknown (MCP decidira)
        self.stats["level_3"] += 1
        self.stats["unknown"] += 1

        result = ClassificationResult(
            tool="unknown",
            confidence=0.0,
            level=3,
            reason="Classificacao incerta, MCP decidira"
        )

        self.logger.info(
            f"[L3] UNKNOWN - MCP tool calling necessario"
        )

        return result


    def _level_1_keywords(self, desc_lower: str) -> ClassificationResult:
        """
        Nivel 1: Classificacao por keywords deterministicas.

        Mais rapido e gratuito - nao usa LLM.

        Args:
            desc_lower: Descricao em minusculas

        Returns:
            ClassificationResult (tool pode ser "unknown" se incerto)
        """
        # Verificar pessoas primeiro (prioridade maxima)
        people_matches = [kw for kw in self.people_keywords if kw in desc_lower]

        if people_matches:
            return ClassificationResult(
                tool="pexels",
                confidence=0.95,
                level=1,
                reason=f"Detectou pessoas/humanos: {people_matches[:3]}",
                matched_keywords=people_matches
            )

        # Verificar abstrato (apenas se NAO tiver pessoas)
        abstract_matches = [kw for kw in self.abstract_keywords if kw in desc_lower]

        if abstract_matches:
            # Verificar se NAO tem nenhuma pessoa mencionada
            has_people = any(pw in desc_lower for pw in ['pessoa', 'humano', 'rosto', 'mao'])

            if not has_people:
                return ClassificationResult(
                    tool="stability",
                    confidence=0.90,
                    level=1,
                    reason=f"Conteudo abstrato/conceitual: {abstract_matches[:3]}",
                    matched_keywords=abstract_matches
                )

        # Incerto - proximo nivel decidira
        return ClassificationResult(
            tool="unknown",
            confidence=0.0,
            level=1,
            reason="Nenhuma keyword deterministica encontrada"
        )


    def _level_2_hybrid(
        self,
        desc_lower: str,
        mood: str,
        style: str
    ) -> ClassificationResult:
        """
        Nivel 2: Deteccao de cenas hibridas.

        Identifica cenas que precisam de AMBOS:
        - Video Pexels de fundo
        - Overlay de imagem Stability

        Exemplo: "Pessoa apresentando grafico de dados"
        - Pexels: video de pessoa apresentando
        - Stability: grafico/dados para overlay

        Args:
            desc_lower: Descricao em minusculas
            mood: Mood
            style: Estilo

        Returns:
            ClassificationResult
        """
        # Verificar pares hibridos
        for pair in self.hybrid_indicators:
            kw1, kw2 = pair
            if kw1 in desc_lower and kw2 in desc_lower:
                return ClassificationResult(
                    tool="both",
                    confidence=0.85,
                    level=2,
                    reason=f"Cena hibrida detectada: {kw1} + {kw2}",
                    matched_keywords=[kw1, kw2]
                )

        # Verificar padroes mais complexos
        # Pessoa + tela/monitor + conteudo digital
        if any(p in desc_lower for p in ['pessoa', 'apresentando', 'mostrando']):
            if any(d in desc_lower for d in ['tela', 'monitor', 'projecao', 'slide']):
                if any(c in desc_lower for c in ['dados', 'grafico', 'logo', 'imagem']):
                    return ClassificationResult(
                        tool="both",
                        confidence=0.80,
                        level=2,
                        reason="Padrao: pessoa + tela + conteudo digital",
                        matched_keywords=['pessoa', 'tela', 'conteudo digital']
                    )

        # Verificar contexto de "com" que pode indicar hibrido
        # Ex: "Escritorio com logo flutuante"
        if ' com ' in desc_lower:
            parts = desc_lower.split(' com ')
            if len(parts) == 2:
                before, after = parts

                # Real + abstrato
                has_real = any(r in before for r in ['escritorio', 'sala', 'mesa', 'ambiente'])
                has_abstract = any(a in after for a in ['logo', 'holograma', 'digital', 'flutuante'])

                if has_real and has_abstract:
                    return ClassificationResult(
                        tool="both",
                        confidence=0.75,
                        level=2,
                        reason=f"Padrao 'real com abstrato' detectado",
                        matched_keywords=[before.strip()[:20], after.strip()[:20]]
                    )

        # Nao identificou hibrido
        return ClassificationResult(
            tool="unknown",
            confidence=0.0,
            level=2,
            reason="Nao identificou padrao hibrido"
        )


    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatisticas de classificacao.

        Returns:
            Dict com metricas de uso por nivel e ferramenta
        """
        total = self.stats["total"]

        if total == 0:
            return {**self.stats, "efficiency": 0.0}

        # Eficiencia = % decidido nos niveis 1 e 2 (sem LLM)
        no_llm = self.stats["level_1"] + self.stats["level_2"]
        efficiency = no_llm / total

        return {
            **self.stats,
            "efficiency": efficiency,
            "efficiency_pct": f"{efficiency:.1%}",
            "level_1_pct": f"{self.stats['level_1']/total:.1%}" if total > 0 else "0%",
            "level_2_pct": f"{self.stats['level_2']/total:.1%}" if total > 0 else "0%",
            "level_3_pct": f"{self.stats['level_3']/total:.1%}" if total > 0 else "0%",
        }


    def reset_stats(self):
        """Reseta estatisticas de classificacao."""
        self.stats = {
            "total": 0,
            "level_1": 0,
            "level_2": 0,
            "level_3": 0,
            "pexels": 0,
            "stability": 0,
            "both": 0,
            "unknown": 0
        }
        self.logger.info("Estatisticas resetadas")


# ============================================================================
# TESTES E EXEMPLOS
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    classifier = SceneClassifier()

    # Testes
    test_scenes = [
        # Nivel 1 - Pexels (pessoas)
        "Pessoa trabalhando no laptop em escritorio moderno",
        "Equipe discutindo projeto em reuniao",
        "Professor explicando conceito para estudantes",
        "Mulher sorrindo durante apresentacao",

        # Nivel 1 - Stability (abstrato)
        "Logo holografico flutuando no espaco",
        "Visualizacao de dados com particulas",
        "Paisagem digital futurista vazia",
        "Rede neural abstrata com conexoes",

        # Nivel 2 - Both (hibrido)
        "Pessoa apresentando grafico de dados",
        "Equipe com logo da empresa ao fundo",
        "Escritorio com holograma flutuante",
        "Apresentador mostrando slides com graficos",

        # Nivel 3 - Unknown (MCP decide)
        "Ambiente corporativo moderno",
        "Cena de inovacao tecnologica",
        "Momento de inspiracao criativa"
    ]

    print("\n" + "="*70)
    print("TESTES DO SCENE CLASSIFIER")
    print("="*70 + "\n")

    for scene in test_scenes:
        result = classifier.classify(scene)
        print(f"Cena: {scene[:50]}...")
        print(f"  -> {result.tool.upper()} (L{result.level}, {result.confidence:.0%})")
        print(f"  -> {result.reason}")
        print()

    print("\n" + "="*70)
    print("ESTATISTICAS")
    print("="*70)

    stats = classifier.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
