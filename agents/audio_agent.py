"""
Audio Agent - Produtor de Audio com Edge TTS

Gera narração usando Edge TTS (gratuito) e adiciona música de fundo.
Integrado com módulos otimizados.
"""

import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from core import AIClient, AIClientFactory


class AudioAgent:
    """
    Agente especializado em produção de áudio.

    Uses:
    - Edge TTS para narração (gratuito, Microsoft)
    - Phi3:mini (local) para análise
    """

    def __init__(self, model_name: str = None):
        """
        Inicializa Audio Agent.

        Args:
            model_name: Modelo para análise (None = auto-detecta do .env)
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # AI client para análise (opcional, para escolher voz)
        if model_name:
            self.llm = AIClient(model=model_name, temperature=0.3)
        else:
            self.llm = AIClientFactory.create_for_agent("audio")

        # Diretórios de saída (múltiplos locais)
        self.output_dirs = [
            Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos/audio"),
            Path("D:/OMA_Videos/audio"),
            Path("./outputs/audio")
        ]

        # Criar diretórios
        for dir_path in self.output_dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.warning(f"Não foi possível criar {dir_path}: {e}")

        # Usar primeiro como principal
        self.output_dir = self.output_dirs[0]

        # Verificar se edge-tts está instalado
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.tts_available = True
        except ImportError:
            self.logger.warning("edge-tts não instalado. Use: pip install edge-tts")
            self.edge_tts = None
            self.tts_available = False


    async def produce_audio(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produz áudio completo baseado no roteiro.

        Args:
            state: Estado com roteiro

        Returns:
            Estado atualizado com arquivos de áudio
        """
        self.logger.info("Produzindo áudio...")

        script = state.get("script")
        if not script:
            raise ValueError("Script não encontrado no estado")

        # Extrair narração completa
        narration = script.get("narration_full", "")

        if not narration:
            # Concatenar narração das cenas
            scenes = script.get("scenes", [])
            narration = " ".join([s.get("narration", "") for s in scenes if s.get("narration")])

        if not narration:
            self.logger.warning("Nenhuma narração encontrada, criando áudio silencioso")
            narration = "Este é um vídeo sem narração."

        # Gerar áudio
        audio_files = {
            "audio_production_id": f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "narration_file": None,
            "music_file": None,
            "final_mix": None,
            "generated_at": datetime.now().isoformat()
        }

        # Gerar narração com Edge TTS
        if self.tts_available:
            try:
                narration_path = await self._generate_tts(narration)
                audio_files["narration_file"] = str(narration_path)
                audio_files["final_mix"] = str(narration_path)  # Por enquanto, apenas narração
                self.logger.info(f"OK - Narração gerada: {narration_path}")
            except Exception as e:
                self.logger.error(f"Erro ao gerar TTS: {e}")
                audio_files["narration_file"] = "placeholder"
                audio_files["final_mix"] = "placeholder"
        else:
            self.logger.warning("Edge TTS não disponível, usando placeholder")
            audio_files["narration_file"] = "placeholder"
            audio_files["final_mix"] = "placeholder"

        # Atualizar estado
        state["audio_files"] = audio_files
        state["current_phase"] = 3

        self.logger.info("OK - Produção de áudio concluída")

        return state


    async def _generate_tts(self, text: str, voice: str = "pt-BR-FranciscaNeural") -> Path:
        """
        Gera áudio usando Edge TTS.

        Args:
            text: Texto para narrar
            voice: Voz a usar (padrão: Francisca, voz feminina brasileira)

        Returns:
            Path para arquivo de áudio

        Voices disponíveis:
        - pt-BR-FranciscaNeural (Feminino)
        - pt-BR-AntonioNeural (Masculino)
        - pt-BR-BrendaNeural (Feminino)
        - pt-BR-DonatoNeural (Masculino)
        """
        self.logger.info(f"Gerando TTS com voz: {voice}")

        # Path de saída
        output_path = self.output_dir / f"narration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

        # Gerar com Edge TTS
        communicate = self.edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

        self.logger.info(f"OK - TTS salvo: {output_path}")

        return output_path


    def list_available_voices(self) -> List[str]:
        """
        Lista vozes disponíveis em português.

        Returns:
            Lista de IDs de vozes
        """
        if not self.tts_available:
            return []

        # Vozes pt-BR mais comuns
        return [
            "pt-BR-FranciscaNeural",  # Feminino
            "pt-BR-AntonioNeural",    # Masculino
            "pt-BR-BrendaNeural",     # Feminino
            "pt-BR-DonatoNeural",     # Masculino
            "pt-BR-ThalitaNeural",    # Feminino (jovem)
            "pt-BR-ValerioNeural",    # Masculino (jovem)
        ]


# ============================================================================
# Para compatibilidade
# ============================================================================

# Alias
generate_audio = AudioAgent().produce_audio
