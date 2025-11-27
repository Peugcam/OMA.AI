"""
Editor Agent - Montagem de Video com FFmpeg

Monta o vídeo final combinando imagens, áudio e efeitos usando FFmpeg.
Integrado com módulos otimizados.
"""

import logging
import subprocess
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from core import AIClient, AIClientFactory
from core.paths import get_output_dir, get_temp_dir


class EditorAgent:
    """
    Agente especializado em edição e montagem de vídeo.

    Uses:
    - FFmpeg para montagem, transições e renderização
    - Phi3:mini (local) para análise opcional
    """

    def __init__(self, model_name: str = None):
        """
        Inicializa Editor Agent.

        Args:
            model_name: Modelo para análise (None = auto-detecta do .env)
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # AI client (opcional, para análise)
        if model_name:
            self.llm = AIClient(model=model_name, temperature=0.3)
        else:
            self.llm = AIClientFactory.create_for_agent("editor")

        # Diretório de saída (usa path dinâmico baseado no ambiente)
        self.output_dir = get_output_dir()
        self.logger.info(f"📁 Output dir: {self.output_dir}")

        # Diretórios adicionais apenas para Windows (desenvolvimento)
        self.additional_output_dirs = []
        if not self.output_dir.as_posix().startswith("/app"):
            # Apenas em desenvolvimento Windows, criar backups adicionais
            self.additional_output_dirs = [
                Path("D:/OMA_Videos"),  # Pendrive
                Path("./outputs/videos")  # Local (backup)
            ]
            for dir_path in self.additional_output_dirs:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"📁 Backup dir: {dir_path}")
                except Exception as e:
                    self.logger.warning(f"Não foi possível criar {dir_path}: {e}")

        # Verificar se FFmpeg está disponível
        self.ffmpeg_available = self._check_ffmpeg()


    def _check_ffmpeg(self) -> bool:
        """
        Verifica se FFmpeg está instalado e acessível.

        Returns:
            True se FFmpeg está disponível
        """
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.logger.info("OK - FFmpeg disponível")
                return True
            else:
                self.logger.warning("FFmpeg não encontrado")
                return False
        except Exception as e:
            self.logger.warning(f"FFmpeg não disponível: {e}")
            return False


    async def edit_video(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monta vídeo final combinando todos os assets.

        Args:
            state: Estado com script, visual_plan e audio_files

        Returns:
            Estado atualizado com video_path
        """
        self.logger.info("Montando vídeo final...")

        # Verificar assets
        script = state.get("script")
        visual_plan = state.get("visual_plan")
        audio_files = state.get("audio_files")

        if not script:
            raise ValueError("Script não encontrado")
        if not visual_plan:
            raise ValueError("Plano visual não encontrado")
        if not audio_files:
            raise ValueError("Arquivos de áudio não encontrados")

        # Gerar vídeo
        if self.ffmpeg_available:
            try:
                video_path = self._render_with_ffmpeg(script, visual_plan, audio_files)
                self.logger.info(f"OK - Vídeo renderizado: {video_path}")

                # Copiar para outros locais
                self._copy_to_all_locations(video_path)

            except Exception as e:
                self.logger.error(f"Erro ao renderizar com FFmpeg: {e}")
                video_path = self._create_placeholder_video()
        else:
            self.logger.warning("FFmpeg não disponível, criando placeholder")
            video_path = self._create_placeholder_video()

        # Atualizar estado
        state["video_path"] = str(video_path)
        state["current_phase"] = 4

        self.logger.info("OK - Edição concluída")

        return state


    def _render_with_ffmpeg(
        self,
        script: Dict[str, Any],
        visual_plan: Dict[str, Any],
        audio_files: Dict[str, Any]
    ) -> Path:
        """
        Renderiza vídeo usando FFmpeg.

        Args:
            script: Dados do roteiro
            visual_plan: Plano visual com imagens
            audio_files: Arquivos de áudio

        Returns:
            Path para vídeo renderizado
        """
        self.logger.info("Renderizando com FFmpeg...")

        # Nome do vídeo de saída
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = self.output_dir / f"video_{timestamp}.mp4"

        scenes = visual_plan.get("scenes", [])

        if not scenes:
            raise ValueError("Nenhuma cena visual encontrada")

        # Estratégia simples: criar vídeo de cada imagem com duração
        # e depois concatenar

        temp_videos = []
        temp_dir = get_temp_dir()
        self.logger.info(f"📁 Temp dir: {temp_dir}")

        try:
            # Criar vídeo para cada cena
            for i, scene in enumerate(scenes):
                media_path = scene.get("media_path")
                media_type = scene.get("media_type", "image")
                duration = scene.get("duration", 5)

                if not media_path or not Path(media_path).exists():
                    self.logger.warning(f"Mídia não encontrada para cena {i+1}: {media_path}")
                    continue

                self.logger.info(f"Processando cena {i+1}: {media_path}")

                # Se já é vídeo, apenas cortar/ajustar duração
                if media_type == "video":
                    temp_video = temp_dir / f"scene_{i:02d}.mp4"

                    # Primeiro verificar duração do vídeo source
                    probe_cmd = [
                        "ffprobe", "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1",
                        str(media_path)
                    ]
                    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    source_duration = float(probe_result.stdout.strip() or duration)

                    # Se vídeo source é mais curto que duração desejada, fazer loop
                    if source_duration < duration:
                        self.logger.info(f"⚠️ Vídeo source ({source_duration}s) menor que duração ({duration}s), aplicando loop")
                        cmd = [
                            "ffmpeg",
                            "-y",
                            "-stream_loop", "-1",  # Loop infinito
                            "-i", str(media_path),
                            "-t", str(duration),  # Cortar na duração exata
                            "-c:v", "libx264",
                            "-preset", "fast",
                            "-crf", "23",
                            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                            "-pix_fmt", "yuv420p",
                            "-r", "30",
                            "-an",  # Sem áudio
                            str(temp_video)
                        ]
                    else:
                        cmd = [
                            "ffmpeg",
                            "-y",
                            "-i", str(media_path),
                            "-t", str(duration),
                            "-c:v", "libx264",
                            "-preset", "fast",
                            "-crf", "23",
                            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                            "-pix_fmt", "yuv420p",
                            "-r", "30",
                            "-an",  # Sem áudio
                            str(temp_video)
                        ]

                    subprocess.run(cmd, check=True, capture_output=True)
                    temp_videos.append(temp_video)
                    self.logger.info(f"✅ Vídeo {i+1} processado ({duration}s)")
                    continue

                # Se é imagem, criar vídeo da imagem
                temp_video = temp_dir / f"scene_{i:02d}.mp4"

                cmd = [
                    "ffmpeg",
                    "-y",  # Sobrescrever
                    "-loop", "1",  # Loop da imagem
                    "-i", str(media_path),  # Input
                    "-t", str(duration),  # Duração
                    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",  # Resize
                    "-c:v", "libx264",  # Codec
                    "-pix_fmt", "yuv420p",  # Formato de pixel
                    "-r", "30",  # FPS
                    str(temp_video)
                ]

                self.logger.info(f"Renderizando cena {i+1}/{len(scenes)}...")

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    self.logger.error(f"Erro FFmpeg cena {i+1}: {result.stderr}")
                else:
                    temp_videos.append(temp_video)

            if not temp_videos:
                raise ValueError("Nenhum vídeo temporário foi criado")

            # Concatenar vídeos
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, "w") as f:
                for video in temp_videos:
                    f.write(f"file '{video.absolute()}'\n")

            # Comando de concatenação
            cmd = [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                str(output_path)
            ]

            # Calcular duração total do vídeo concatenado
            total_video_duration = sum(scene.get("duration", 5) for scene in scenes)
            self.logger.info(f"Duração total do vídeo: {total_video_duration}s")

            # Adicionar áudio se disponível
            narration_file = audio_files.get("final_mix") or audio_files.get("narration_file")

            if narration_file and narration_file != "placeholder" and Path(narration_file).exists():
                # Recriar comando com áudio - SEM -shortest para evitar freeze
                # Usar -t para definir duração exata do output
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(concat_file),
                    "-i", str(narration_file),
                    "-t", str(total_video_duration),  # Duração exata do vídeo
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-af", f"apad=whole_dur={total_video_duration}",  # Pad áudio se mais curto
                    str(output_path)
                ]

            self.logger.info("Concatenando cenas...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise Exception(f"Erro ao concatenar: {result.stderr}")

            self.logger.info(f"OK - Vídeo salvo: {output_path}")

            # Limpar arquivos temporários
            for temp_video in temp_videos:
                temp_video.unlink(missing_ok=True)
            concat_file.unlink(missing_ok=True)

            return output_path

        except Exception as e:
            self.logger.error(f"Erro no processo de renderização: {e}")
            # Limpar temp
            for temp_video in temp_videos:
                if temp_video.exists():
                    temp_video.unlink()
            raise


    def _copy_to_all_locations(self, source_path: Path):
        """
        Copia vídeo para todos os locais adicionais configurados (apenas Windows).

        Args:
            source_path: Path do vídeo original
        """
        import shutil

        filename = source_path.name

        for target_dir in self.additional_output_dirs:
            try:
                target_path = target_dir / filename
                shutil.copy2(source_path, target_path)
                self.logger.info(f"OK - Cópia salva em: {target_path}")
            except Exception as e:
                self.logger.warning(f"Não foi possível copiar para {target_dir}: {e}")


    def _create_placeholder_video(self) -> Path:
        """
        Cria vídeo placeholder quando FFmpeg não está disponível.

        Returns:
            Path para arquivo placeholder
        """
        self.logger.info("Criando placeholder de vídeo...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        placeholder_path = self.output_dir / f"video_{timestamp}_placeholder.txt"

        placeholder_path.write_text(
            "Placeholder de vídeo.\n"
            "FFmpeg não está disponível para renderização.\n"
            f"Criado em: {datetime.now().isoformat()}"
        )

        return placeholder_path


# ============================================================================
# Para compatibilidade
# ============================================================================

# Alias
render_video = EditorAgent().edit_video
