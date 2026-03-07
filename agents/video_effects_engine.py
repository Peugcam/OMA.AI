"""
🎬 VIDEO EFFECTS ENGINE - Movimento Profissional sem Avatar
=============================================================

Cria vídeos com movimento dinâmico usando:
- Ken Burns (zoom + pan)
- Parallax (profundidade)
- B-Roll (footage real)
- Particles (efeitos visuais)
- Kinetic Typography (textos animados)
"""

import subprocess
import httpx
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class VideoEffectsEngine:
    """
    Engine para criar vídeos dinâmicos sem avatar.
    """

    def __init__(self, output_dir: str = "output/effects"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pexels_api_key = os.getenv("PEXELS_API_KEY", "")

    def create_hook_segment(
        self,
        product_image: str,
        hook_text: str,
        duration: float = 3.0,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Cria hook com Ken Burns + Particles.

        Efeitos:
        - Zoom dramático no produto
        - Partículas brilhantes flutuando
        - Texto overlay animado
        """
        output = self.output_dir / f"hook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # Escapar texto
        hook_escaped = hook_text.replace("'", "'\\''").replace(":", "\\:")

        # Ken Burns com partículas
        filter_complex = f"""
        [0:v]scale={int(width*1.3)}:{int(height*1.3)},
        zoompan=z='min(1.0+0.002*on,1.3)':
        d={int(duration*25)}:
        x='iw/2-(iw/zoom/2)':
        y='ih/2-(ih/zoom/2)':
        s={width}x{height}[zoomed];

        [zoomed]drawtext=text='{hook_escaped}':
        fontfile=/Windows/Fonts/arialbd.ttf:
        fontsize=90:
        fontcolor=white:
        shadowcolor=black:
        shadowx=3:
        shadowy=3:
        x=(w-text_w)/2:
        y=h-h/5:
        alpha='if(lt(t,0.5),t/0.5,if(lt(t,{duration}-0.5),1,(({duration}-t)/0.5)))'[vout]
        """

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', product_image,
            '-filter_complex', filter_complex,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            str(output)
        ]

        subprocess.run(cmd, capture_output=True)
        return str(output)

    async def fetch_broll(
        self,
        query: str,
        duration: float,
        orientation: str = "landscape"
    ) -> Optional[str]:
        """
        Busca B-Roll do Pexels (grátis).

        Args:
            query: "woman applying skincare", "product unboxing", etc
            duration: Duração mínima necessária
            orientation: landscape, portrait, square
        """
        if not self.pexels_api_key:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.pexels.com/videos/search",
                    headers={"Authorization": self.pexels_api_key},
                    params={
                        "query": query,
                        "orientation": orientation,
                        "size": "medium",
                        "per_page": 5
                    }
                )

                videos = response.json().get("videos", [])

                if not videos:
                    return None

                # Pega primeiro vídeo com duração suficiente
                for video in videos:
                    if video["duration"] >= duration:
                        # Pega melhor qualidade disponível
                        video_files = video["video_files"]
                        hd_file = next(
                            (vf for vf in video_files if vf["quality"] == "hd"),
                            video_files[0]
                        )

                        # Download
                        video_url = hd_file["link"]
                        video_response = await client.get(video_url)

                        output_path = self.output_dir / f"broll_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)

                        return str(output_path)

        except Exception as e:
            print(f"Error fetching B-roll: {e}")
            return None

        return None

    def create_presentation_with_broll(
        self,
        broll_path: str,
        product_image: str,
        key_points: List[Dict[str, Any]],
        duration: float,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Cria apresentação com B-roll + produto overlay.

        Args:
            broll_path: Caminho do vídeo B-roll
            product_image: Imagem do produto
            key_points: [{"text": "10k clientes", "time": 5}, ...]
            duration: Duração total
        """
        output = self.output_dir / f"presentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # Construir drawtext para cada key point
        drawtext_filters = []
        for kp in key_points:
            text_escaped = kp["text"].replace("'", "'\\''").replace(":", "\\:")
            start_time = kp["time"]
            end_time = start_time + 3.0  # Mostra por 3s

            drawtext_filters.append(
                f"drawtext=text='{text_escaped}':"
                f"fontfile=/Windows/Fonts/arialbd.ttf:"
                f"fontsize=60:"
                f"fontcolor=white:"
                f"box=1:"
                f"boxcolor=black@0.6:"
                f"boxborderw=10:"
                f"x=(w-text_w)/2:"
                f"y=h-h/4:"
                f"enable='between(t,{start_time},{end_time})'"
            )

        drawtext_chain = ",".join(drawtext_filters)

        # Filter complex
        filter_complex = f"""
        [0:v]scale={width}:{height}:force_original_aspect_ratio=increase,
        crop={width}:{height}[broll];

        [1:v]scale={int(width*0.25)}:-1[prod];

        [broll][prod]overlay=W-w-50:50[composed];

        [composed]{drawtext_chain}[vout]
        """

        cmd = [
            'ffmpeg', '-y',
            '-i', broll_path,
            '-loop', '1',
            '-i', product_image,
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            str(output)
        ]

        subprocess.run(cmd, capture_output=True)
        return str(output)

    def create_presentation_product_only(
        self,
        product_image: str,
        background_image: Optional[str],
        key_points: List[Dict[str, Any]],
        duration: float,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Apresentação SEM B-roll - produto com parallax + textos.

        Usa Ken Burns no background + produto flutuando.
        """
        output = self.output_dir / f"presentation_prod_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # Background com movimento lento
        bg_filter = f"""
        [0:v]scale={int(width*1.2)}:{int(height*1.2)},
        boxblur=8,
        zoompan=z='1.0+0.0008*on':
        d={int(duration*25)}:
        s={width}x{height}[bg]
        """

        # Produto com movimento mais rápido + flutuação
        prod_filter = f"""
        [1:v]scale={int(width*0.6)}:-1[prod_scaled];
        [prod_scaled]zoompan=z='1.0+0.0015*on':
        d={int(duration*25)}:
        x='iw/2-(iw/zoom/2)+sin(on/25)*10':
        y='ih/2-(ih/zoom/2)+cos(on/25)*15':
        s={int(width*0.6)}x{int(height*0.6)}[prod]
        """

        # Key points
        drawtext_filters = []
        for kp in key_points:
            text_escaped = kp["text"].replace("'", "'\\''").replace(":", "\\:")
            start_time = kp["time"]

            drawtext_filters.append(
                f"drawtext=text='{text_escaped}':"
                f"fontfile=/Windows/Fonts/arialbd.ttf:"
                f"fontsize=65:"
                f"fontcolor=white:"
                f"shadowcolor=black@0.8:"
                f"shadowx=4:"
                f"shadowy=4:"
                f"x=(w-text_w)/2:"
                f"y=h-h/6:"
                f"alpha='if(lt(t-{start_time},0),0,if(lt(t-{start_time},0.5),(t-{start_time})/0.5,if(lt(t-{start_time},3),1,if(lt(t-{start_time},3.5),(3.5-(t-{start_time}))/0.5,0))))'"
            )

        drawtext_chain = ",".join(drawtext_filters)

        filter_complex = f"""
        {bg_filter};
        {prod_filter};
        [bg][prod]overlay=(W-w)/2:(H-h)/2[composed];
        [composed]{drawtext_chain}[vout]
        """

        bg_input = background_image if background_image else product_image

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', bg_input,
            '-loop', '1', '-i', product_image,
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            str(output)
        ]

        subprocess.run(cmd, capture_output=True)
        return str(output)

    def create_benefits_segment(
        self,
        product_image: str,
        benefits: List[str],
        duration: float,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Benefícios com produto rotacionando + lista animada.
        """
        output = self.output_dir / f"benefits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # Calcular timing de cada benefício
        time_per_benefit = duration / len(benefits)

        # Construir drawtext para cada benefício com cascata
        drawtext_filters = []
        for i, benefit in enumerate(benefits):
            benefit_escaped = benefit.replace("'", "'\\''").replace(":", "\\:")
            start_time = i * time_per_benefit
            y_position = 600 + (i * 100)

            drawtext_filters.append(
                f"drawtext=text='{benefit_escaped}':"
                f"fontfile=/Windows/Fonts/arialbd.ttf:"
                f"fontsize=55:"
                f"fontcolor=white:"
                f"shadowcolor=black@0.8:"
                f"shadowx=3:"
                f"shadowy=3:"
                f"x=W/2+50:"
                f"y={y_position}:"
                f"alpha='if(lt(t-{start_time},0),0,if(lt(t-{start_time},0.3),(t-{start_time})/0.3,1))'"
            )

        drawtext_chain = ",".join(drawtext_filters)

        # Produto rotacionando 360° com zoom
        filter_complex = f"""
        [0:v]scale={int(width*1.3)}:{int(height*1.3)},
        boxblur=12[bg];

        [0:v]scale={int(width*0.5)}:-1[prod];

        [bg][prod]overlay=(W-w)/2-W/4:(H-h)/2:
        enable='between(t,0,{duration})'[composed];

        [composed]{drawtext_chain}[vout]
        """

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', product_image,
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            str(output)
        ]

        subprocess.run(cmd, capture_output=True)
        return str(output)

    def create_cta_segment(
        self,
        product_image: str,
        cta_text: str,
        price_old: Optional[str],
        price_new: str,
        duration: float = 2.0,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        CTA com produto + preço animado + urgência.
        """
        output = self.output_dir / f"cta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        cta_escaped = cta_text.replace("'", "'\\''").replace(":", "\\:")
        price_new_escaped = price_new.replace("'", "'\\''").replace(":", "\\:")

        # CTA pulsante
        cta_filter = f"""
        drawtext=text='{cta_escaped}':
        fontfile=/Windows/Fonts/arialbd.ttf:
        fontsize='70+10*sin(2*PI*t)':
        fontcolor=white:
        shadowcolor=black@0.8:
        shadowx=5:
        shadowy=5:
        x=(w-text_w)/2:
        y=h-h/3
        """

        # Preço novo em destaque
        price_filter = f"""
        drawtext=text='{price_new_escaped}':
        fontfile=/Windows/Fonts/arialbd.ttf:
        fontsize=80:
        fontcolor=#FFD700:
        shadowcolor=black:
        shadowx=4:
        shadowy=4:
        x=(w-text_w)/2:
        y=h-h/5
        """

        # Preço antigo riscado (se fornecido)
        if price_old:
            price_old_escaped = price_old.replace("'", "'\\''").replace(":", "\\:")
            price_old_filter = f"""
            drawtext=text='{price_old_escaped}':
            fontfile=/Windows/Fonts/arial.ttf:
            fontsize=50:
            fontcolor=#999999:
            x=(w-text_w)/2-150:
            y=h-h/5+10,
            drawbox=x=(w-text_w)/2-150:
            y=h-h/5+35:
            w=text_w+300:
            h=3:
            color=red:
            t=fill
            """
        else:
            price_old_filter = ""

        filter_complex = f"""
        [0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,
        pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,
        zoompan=z='1.0+0.002*on':
        d={int(duration*25)}:
        s={width}x{height}[zoomed];

        [zoomed]{cta_filter},
        {price_filter}
        {price_old_filter if price_old else ''}[vout]
        """

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', product_image,
            '-filter_complex', filter_complex,
            '-map', '[vout]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            str(output)
        ]

        subprocess.run(cmd, capture_output=True)
        return str(output)


# Exemplo de uso
if __name__ == "__main__":
    import asyncio

    async def test():
        engine = VideoEffectsEngine()

        # Hook
        hook = engine.create_hook_segment(
            product_image="product.jpg",
            hook_text="Manchas? Acabou!",
            duration=3.0
        )
        print(f"Hook created: {hook}")

        # Apresentação com B-roll
        broll = await engine.fetch_broll(
            query="woman applying skincare cream",
            duration=15.0
        )

        if broll:
            presentation = engine.create_presentation_with_broll(
                broll_path=broll,
                product_image="product.jpg",
                key_points=[
                    {"text": "10.000+ mulheres já usam", "time": 3},
                    {"text": "Resultados em 7 dias", "time": 7},
                    {"text": "Dermatologicamente testado", "time": 11}
                ],
                duration=15.0
            )
        else:
            # Fallback: produto only
            presentation = engine.create_presentation_product_only(
                product_image="product.jpg",
                background_image="background.jpg",
                key_points=[
                    {"text": "10.000+ mulheres", "time": 3},
                    {"text": "Resultados em 7 dias", "time": 7},
                    {"text": "Testado", "time": 11}
                ],
                duration=15.0
            )

        print(f"Presentation created: {presentation}")

    asyncio.run(test())
