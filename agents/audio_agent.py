"""
Audio Agent - Produtor de Audio com Edge TTS

Gera narração usando Edge TTS (gratuito) e adiciona música de fundo.
Integrado com módulos otimizados.
"""

import logging
import asyncio
import os
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

        # Verificar ElevenLabs (prioridade)
        self.elevenlabs_available = False
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_client = None

        # Tentar importar ElevenLabs (independente da API key)
        try:
            from elevenlabs.client import ElevenLabs
            if self.elevenlabs_key:
                self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_key)
                self.elevenlabs_available = True
                self.logger.info("✅ ElevenLabs TTS disponível (v2+ API)")
            else:
                self.logger.warning("ElevenLabs instalado mas sem API key")
        except ImportError as e:
            self.logger.warning(f"elevenlabs não instalado: {e}")
        except Exception as e:
            self.logger.error(f"Erro ao configurar ElevenLabs: {e}")

        # Fallback para Edge TTS (gratuito)
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.edge_tts_available = True
            self.logger.info("✅ Edge TTS disponível (fallback)")
        except ImportError:
            self.logger.warning("edge-tts não instalado")
            self.edge_tts_available = False

        self.tts_available = self.elevenlabs_available or self.edge_tts_available


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

        # Tentar gerar narração com TTS disponível
        if self.tts_available:
            narration_path = None

            # Prioridade 1: ElevenLabs (melhor qualidade)
            if self.elevenlabs_available:
                try:
                    self.logger.info("Tentando gerar com ElevenLabs...")
                    narration_path = await self._generate_elevenlabs_tts(narration)
                    self.logger.info(f"✅ Narração gerada com ElevenLabs: {narration_path}")
                except Exception as e:
                    self.logger.warning(f"ElevenLabs falhou: {e}")
                    narration_path = None

            # Fallback: Edge TTS
            if not narration_path and self.edge_tts_available:
                try:
                    self.logger.info("Tentando gerar com Edge TTS (fallback)...")
                    narration_path = await self._generate_edge_tts(narration)
                    self.logger.info(f"✅ Narração gerada com Edge TTS: {narration_path}")
                except Exception as e:
                    self.logger.error(f"Edge TTS também falhou: {e}")
                    narration_path = None

            # Resultado final
            if narration_path:
                audio_files["narration_file"] = str(narration_path)
                audio_files["final_mix"] = str(narration_path)
            else:
                self.logger.error("Todos os serviços TTS falharam")
                audio_files["narration_file"] = "placeholder"
                audio_files["final_mix"] = "placeholder"
        else:
            self.logger.warning("Nenhum serviço TTS disponível, usando placeholder")
            audio_files["narration_file"] = "placeholder"
            audio_files["final_mix"] = "placeholder"

        # Atualizar estado
        state["audio_files"] = audio_files
        state["current_phase"] = 3

        self.logger.info("OK - Produção de áudio concluída")

        return state


    async def _generate_elevenlabs_tts(self, text: str, voice_id: str = "XrExE9yKIg1WjnnlVkGX") -> Path:
        """
        Gera áudio usando ElevenLabs TTS (API v2+).

        Args:
            text: Texto para narrar
            voice_id: ID da voz (padrão: Matilda - voz feminina brasileira natural)

        Returns:
            Path para arquivo de áudio

        Voices disponíveis:
        - XrExE9yKIg1WjnnlVkGX: Matilda (português BR, feminina)
        - pqHfZKP75CvOlQylNhV4: Bill (português BR, masculino)
        """
        self.logger.info(f"Gerando TTS com ElevenLabs v2 (voice: {voice_id})...")

        # Path de saída
        output_path = self.output_dir / f"narration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

        # Gerar com ElevenLabs v2 API
        audio = self.elevenlabs_client.generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2"
        )

        # Salvar áudio (audio é um generator de bytes)
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        self.logger.info(f"OK - ElevenLabs TTS salvo: {output_path}")

        return output_path


    async def _generate_edge_tts(self, text: str, voice: str = "pt-BR-FranciscaNeural") -> Path:
        """
        Gera áudio usando Edge TTS (fallback gratuito).

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
        self.logger.info(f"Gerando TTS com Edge TTS (voice: {voice})...")

        # Validar texto
        if not text or not text.strip():
            raise ValueError("Texto vazio para TTS")

        # Path de saída
        output_path = self.output_dir / f"narration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

        # Gerar com Edge TTS
        communicate = self.edge_tts.Communicate(text=text, voice=voice, rate="+0%", volume="+0%")
        await communicate.save(str(output_path))

        # Verificar se arquivo foi criado
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Edge TTS não gerou áudio válido: {output_path}")

        self.logger.info(f"OK - Edge TTS salvo: {output_path} ({output_path.stat().st_size} bytes)")

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

# NOTA: Alias removido - causava instanciação durante import
# Se precisar de compatibilidade, use: AudioAgent().produce_audio diretamente
# generate_audio = AudioAgent().produce_audio  # ← Removido
