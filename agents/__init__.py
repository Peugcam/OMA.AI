"""
Agents Module - Agentes Especializados do OMA

Agentes disponiveis:
- SupervisorAgent: Coordenacao e planejamento
- ScriptAgent: Criacao de roteiros
- VisualAgent: Geracao/busca de conteudo visual (V1)
- VisualAgentV2: Integracao eficiente Pexels + Stability (V2)
- VisualAgentMCP: Versao MCP do visual agent
- AudioAgent: Producao de audio/narracao
- EditorAgent: Montagem final com FFmpeg
"""

from .supervisor_agent import SupervisorAgent
from .script_agent import ScriptAgent
from .visual_agent import VisualAgent
from .visual_agent_v2 import VisualAgentV2, VisualMetrics
from .visual_agent_mcp import VisualAgentMCP
from .audio_agent import AudioAgent
from .editor_agent import EditorAgent

__all__ = [
    "SupervisorAgent",
    "ScriptAgent",
    "VisualAgent",
    "VisualAgentV2",
    "VisualMetrics",
    "VisualAgentMCP",
    "AudioAgent",
    "EditorAgent"
]
