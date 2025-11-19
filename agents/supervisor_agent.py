"""
🧠 SUPERVISOR AGENT - Multi-Agent Orchestrator
===============================================

Inspirado em:
- AWS Bedrock Multi-Agent Collaboration (Supervisor Mode)
- Azure AI Multi-Agent Orchestrator (Supervisor-Worker Pattern)
- Google Vertex AI Agent Builder (ADK Multi-Agent Coordination)

Este agente coordena todos os worker agents para criar vídeos.

Model: Qwen2.5-3B-Instruct
Capabilities:
- Task decomposition (decompor tarefas complexas)
- Intelligent routing (rotear para agentes especializados)
- Result synthesis (sintetizar resultados parciais)
- Error recovery (recuperação de erros)
- Quality validation (validação de qualidade)
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio

# Módulos otimizados
from core import AIClient, AIClientFactory, SmartRouter, PromptTemplates, ResponseValidator

# Tipos para compatibilidade (VideoState é apenas um dict)
from typing import Dict, Any
VideoState = Dict[str, Any]


# ============================================================================
# TIPOS E ENUMS
# ============================================================================

class AgentStatus(Enum):
    """Status de execução de um agente"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(Enum):
    """Tipos de tarefas que o supervisor pode delegar"""
    SCRIPT_GENERATION = "script"
    VISUAL_PLANNING = "visual"
    AUDIO_PRODUCTION = "audio"
    VIDEO_EDITING = "editing"
    METADATA_GENERATION = "metadata"


class AgentRole(Enum):
    """Roles dos agentes no sistema"""
    SCRIPT_WRITER = "script_agent"
    VISUAL_PLANNER = "visual_agent"
    AUDIO_PRODUCER = "audio_agent"
    VIDEO_EDITOR = "editor_agent"


@dataclass
class SubTask:
    """Representa uma subtarefa delegada a um agente"""
    id: str
    type: TaskType
    agent: AgentRole
    description: str
    dependencies: List[str] = field(default_factory=list)
    priority: int = 1
    estimated_time: int = 60  # segundos
    status: AgentStatus = AgentStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class ExecutionPlan:
    """Plano de execução completo"""
    task_id: str
    subtasks: List[SubTask]
    parallel_groups: List[List[str]]  # Grupos de subtasks que podem rodar em paralelo
    total_estimated_time: int


# ============================================================================
# SUPERVISOR AGENT
# ============================================================================

class SupervisorAgent:
    """
    Agente supervisor que coordena todos os worker agents.

    Padrão: Supervisor-Worker (AWS Bedrock / Azure AI / Vertex AI)

    Responsabilidades:
    1. Analisar requisição do usuário
    2. Decompor em subtarefas
    3. Criar plano de execução
    4. Rotear subtarefas para agentes especializados
    5. Monitorar progresso
    6. Sintetizar resultados
    7. Validar qualidade final
    8. Recuperar de erros
    """

    def __init__(
        self,
        model_name: str = None,  # Auto-detecta do .env se None
        temperature: float = 0.3,  # Baixa temperatura para decisões mais determinísticas
        max_retries: int = 3,
        enable_cache: bool = True,  # Ativar cache do SmartRouter
        enable_fallback: bool = True  # Ativar fallback para regras
    ):
        self.temperature = temperature
        self.max_retries = max_retries

        # Criar AI client usando Factory (lê do .env)
        if model_name:
            self.llm = AIClient(model=model_name, temperature=temperature)
        else:
            self.llm = AIClientFactory.create_for_agent("supervisor")

        # SmartRouter para decisões de roteamento
        self.router = SmartRouter(
            enable_cache=enable_cache,
            enable_fallback=enable_fallback
        )

        self.logger = logging.getLogger(self.__class__.__name__)

        # Prompt system otimizado para supervisão
        self.system_prompt = PromptTemplates.supervisor_system_prompt()

        # Registro de agentes disponíveis (lidos do .env via Factory)
        self.agent_clients = AIClientFactory.create_all_agents()

        self.available_agents = {
            AgentRole.SCRIPT_WRITER: {
                "model": self.agent_clients.get("script").model,
                "capabilities": ["roteiro", "copywriting", "storytelling", "hooks"],
                "avg_time": 45  # segundos
            },
            AgentRole.VISUAL_PLANNER: {
                "model": self.agent_clients.get("visual").model,
                "capabilities": ["storyboard", "visual_prompts", "composition", "stock_search"],
                "avg_time": 60
            },
            AgentRole.AUDIO_PRODUCER: {
                "model": self.agent_clients.get("audio").model,
                "capabilities": ["tts", "music_selection", "audio_mixing"],
                "avg_time": 90
            },
            AgentRole.VIDEO_EDITOR: {
                "model": self.agent_clients.get("editor").model,
                "capabilities": ["ffmpeg", "transitions", "rendering", "export"],
                "avg_time": 120
            }
        }


    # ========================================================================
    # FASE 1: ANÁLISE E PLANEJAMENTO
    # ========================================================================

    async def analyze_request(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa a requisição do usuário e extrai requisitos.

        Args:
            brief: Briefing do vídeo com informações do cliente

        Returns:
            Análise estruturada dos requisitos
        """
        self.logger.info(f"🔍 Analisando requisição: {brief.get('title', 'Sem título')}")

        prompt = f"""Analise esta requisição de vídeo e extraia os requisitos:

BRIEFING:
{json.dumps(brief, indent=2, ensure_ascii=False)}

Identifique:
1. Objetivo principal do vídeo
2. Público-alvo
3. Tom/estilo desejado
4. Duração target
5. Elementos visuais necessários
6. Requisitos de áudio (narração, música)
7. Call-to-action ou mensagem final

Responda em JSON com essa estrutura:
{{
  "objective": "objetivo do vídeo",
  "target_audience": "descrição do público",
  "style": "tom e estilo",
  "duration_seconds": número,
  "visual_requirements": ["item1", "item2"],
  "audio_requirements": ["item1", "item2"],
  "cta": "call to action"
}}
"""

        response = await self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=self.system_prompt
        )

        # Usar ResponseValidator para parsing robusto
        analysis = ResponseValidator.extract_first_json(response)

        if analysis and "objective" in analysis:
            self.logger.info(f"OK - Analise completa: {analysis.get('objective', '')}")
            return analysis
        else:
            self.logger.error("WARN - Falha ao parsear analise, usando fallback")
            # Fallback: retornar estrutura básica
            return {
                "objective": brief.get("description", "Criar vídeo"),
                "target_audience": brief.get("target", "Público geral"),
                "style": brief.get("style", "profissional"),
                "duration_seconds": brief.get("duration", 30),
                "visual_requirements": ["imagens de alta qualidade"],
                "audio_requirements": ["narração profissional", "música de fundo"],
                "cta": brief.get("cta", "Saiba mais")
            }


    async def decompose_task(self, analysis: Dict[str, Any]) -> List[SubTask]:
        """
        Decompõe a tarefa principal em subtarefas atômicas.

        Inspirado em: AWS Bedrock Agent Decomposition Pattern

        Args:
            analysis: Análise da requisição

        Returns:
            Lista de subtarefas a serem executadas
        """
        self.logger.info("🔨 Decompondo tarefa em subtasks...")

        prompt = f"""Com base nesta análise, decomponha em SUBTAREFAS específicas:

ANÁLISE:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

Crie subtarefas para:
1. Script Agent: Escrever o roteiro completo
2. Visual Agent: Planejar storyboard e buscar mídia
3. Audio Agent: Gerar narração e música
4. Editor Agent: Montar e renderizar vídeo

Cada subtask deve ter:
- id único (ex: "script_01")
- tipo (script/visual/audio/editing)
- agente responsável
- descrição clara do que fazer
- dependências (ids de outras subtasks que precisam estar prontas)
- prioridade (1=alta, 3=baixa)

Responda em JSON:
{{
  "subtasks": [
    {{
      "id": "script_01",
      "type": "script",
      "agent": "script_agent",
      "description": "Escrever roteiro...",
      "dependencies": [],
      "priority": 1
    }},
    ...
  ]
}}
"""

        response = await self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=self.system_prompt
        )

        # Usar ResponseValidator para parsing robusto
        data = ResponseValidator.extract_first_json(response)

        if data and "subtasks" in data:
            try:
                subtasks = []

                for st in data.get("subtasks", []):
                    subtask = SubTask(
                        id=st["id"],
                        type=TaskType[st["type"].upper()],
                        agent=AgentRole[st["agent"].upper()],
                        description=st["description"],
                        dependencies=st.get("dependencies", []),
                        priority=st.get("priority", 2)
                    )
                    subtasks.append(subtask)

                self.logger.info(f"OK - {len(subtasks)} subtarefas criadas")
                return subtasks

            except Exception as e:
                self.logger.error(f"WARN - Erro na decomposicao: {e}")
                return self._create_default_plan(analysis)
        else:
            self.logger.error("WARN - Resposta invalida, usando plano padrao")
            return self._create_default_plan(analysis)


    def _create_default_plan(self, analysis: Dict) -> List[SubTask]:
        """Cria um plano padrão caso a decomposição falhe"""
        return [
            SubTask(
                id="script_01",
                type=TaskType.SCRIPT_GENERATION,
                agent=AgentRole.SCRIPT_WRITER,
                description=f"Escrever roteiro para: {analysis['objective']}",
                dependencies=[],
                priority=1
            ),
            SubTask(
                id="visual_01",
                type=TaskType.VISUAL_PLANNING,
                agent=AgentRole.VISUAL_PLANNER,
                description="Planejar storyboard e buscar mídia visual",
                dependencies=["script_01"],
                priority=2
            ),
            SubTask(
                id="audio_01",
                type=TaskType.AUDIO_PRODUCTION,
                agent=AgentRole.AUDIO_PRODUCER,
                description="Gerar narração e música de fundo",
                dependencies=["script_01"],
                priority=2
            ),
            SubTask(
                id="edit_01",
                type=TaskType.VIDEO_EDITING,
                agent=AgentRole.VIDEO_EDITOR,
                description="Montar vídeo final com todos os assets",
                dependencies=["visual_01", "audio_01"],
                priority=3
            )
        ]


    def create_execution_plan(self, subtasks: List[SubTask]) -> ExecutionPlan:
        """
        Cria um plano de execução otimizado identificando paralelismo.

        Inspirado em: Azure AI Orchestrator Parallel Execution

        Args:
            subtasks: Lista de subtarefas

        Returns:
            Plano de execução com grupos paralelos
        """
        self.logger.info("📋 Criando plano de execução...")

        # Análise de dependências para identificar paralelismo
        dependency_graph = {st.id: set(st.dependencies) for st in subtasks}
        completed = set()
        parallel_groups = []

        while len(completed) < len(subtasks):
            # Encontrar todas as tarefas que podem executar agora
            ready = []
            for st in subtasks:
                if st.id not in completed:
                    deps_met = all(dep in completed for dep in st.dependencies)
                    if deps_met:
                        ready.append(st.id)

            if not ready:
                self.logger.warning("⚠️ Detectado deadlock em dependências")
                break

            parallel_groups.append(ready)
            completed.update(ready)

        total_time = sum(
            max([st.estimated_time for st in subtasks if st.id in group], default=0)
            for group in parallel_groups
        )

        plan = ExecutionPlan(
            task_id=f"plan_{len(parallel_groups)}",
            subtasks=subtasks,
            parallel_groups=parallel_groups,
            total_estimated_time=total_time
        )

        self.logger.info(f"✅ Plano criado: {len(parallel_groups)} fases, ~{total_time}s")
        return plan


    # ========================================================================
    # ROTEAMENTO OTIMIZADO
    # ========================================================================

    def route_next(self, state: VideoState) -> str:
        """
        Decide qual agente chamar a seguir usando SmartRouter.

        Substituição otimizada do roteamento anterior que usava LLM.
        Agora usa SLM local (Phi3:mini) com cache MD5.

        Args:
            state: Estado atual do vídeo

        Returns:
            Nome do próximo agente ou "FINISH"

        Exemplo:
            next_agent = supervisor.route_next(state)
            # "script_agent" | "visual_agent" | "audio_agent" | "editor_agent" | "FINISH"
        """
        decision = self.router.route(state)
        self.logger.info(f"[ROUTER] Próximo: {decision}")
        return decision

    def get_routing_stats(self) -> dict:
        """
        Retorna estatísticas do SmartRouter.

        Returns:
            Dicionário com estatísticas de cache, tempo, etc.
        """
        return self.router.stats

    def print_routing_stats(self):
        """Imprime estatísticas do SmartRouter"""
        self.router.print_stats()

    def clear_routing_cache(self):
        """Limpa cache do SmartRouter"""
        self.router.clear_cache()

    # ========================================================================
    # FASE 2: EXECUÇÃO E COORDENAÇÃO
    # ========================================================================

    async def execute_plan(
        self,
        plan: ExecutionPlan,
        state: VideoState
    ) -> Tuple[bool, VideoState]:
        """
        Executa o plano coordenando todos os agentes.

        Inspirado em: Google Vertex AI Multi-System Agent Coordination

        Args:
            plan: Plano de execução
            state: Estado compartilhado entre agentes

        Returns:
            (sucesso, estado_atualizado)
        """
        self.logger.info(f"🚀 Iniciando execução do plano: {plan.task_id}")

        from . import script_agent, visual_agent, audio_agent, editor_agent

        # Mapear agentes
        agent_instances = {
            AgentRole.SCRIPT_WRITER: script_agent.ScriptAgent(),
            AgentRole.VISUAL_PLANNER: visual_agent.VisualAgent(),
            AgentRole.AUDIO_PRODUCER: audio_agent.AudioAgent(),
            AgentRole.VIDEO_EDITOR: editor_agent.EditorAgent()
        }

        try:
            # Executar cada grupo de tarefas paralelas
            for group_idx, group in enumerate(plan.parallel_groups, 1):
                self.logger.info(f"📦 Fase {group_idx}/{len(plan.parallel_groups)}")

                # Executar tarefas do grupo em paralelo
                tasks = []
                for task_id in group:
                    subtask = next(st for st in plan.subtasks if st.id == task_id)
                    agent = agent_instances[subtask.agent]

                    # Criar corrotina para execução
                    coro = self._execute_subtask(agent, subtask, state)
                    tasks.append(coro)

                # Aguardar conclusão de todas as tarefas do grupo
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Processar resultados
                for task_id, result in zip(group, results):
                    subtask = next(st for st in plan.subtasks if st.id == task_id)

                    if isinstance(result, Exception):
                        subtask.status = AgentStatus.FAILED
                        subtask.error = str(result)
                        self.logger.error(f"❌ {task_id} falhou: {result}")
                    else:
                        subtask.status = AgentStatus.COMPLETED
                        subtask.result = result
                        state = result  # Atualizar estado com resultado
                        self.logger.info(f"✅ {task_id} concluído")

            # Verificar se todas as tarefas foram concluídas
            failed = [st for st in plan.subtasks if st.status == AgentStatus.FAILED]
            if failed:
                self.logger.error(f"❌ {len(failed)} tarefas falharam")
                return False, state

            self.logger.info("🎉 Plano executado com sucesso!")
            return True, state

        except Exception as e:
            self.logger.error(f"❌ Erro fatal na execução: {e}")
            return False, state


    async def _execute_subtask(
        self,
        agent: Any,
        subtask: SubTask,
        state: VideoState
    ) -> VideoState:
        """Executa uma subtarefa específica com um agente"""
        self.logger.info(f"▶️  Executando: {subtask.id} ({subtask.agent.value})")

        subtask.status = AgentStatus.RUNNING

        # Chamar o agente apropriado
        if subtask.type == TaskType.SCRIPT_GENERATION:
            result = await agent.generate_script(state)
        elif subtask.type == TaskType.VISUAL_PLANNING:
            result = await agent.plan_visuals(state)
        elif subtask.type == TaskType.AUDIO_PRODUCTION:
            result = await agent.produce_audio(state)
        elif subtask.type == TaskType.VIDEO_EDITING:
            result = await agent.edit_video(state)
        else:
            raise ValueError(f"Task type desconhecido: {subtask.type}")

        return result


    # ========================================================================
    # FASE 3: VALIDAÇÃO E QUALIDADE
    # ========================================================================

    async def validate_output(self, state: VideoState) -> Tuple[bool, List[str]]:
        """
        Valida o output final antes de entregar ao cliente.

        Args:
            state: Estado final com vídeo renderizado

        Returns:
            (is_valid, lista_de_problemas)
        """
        self.logger.info("🔍 Validando output final...")

        issues = []

        # Verificar se o vídeo foi gerado
        if not state.get("video_path"):
            issues.append("Vídeo não foi renderizado")

        # Verificar metadados essenciais
        if not state.get("script"):
            issues.append("Script ausente")

        if not state.get("visual_plan"):
            issues.append("Plano visual ausente")

        if not state.get("audio_files"):
            issues.append("Arquivos de áudio ausentes")

        # Verificar duração
        expected_duration = state.get("brief", {}).get("duration", 30)
        actual_duration = state.get("metadata", {}).get("duration", 0)

        if abs(actual_duration - expected_duration) > 5:
            issues.append(f"Duração fora do esperado: {actual_duration}s vs {expected_duration}s")

        is_valid = len(issues) == 0

        if is_valid:
            self.logger.info("✅ Validação passou!")
        else:
            self.logger.warning(f"⚠️ {len(issues)} problemas encontrados")

        return is_valid, issues


    # ========================================================================
    # FASE 4: RECOVERY E ERROR HANDLING
    # ========================================================================

    async def recover_from_failure(
        self,
        failed_subtask: SubTask,
        state: VideoState
    ) -> Optional[SubTask]:
        """
        Tenta recuperar de uma falha em uma subtarefa.

        Estratégias:
        1. Retry simples (até 3x)
        2. Simplificar requisitos
        3. Usar fallback agent
        4. Solicitar intervenção humana

        Args:
            failed_subtask: Subtarefa que falhou
            state: Estado atual

        Returns:
            Nova subtarefa para tentar ou None se irrecuperável
        """
        self.logger.warning(f"🔄 Tentando recuperar: {failed_subtask.id}")

        # Estratégia 1: Retry simples
        if failed_subtask.priority < 3:
            self.logger.info("Tentando retry...")
            new_subtask = SubTask(
                id=f"{failed_subtask.id}_retry",
                type=failed_subtask.type,
                agent=failed_subtask.agent,
                description=f"[RETRY] {failed_subtask.description}",
                dependencies=failed_subtask.dependencies,
                priority=failed_subtask.priority + 1
            )
            return new_subtask

        # Estratégia 2: Fallback
        self.logger.error("❌ Falha irrecuperável, requer intervenção")
        return None
