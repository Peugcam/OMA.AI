"""
Response Validators - Validação e Parsing de Respostas de IA

Valida e faz parsing de respostas de modelos de IA,
com tratamento robusto de erros e extração de dados estruturados.
"""

import json
import re
from typing import Any, Optional


class ResponseValidator:
    """
    Validadores reutilizáveis para respostas de modelos de IA.

    Fornece métodos para:
    - Parse de JSON (com fallbacks)
    - Extração de JSON de texto misto
    - Validação de nomes de agentes
    - Limpeza de respostas
    """

    # Agentes válidos no sistema
    VALID_AGENTS = ["script_agent", "visual_agent", "audio_agent", "editor_agent", "FINISH"]

    @staticmethod
    def parse_json(response: str, default: Optional[dict] = None) -> dict:
        """
        Faz parse de JSON, retornando default se falhar.

        Args:
            response: String JSON
            default: Valor padrão se parse falhar

        Returns:
            Dict parseado ou default

        Exemplo:
            result = ResponseValidator.parse_json('{"key": "value"}')
            # {"key": "value"}

            result = ResponseValidator.parse_json('invalid', default={})
            # {}
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON inválido: {e}")
            print(f"       Resposta: {response[:100]}...")
            return default or {}

    @staticmethod
    def extract_first_json(text: str) -> Optional[dict]:
        """
        Extrai primeiro JSON válido de um texto.

        Útil quando o modelo adiciona texto explicativo antes/depois do JSON.

        Args:
            text: Texto contendo JSON

        Returns:
            Dict com JSON ou None se não encontrado

        Exemplo:
            text = "Aqui está o resultado: {\"a\": 1} e mais texto"
            result = ResponseValidator.extract_first_json(text)
            # {"a": 1}
        """
        # Procurar primeiro { e último }
        start = text.find('{')
        end = text.rfind('}') + 1

        if start != -1 and end > start:
            json_candidate = text[start:end]
            try:
                return json.loads(json_candidate)
            except json.JSONDecodeError:
                # Se falhar, tentar com regex para encontrar JSON aninhado
                pass

        # Fallback: procurar padrão de JSON com regex
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text)

        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        return None

    @staticmethod
    def extract_json_array(text: str) -> Optional[list]:
        """
        Extrai primeiro array JSON válido de um texto.

        Args:
            text: Texto contendo array JSON

        Returns:
            List com array ou None

        Exemplo:
            text = "Keywords: [\"a\", \"b\", \"c\"]"
            result = ResponseValidator.extract_json_array(text)
            # ["a", "b", "c"]
        """
        # Procurar primeiro [ e último ]
        start = text.find('[')
        end = text.rfind(']') + 1

        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        return None

    @staticmethod
    def validate_agent_name(agent: str) -> bool:
        """
        Valida se o nome do agente é válido.

        Args:
            agent: Nome do agente

        Returns:
            True se válido, False caso contrário

        Exemplo:
            ResponseValidator.validate_agent_name("script_agent")  # True
            ResponseValidator.validate_agent_name("invalid")       # False
        """
        return agent in ResponseValidator.VALID_AGENTS

    @staticmethod
    def clean_agent_name(response: str) -> str:
        """
        Limpa resposta de roteamento, extraindo nome do agente.

        Remove espaços, quebras de linha, e texto adicional.

        Args:
            response: Resposta bruta do modelo

        Returns:
            Nome do agente limpo

        Exemplo:
            ResponseValidator.clean_agent_name("  script_agent\\n")
            # "script_agent"

            ResponseValidator.clean_agent_name("O próximo é: visual_agent")
            # "visual_agent"
        """
        # Remover espaços e quebras de linha
        cleaned = response.strip().lower()

        # Procurar nome de agente válido na resposta
        for agent in ResponseValidator.VALID_AGENTS:
            if agent.lower() in cleaned:
                return agent

        # Se não encontrado, retornar original limpo
        return cleaned

    @staticmethod
    def validate_json_schema(data: dict, required_keys: list[str]) -> tuple[bool, list[str]]:
        """
        Valida se um JSON contém todas as chaves obrigatórias.

        Args:
            data: Dict para validar
            required_keys: Lista de chaves obrigatórias

        Returns:
            Tupla (is_valid, missing_keys)

        Exemplo:
            data = {"a": 1, "b": 2}
            valid, missing = ResponseValidator.validate_json_schema(data, ["a", "b", "c"])
            # (False, ["c"])
        """
        missing = [key for key in required_keys if key not in data]
        return (len(missing) == 0, missing)

    @staticmethod
    def extract_code_block(text: str, language: str = "") -> Optional[str]:
        """
        Extrai bloco de código de markdown.

        Args:
            text: Texto contendo código markdown
            language: Linguagem do código (opcional)

        Returns:
            String com código ou None

        Exemplo:
            text = "```python\\nprint('hello')\\n```"
            code = ResponseValidator.extract_code_block(text, "python")
            # "print('hello')"
        """
        # Padrão: ```language\ncode\n```
        if language:
            pattern = f"```{language}\\s*\\n(.*?)\\n```"
        else:
            pattern = r"```\w*\s*\n(.*?)\n```"

        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def sanitize_filename(name: str, max_length: int = 255) -> str:
        """
        Sanitiza string para ser usada como nome de arquivo.

        Remove caracteres inválidos e limita tamanho.

        Args:
            name: Nome original
            max_length: Tamanho máximo

        Returns:
            Nome sanitizado

        Exemplo:
            ResponseValidator.sanitize_filename("Vídeo: teste/novo?.mp4")
            # "Video_teste_novo.mp4"
        """
        # Remover caracteres inválidos
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)

        # Remover espaços múltiplos
        sanitized = re.sub(r'\s+', '_', sanitized)

        # Limitar tamanho
        if len(sanitized) > max_length:
            # Manter extensão se houver
            parts = sanitized.rsplit('.', 1)
            if len(parts) == 2:
                name_part, ext = parts
                max_name = max_length - len(ext) - 1
                sanitized = f"{name_part[:max_name]}.{ext}"
            else:
                sanitized = sanitized[:max_length]

        return sanitized


class VideoStateValidator:
    """
    Validador específico para VideoState (estado do LangGraph).

    Garante que o estado tenha estrutura correta em cada fase.
    """

    @staticmethod
    def validate_phase(state: dict, expected_phase: int) -> tuple[bool, str]:
        """
        Valida se estado está na fase esperada.

        Args:
            state: Estado atual
            expected_phase: Fase esperada (0-4)

        Returns:
            Tupla (is_valid, error_message)
        """
        current_phase = state.get('current_phase', -1)

        if current_phase != expected_phase:
            return (
                False,
                f"Fase inválida: esperado {expected_phase}, atual {current_phase}"
            )

        return (True, "")

    @staticmethod
    def validate_script(script: dict) -> tuple[bool, str]:
        """
        Valida estrutura do script.

        Args:
            script: Dict com script

        Returns:
            Tupla (is_valid, error_message)
        """
        required = ["script_id", "scenes", "duration_seconds"]

        valid, missing = ResponseValidator.validate_json_schema(script, required)
        if not valid:
            return (False, f"Script inválido: faltando {missing}")

        # Validar cenas
        scenes = script.get('scenes', [])
        if not scenes or len(scenes) == 0:
            return (False, "Script sem cenas")

        # Validar cada cena
        scene_required = ["scene_number", "visual_description", "duration"]
        for i, scene in enumerate(scenes):
            valid, missing = ResponseValidator.validate_json_schema(scene, scene_required)
            if not valid:
                return (False, f"Cena {i+1} inválida: faltando {missing}")

        return (True, "")

    @staticmethod
    def validate_visual_plan(visual_plan: dict) -> tuple[bool, str]:
        """
        Valida estrutura do plano visual.

        Args:
            visual_plan: Dict com plano visual

        Returns:
            Tupla (is_valid, error_message)
        """
        required = ["visual_plan_id", "scenes"]

        valid, missing = ResponseValidator.validate_json_schema(visual_plan, required)
        if not valid:
            return (False, f"Plano visual inválido: faltando {missing}")

        scenes = visual_plan.get('scenes', [])
        if not scenes:
            return (False, "Plano visual sem cenas")

        return (True, "")

    @staticmethod
    def validate_audio_files(audio_files: dict) -> tuple[bool, str]:
        """
        Valida estrutura dos arquivos de áudio.

        Args:
            audio_files: Dict com arquivos de áudio

        Returns:
            Tupla (is_valid, error_message)
        """
        required = ["audio_production_id", "final_mix"]

        valid, missing = ResponseValidator.validate_json_schema(audio_files, required)
        if not valid:
            return (False, f"Áudio inválido: faltando {missing}")

        final_mix = audio_files.get('final_mix', {})
        if not final_mix.get('file_path'):
            return (False, "Áudio sem arquivo final")

        return (True, "")


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("🧪 Testando ResponseValidator...\n")

    # Teste 1: Parse JSON
    print("TESTE 1: Parse JSON")
    print("-" * 40)

    valid_json = '{"name": "teste", "value": 123}'
    result = ResponseValidator.parse_json(valid_json)
    print(f"✅ JSON válido: {result}")

    invalid_json = '{invalid json'
    result = ResponseValidator.parse_json(invalid_json, default={"error": True})
    print(f"✅ JSON inválido (com default): {result}")

    # Teste 2: Extrair JSON de texto
    print("\nTESTE 2: Extrair JSON de texto misto")
    print("-" * 40)

    mixed_text = 'Aqui está o resultado: {"status": "ok", "count": 5} e mais texto'
    result = ResponseValidator.extract_first_json(mixed_text)
    print(f"✅ JSON extraído: {result}")

    # Teste 3: Validar nome de agente
    print("\nTESTE 3: Validar nome de agente")
    print("-" * 40)

    print(f"✅ 'script_agent' válido? {ResponseValidator.validate_agent_name('script_agent')}")
    print(f"✅ 'invalid_agent' válido? {ResponseValidator.validate_agent_name('invalid_agent')}")

    # Teste 4: Limpar nome de agente
    print("\nTESTE 4: Limpar nome de agente")
    print("-" * 40)

    dirty_names = [
        "  visual_agent\\n",
        "O próximo é: audio_agent",
        "FINISH"
    ]

    for dirty in dirty_names:
        clean = ResponseValidator.clean_agent_name(dirty)
        print(f"✅ '{dirty}' → '{clean}'")

    # Teste 5: Extrair array JSON
    print("\nTESTE 5: Extrair array JSON")
    print("-" * 40)

    array_text = 'Keywords: ["coffee", "barista", "latte"]'
    result = ResponseValidator.extract_json_array(array_text)
    print(f"✅ Array extraído: {result}")

    # Teste 6: Validar schema JSON
    print("\nTESTE 6: Validar schema JSON")
    print("-" * 40)

    data = {"a": 1, "b": 2}
    valid, missing = ResponseValidator.validate_json_schema(data, ["a", "b", "c"])
    print(f"✅ Válido? {valid}, Faltando: {missing}")

    # Teste 7: Sanitizar filename
    print("\nTESTE 7: Sanitizar filename")
    print("-" * 40)

    dirty_filename = "Vídeo: teste/novo?.mp4"
    clean_filename = ResponseValidator.sanitize_filename(dirty_filename)
    print(f"✅ '{dirty_filename}' → '{clean_filename}'")

    print("\n✅ Todos os testes concluídos!")
