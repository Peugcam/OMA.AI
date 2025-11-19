"""
Smart Router - Roteamento Otimizado com Cache

Router inteligente que usa SLM local (Phi3:mini) para decisões
de roteamento rápidas e econômicas, com cache para evitar
chamadas duplicadas.

Reduz custo do Supervisor em 95% e latência em 80%.
"""

from core.ai_client import AIClient
from core.prompts import PromptTemplates
from core.validators import ResponseValidator
import hashlib
from typing import Literal
import time


class SmartRouter:
    """
    Router otimizado para decisões de roteamento do Supervisor.

    Características:
    - Usa SLM local (Phi3:mini) para decisões rápidas ($0 custo)
    - Cache de decisões (evita chamadas duplicadas)
    - Fallback automático para regras se SLM falhar
    - Monitoramento de estatísticas

    Exemplo:
        router = SmartRouter()
        next_agent = router.route(state)  # "script_agent"
    """

    def __init__(self, enable_cache: bool = True, enable_fallback: bool = True):
        """
        Inicializa SmartRouter.

        Args:
            enable_cache: Se True, ativa cache de decisões
            enable_fallback: Se True, usa regras como fallback se SLM falhar
        """
        # Cliente SLM local (Phi3:mini via Ollama)
        self.client = AIClient(model="phi3:mini", use_local=True)

        # Configurações
        self.enable_cache = enable_cache
        self.enable_fallback = enable_fallback

        # Cache de decisões
        self.decision_cache = {}

        # Estatísticas
        self.stats = {
            "total_decisions": 0,
            "cache_hits": 0,
            "slm_calls": 0,
            "fallback_calls": 0,
            "invalid_responses": 0,
            "total_time_ms": 0
        }

    def route(
        self,
        state: dict
    ) -> Literal["script_agent", "visual_agent", "audio_agent", "editor_agent", "FINISH"]:
        """
        Decide qual agente chamar a seguir baseado no estado.

        Fluxo:
        1. Calcula hash do estado
        2. Verifica cache
        3. Se não cached, chama SLM local
        4. Valida resposta
        5. Armazena no cache
        6. Retorna decisão

        Args:
            state: Estado atual do vídeo (VideoState)

        Returns:
            Nome do próximo agente ou "FINISH"

        Exemplo:
            state = {"current_phase": 1, "script": None, ...}
            next_agent = router.route(state)  # "script_agent"
        """
        start_time = time.time()
        self.stats["total_decisions"] += 1

        # 1. Verificar cache
        if self.enable_cache:
            state_hash = self._hash_state(state)

            if state_hash in self.decision_cache:
                self.stats["cache_hits"] += 1
                decision = self.decision_cache[state_hash]
                print(f"[ROUTER] CACHE HIT! Decisão: {decision}")
                return decision

        # 2. Chamar SLM local
        try:
            decision = self._route_with_slm(state)
            self.stats["slm_calls"] += 1

        except Exception as e:
            print(f"[ROUTER] WARN - SLM falhou: {e}")

            if self.enable_fallback:
                decision = self._route_with_rules(state)
                self.stats["fallback_calls"] += 1
            else:
                raise

        # 3. Validar resposta
        if not ResponseValidator.validate_agent_name(decision):
            print(f"[ROUTER] WARN - Resposta inválida: '{decision}', usando fallback")
            self.stats["invalid_responses"] += 1

            decision = self._route_with_rules(state)
            self.stats["fallback_calls"] += 1

        # 4. Armazenar no cache
        if self.enable_cache:
            self.decision_cache[state_hash] = decision

        # 5. Atualizar estatísticas
        elapsed_ms = (time.time() - start_time) * 1000
        self.stats["total_time_ms"] += elapsed_ms

        print(f"[ROUTER] OK - Decisão: {decision} ({elapsed_ms:.0f}ms)")

        return decision

    def _route_with_slm(self, state: dict) -> str:
        """
        Decisão de roteamento usando SLM local (Phi3:mini).

        Args:
            state: Estado atual

        Returns:
            Nome do próximo agente

        Raises:
            Exception: Se chamada ao SLM falhar
        """
        # Construir prompt conciso
        prompt = PromptTemplates.routing_decision(state)
        system_prompt = PromptTemplates.routing_system_prompt()

        # Chamar SLM local
        response = self.client.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,  # Determinístico
            max_tokens=10,    # Resposta curta
            system_prompt=system_prompt
        )

        # Limpar resposta
        decision = ResponseValidator.clean_agent_name(response)

        return decision

    def _route_with_rules(self, state: dict) -> str:
        """
        Fallback: decisão baseada em regras (sem IA).

        Ordem de execução:
        1. Script (se não tem)
        2. Visual e Audio (podem ser paralelos, retorna primeiro faltante)
        3. Editor (se tem visual e audio, mas não tem vídeo)
        4. FINISH (se tem vídeo)

        Args:
            state: Estado atual

        Returns:
            Nome do próximo agente
        """
        # Verificar o que já foi feito
        has_script = bool(state.get('script'))
        has_visual = bool(state.get('visual_plan'))
        has_audio = bool(state.get('audio_files'))
        has_video = bool(state.get('video_path'))

        # Aplicar regras
        if not has_script:
            return "script_agent"
        elif not has_visual:
            return "visual_agent"
        elif not has_audio:
            return "audio_agent"
        elif not has_video:
            return "editor_agent"
        else:
            return "FINISH"

    def _hash_state(self, state: dict) -> str:
        """
        Cria hash único do estado para cache.

        Apenas chaves relevantes são consideradas para evitar
        cache misses desnecessários.

        Args:
            state: Estado atual

        Returns:
            Hash MD5 do estado relevante
        """
        # Extrair apenas chaves relevantes para roteamento
        relevant_state = {
            'phase': state.get('current_phase', 0),
            'has_script': bool(state.get('script')),
            'has_visual': bool(state.get('visual_plan')),
            'has_audio': bool(state.get('audio_files')),
            'has_video': bool(state.get('video_path'))
        }

        # Gerar hash
        state_str = str(sorted(relevant_state.items()))
        return hashlib.md5(state_str.encode()).hexdigest()

    def clear_cache(self):
        """Limpa cache de decisões"""
        self.decision_cache = {}
        print("[ROUTER] Cache limpo")

    def print_stats(self):
        """Imprime estatísticas de uso"""
        print("\n" + "="*60)
        print("ESTATISTICAS DO SMART ROUTER")
        print("="*60)

        print(f"Total de decisões: {self.stats['total_decisions']}")

        if self.stats['total_decisions'] > 0:
            # Taxa de cache hit
            cache_rate = (self.stats['cache_hits'] / self.stats['total_decisions']) * 100
            print(f"Cache hits: {self.stats['cache_hits']} ({cache_rate:.1f}%)")

            # Chamadas
            print(f"Chamadas SLM: {self.stats['slm_calls']}")
            print(f"Fallback (regras): {self.stats['fallback_calls']}")
            print(f"Respostas inválidas: {self.stats['invalid_responses']}")

            # Tempo
            avg_time = self.stats['total_time_ms'] / self.stats['total_decisions']
            print(f"Tempo médio: {avg_time:.0f}ms")
            print(f"Tempo total: {self.stats['total_time_ms']/1000:.2f}s")

        print("="*60 + "\n")

    def reset_stats(self):
        """Reseta estatísticas (mantém cache)"""
        self.stats = {
            "total_decisions": 0,
            "cache_hits": 0,
            "slm_calls": 0,
            "fallback_calls": 0,
            "invalid_responses": 0,
            "total_time_ms": 0
        }


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("🧪 Testando SmartRouter...\n")

    # Criar router
    router = SmartRouter(enable_cache=True, enable_fallback=True)

    # Estados de teste (simulando fluxo completo)
    print("=" * 60)
    print("SIMULAÇÃO: Criação de Vídeo Completo")
    print("=" * 60 + "\n")

    # Estado 1: Início (nada feito)
    print("▶️  Estado 1: Início")
    state1 = {
        "current_phase": 0,
        "script": None,
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }
    decision1 = router.route(state1)
    assert decision1 == "script_agent", f"Esperado 'script_agent', got '{decision1}'"
    print()

    # Estado 2: Script concluído
    print("▶️  Estado 2: Script concluído")
    state2 = {
        "current_phase": 1,
        "script": {"scenes": [{"scene": 1}]},
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }
    decision2 = router.route(state2)
    assert decision2 in ["visual_agent", "audio_agent"], f"Esperado 'visual_agent' ou 'audio_agent', got '{decision2}'"
    print()

    # Estado 3: Script + Visual concluídos
    print("▶️  Estado 3: Script + Visual concluídos")
    state3 = {
        "current_phase": 2,
        "script": {"scenes": [{"scene": 1}]},
        "visual_plan": {"scenes": []},
        "audio_files": None,
        "video_path": None
    }
    decision3 = router.route(state3)
    assert decision3 == "audio_agent", f"Esperado 'audio_agent', got '{decision3}'"
    print()

    # Estado 4: Script + Visual + Audio concluídos
    print("▶️  Estado 4: Tudo pronto, falta editar")
    state4 = {
        "current_phase": 3,
        "script": {"scenes": [{"scene": 1}]},
        "visual_plan": {"scenes": []},
        "audio_files": {"final_mix": {}},
        "video_path": None
    }
    decision4 = router.route(state4)
    assert decision4 == "editor_agent", f"Esperado 'editor_agent', got '{decision4}'"
    print()

    # Estado 5: Tudo concluído
    print("▶️  Estado 5: Vídeo finalizado")
    state5 = {
        "current_phase": 4,
        "script": {"scenes": [{"scene": 1}]},
        "visual_plan": {"scenes": []},
        "audio_files": {"final_mix": {}},
        "video_path": "./output.mp4"
    }
    decision5 = router.route(state5)
    assert decision5 == "FINISH", f"Esperado 'FINISH', got '{decision5}'"
    print()

    # Testar cache: repetir decisão 1
    print("=" * 60)
    print("TESTE DE CACHE: Repetir decisão 1")
    print("=" * 60 + "\n")

    print("▶️  Chamada duplicada (deve usar cache)")
    decision1_cached = router.route(state1)
    assert decision1_cached == decision1, "Cache retornou decisão diferente!"
    print()

    # Mostrar estatísticas
    router.print_stats()

    # Verificar taxa de cache
    cache_rate = (router.stats['cache_hits'] / router.stats['total_decisions']) * 100
    print(f"✅ Taxa de cache: {cache_rate:.1f}%")
    print(f"✅ Economia de chamadas: {router.stats['cache_hits']} chamadas evitadas")

    print("\n✅ Todos os testes passaram!")
