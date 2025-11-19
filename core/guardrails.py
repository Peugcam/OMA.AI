"""
Guardrails - Content Safety & PII Detection
100% GRATUITO - Modelos locais + Regex
Inspirado em AWS Bedrock Guardrails, Azure Content Safety
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


# ============================================================================
# PII DETECTION (Regex-based - 100% FREE)
# ============================================================================

@dataclass
class PIIMatch:
    """Match de PII encontrado"""
    type: str
    value: str
    start: int
    end: int


class PIIDetector:
    """
    Detector de PII (Personally Identifiable Information)

    Detecta:
    - CPF
    - CNPJ
    - Email
    - Telefone
    - Cartão de crédito
    - RG
    - CEP

    100% GRATUITO - Regex patterns
    """

    def __init__(self):
        self.patterns = {
            'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
            'cnpj': r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b',
            'email': r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            'phone_br': r'\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\s?)?\d{4}[\s-]?\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'rg': r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9xX]\b',
            'cep': r'\b\d{5}-?\d{3}\b'
        }

    def detect(self, text: str) -> Dict[str, List[PIIMatch]]:
        """
        Detecta PII no texto

        Args:
            text: Texto para analisar

        Returns:
            Dicionário com PIIs encontrados por tipo
        """
        results = {}

        for pii_type, pattern in self.patterns.items():
            matches = []

            for match in re.finditer(pattern, text):
                matches.append(PIIMatch(
                    type=pii_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end()
                ))

            if matches:
                results[pii_type] = matches

        return results

    def redact(self, text: str, replacement: str = "[REDACTED]") -> Tuple[str, Dict]:
        """
        Redacta PII do texto

        Args:
            text: Texto original
            replacement: String para substituir PII

        Returns:
            (texto_redactado, pii_encontrado)
        """
        pii_found = self.detect(text)
        redacted = text

        # Substituir em ordem reversa para manter índices corretos
        all_matches = []
        for pii_type, matches in pii_found.items():
            all_matches.extend(matches)

        # Ordenar por posição (reverso)
        all_matches.sort(key=lambda m: m.start, reverse=True)

        for match in all_matches:
            redacted = redacted[:match.start] + f"[{match.type.upper()}_REDACTED]" + redacted[match.end:]

        return redacted, pii_found

    def has_pii(self, text: str) -> bool:
        """Verifica se texto contém PII"""
        return len(self.detect(text)) > 0


# ============================================================================
# CONTENT SAFETY (Rule-based - 100% FREE)
# ============================================================================

class ContentSafety:
    """
    Content safety checker usando regras e patterns

    Detecta:
    - Profanidade
    - Conteúdo sexual
    - Violência
    - Discurso de ódio
    - Política (opcional)
    - Religião (opcional)

    100% GRATUITO - Pattern matching
    Similar a: AWS Bedrock Content Filters
    """

    def __init__(self):
        # Palavras bloqueadas (exemplo básico - expandir conforme necessidade)
        self.blocked_words = {
            'profanity': [
                'profanidade1', 'profanidade2',  # Adicionar palavras reais
            ],
            'sexual': [
                'sexual1', 'sexual2',  # Adicionar palavras reais
            ],
            'violence': [
                'matar', 'violência', 'arma',
            ],
            'hate_speech': [
                'discurso1', 'odio1',  # Adicionar palavras reais
            ]
        }

        # Topics bloqueados (opcional)
        self.blocked_topics = {
            'politics': ['político', 'eleição', 'partido'],
            'religion': ['religião', 'igreja', 'deus']  # Use com cuidado!
        }

    def check_content(self, text: str, block_topics: List[str] = None) -> Dict:
        """
        Verifica segurança do conteúdo

        Args:
            text: Texto para verificar
            block_topics: Lista de topics para bloquear (politics, religion)

        Returns:
            {
                'safe': bool,
                'violations': list,
                'blocked_words': list,
                'score': float  # 0.0 (unsafe) to 1.0 (safe)
            }
        """
        text_lower = text.lower()
        violations = []
        blocked_found = []

        # Check blocked words
        for category, words in self.blocked_words.items():
            for word in words:
                if word.lower() in text_lower:
                    violations.append(category)
                    blocked_found.append({'word': word, 'category': category})

        # Check blocked topics
        if block_topics:
            for topic in block_topics:
                if topic in self.blocked_topics:
                    for keyword in self.blocked_topics[topic]:
                        if keyword.lower() in text_lower:
                            violations.append(f"topic_{topic}")
                            blocked_found.append({'word': keyword, 'category': topic})

        # Calculate safety score
        violations_count = len(set(violations))
        score = max(0.0, 1.0 - (violations_count * 0.25))

        is_safe = score >= 0.7 and violations_count == 0

        return {
            'safe': is_safe,
            'violations': list(set(violations)),
            'blocked_words': blocked_found,
            'score': score
        }

    def add_blocked_word(self, word: str, category: str = 'custom'):
        """Adiciona palavra à lista de bloqueio"""
        if category not in self.blocked_words:
            self.blocked_words[category] = []

        self.blocked_words[category].append(word.lower())


# ============================================================================
# INPUT VALIDATOR
# ============================================================================

class InputValidator:
    """
    Valida inputs do usuário

    Features:
    - Length limits
    - Format validation
    - Content safety
    - PII detection
    """

    def __init__(self):
        self.pii_detector = PIIDetector()
        self.content_safety = ContentSafety()

    def validate_brief(self, brief: Dict) -> Tuple[bool, List[str]]:
        """
        Valida briefing de vídeo

        Args:
            brief: Dict com campos do briefing

        Returns:
            (is_valid, errors)
        """
        errors = []

        # Required fields
        required_fields = ['title', 'description', 'duration']
        for field in required_fields:
            if field not in brief or not brief[field]:
                errors.append(f"Campo obrigatório ausente: {field}")

        # Validate title
        if 'title' in brief:
            title = brief['title']
            if len(title) < 3:
                errors.append("Título muito curto (mínimo 3 caracteres)")
            if len(title) > 200:
                errors.append("Título muito longo (máximo 200 caracteres)")

        # Validate description
        if 'description' in brief:
            desc = brief['description']
            if len(desc) < 10:
                errors.append("Descrição muito curta (mínimo 10 caracteres)")
            if len(desc) > 5000:
                errors.append("Descrição muito longa (máximo 5000 caracteres)")

            # Check content safety
            safety_check = self.content_safety.check_content(desc)
            if not safety_check['safe']:
                errors.append(f"Conteúdo inadequado: {', '.join(safety_check['violations'])}")

            # Check for PII
            if self.pii_detector.has_pii(desc):
                errors.append("⚠️ Aviso: Detectados dados pessoais (PII) na descrição")

        # Validate duration
        if 'duration' in brief:
            duration = brief['duration']
            if not isinstance(duration, (int, float)):
                errors.append("Duração deve ser um número")
            elif duration < 5:
                errors.append("Duração muito curta (mínimo 5 segundos)")
            elif duration > 300:
                errors.append("Duração muito longa (máximo 300 segundos)")

        is_valid = len(errors) == 0

        return is_valid, errors


# ============================================================================
# GUARDRAILS MANAGER
# ============================================================================

class GuardrailsManager:
    """
    Manager centralizado para todos os guardrails

    Similar a: AWS Bedrock Guardrails Manager
    """

    def __init__(self, config: Dict = None):
        self.config = config or {
            'pii_detection': True,
            'content_safety': True,
            'pii_redaction': True,
            'block_topics': [],  # ['politics', 'religion']
            'max_text_length': 10000
        }

        self.pii_detector = PIIDetector()
        self.content_safety = ContentSafety()
        self.validator = InputValidator()

    def check_input(self, text: str) -> Dict:
        """
        Verifica input completo

        Returns:
            {
                'allowed': bool,
                'pii_detected': bool,
                'pii_found': dict,
                'content_safe': bool,
                'content_check': dict,
                'redacted_text': str (opcional)
            }
        """
        result = {
            'allowed': True,
            'pii_detected': False,
            'content_safe': True,
            'violations': []
        }

        # Check length
        if len(text) > self.config.get('max_text_length', 10000):
            result['allowed'] = False
            result['violations'].append('text_too_long')
            return result

        # PII Detection
        if self.config.get('pii_detection'):
            pii_found = self.pii_detector.detect(text)
            if pii_found:
                result['pii_detected'] = True
                result['pii_found'] = {k: [m.value for m in v] for k, v in pii_found.items()}

                # Redact if configured
                if self.config.get('pii_redaction'):
                    redacted, _ = self.pii_detector.redact(text)
                    result['redacted_text'] = redacted

        # Content Safety
        if self.config.get('content_safety'):
            safety_check = self.content_safety.check_content(
                text,
                block_topics=self.config.get('block_topics', [])
            )

            result['content_safe'] = safety_check['safe']
            result['content_check'] = safety_check

            if not safety_check['safe']:
                result['allowed'] = False
                result['violations'].extend(safety_check['violations'])

        return result

    def validate_brief(self, brief: Dict) -> Tuple[bool, List[str]]:
        """Valida briefing completo"""
        return self.validator.validate_brief(brief)


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Default guardrails instance
guardrails = GuardrailsManager()


def get_guardrails() -> GuardrailsManager:
    """Factory para obter guardrails manager"""
    return guardrails
