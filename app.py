"""
OMA Video Generator - Hugging Face Spaces Entry Point
======================================================

Este arquivo é o ponto de entrada para o Hugging Face Spaces.
Importa e executa o dashboard principal.
"""

import os

# Configurar variáveis de ambiente para HF Spaces
os.environ.setdefault("GRADIO_SERVER_NAME", "0.0.0.0")
os.environ.setdefault("GRADIO_SERVER_PORT", "7860")

# Criar diretórios necessários
for dir_path in ["outputs/videos", "outputs/temp", "outputs/images", "logs"]:
    os.makedirs(dir_path, exist_ok=True)

# Importar e executar o dashboard
from video_dashboard_complete import demo

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
