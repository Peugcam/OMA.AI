#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧹 Cleanup Script - OMA Video Generator
========================================

Limpa arquivos temporários e libera espaço.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta


def format_size(bytes):
    """Formata tamanho em bytes para humano"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"


def get_folder_size(path):
    """Calcula tamanho de uma pasta"""
    total = 0
    try:
        for entry in Path(path).rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except Exception:
        pass
    return total


def cleanup_old_videos(days=7, dry_run=True):
    """Remove vídeos com mais de N dias"""
    print(f"\n[VIDEOS] Limpando vídeos com mais de {days} dias...")

    videos_dir = Path("outputs/videos")
    if not videos_dir.exists():
        print("  Pasta não encontrada")
        return 0

    cutoff = datetime.now() - timedelta(days=days)
    removed_size = 0
    removed_count = 0

    for video in videos_dir.glob("*.mp4"):
        try:
            mtime = datetime.fromtimestamp(video.stat().st_mtime)
            if mtime < cutoff:
                size = video.stat().st_size
                if dry_run:
                    print(f"  [DRY-RUN] Removeria: {video.name} ({format_size(size)})")
                else:
                    video.unlink()
                    print(f"  Removido: {video.name} ({format_size(size)})")
                removed_size += size
                removed_count += 1
        except Exception as e:
            print(f"  Erro ao processar {video.name}: {e}")

    if removed_count == 0:
        print(f"  Nenhum vídeo com mais de {days} dias encontrado")
    else:
        print(f"  Total: {removed_count} vídeos, {format_size(removed_size)}")

    return removed_size


def cleanup_temp_files(dry_run=True):
    """Remove arquivos temporários"""
    print("\n[TEMP] Limpando arquivos temporários...")

    temp_patterns = [
        "outputs/temp/*",
        "outputs/*.json",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
    ]

    removed_size = 0
    removed_count = 0

    for pattern in temp_patterns:
        for path in Path(".").rglob(pattern):
            try:
                size = get_folder_size(path) if path.is_dir() else path.stat().st_size

                if dry_run:
                    print(f"  [DRY-RUN] Removeria: {path} ({format_size(size)})")
                else:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    print(f"  Removido: {path} ({format_size(size)})")

                removed_size += size
                removed_count += 1
            except Exception as e:
                print(f"  Erro ao processar {path}: {e}")

    if removed_count == 0:
        print("  Nenhum arquivo temporário encontrado")
    else:
        print(f"  Total: {removed_count} itens, {format_size(removed_size)}")

    return removed_size


def cleanup_logs(days=30, dry_run=True):
    """Remove logs antigos"""
    print(f"\n[LOGS] Limpando logs com mais de {days} dias...")

    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("  Pasta não encontrada")
        return 0

    cutoff = datetime.now() - timedelta(days=days)
    removed_size = 0
    removed_count = 0

    for log in logs_dir.glob("*.log"):
        try:
            mtime = datetime.fromtimestamp(log.stat().st_mtime)
            if mtime < cutoff:
                size = log.stat().st_size
                if dry_run:
                    print(f"  [DRY-RUN] Removeria: {log.name} ({format_size(size)})")
                else:
                    log.unlink()
                    print(f"  Removido: {log.name} ({format_size(size)})")
                removed_size += size
                removed_count += 1
        except Exception as e:
            print(f"  Erro ao processar {log.name}: {e}")

    if removed_count == 0:
        print(f"  Nenhum log com mais de {days} dias encontrado")
    else:
        print(f"  Total: {removed_count} logs, {format_size(removed_size)}")

    return removed_size


def cleanup_node_modules(dry_run=True):
    """Remove node_modules se existir"""
    print("\n[NODE] Verificando node_modules...")

    node_dir = Path("node_modules")
    if not node_dir.exists():
        print("  Pasta não encontrada")
        return 0

    size = get_folder_size(node_dir)

    if dry_run:
        print(f"  [DRY-RUN] Removeria: node_modules ({format_size(size)})")
        print("  Obs: Pode ser reinstalado com 'npm install' se necessário")
    else:
        shutil.rmtree(node_dir)
        print(f"  Removido: node_modules ({format_size(size)})")

    return size


def cleanup_test_artifacts(dry_run=True):
    """Remove artefatos de testes"""
    print("\n[TESTS] Limpando artefatos de testes...")

    test_dirs = ["htmlcov", "reports", ".coverage"]
    removed_size = 0
    removed_count = 0

    for dir_name in test_dirs:
        path = Path(dir_name)
        if path.exists():
            size = get_folder_size(path) if path.is_dir() else path.stat().st_size

            if dry_run:
                print(f"  [DRY-RUN] Removeria: {dir_name} ({format_size(size)})")
            else:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"  Removido: {dir_name} ({format_size(size)})")

            removed_size += size
            removed_count += 1

    if removed_count == 0:
        print("  Nenhum artefato encontrado")
    else:
        print(f"  Total: {removed_count} itens, {format_size(removed_size)}")

    return removed_size


def cleanup_screenshots(dry_run=True):
    """Remove screenshots PNG da raiz"""
    print("\n[SCREENSHOTS] Limpando screenshots da raiz...")

    screenshots = list(Path(".").glob("*.png"))
    removed_size = 0

    for img in screenshots:
        try:
            size = img.stat().st_size
            if dry_run:
                print(f"  [DRY-RUN] Removeria: {img.name} ({format_size(size)})")
            else:
                img.unlink()
                print(f"  Removido: {img.name} ({format_size(size)})")
            removed_size += size
        except Exception as e:
            print(f"  Erro ao processar {img.name}: {e}")

    if not screenshots:
        print("  Nenhum screenshot encontrado")
    else:
        print(f"  Total: {len(screenshots)} imagens, {format_size(removed_size)}")

    return removed_size


def show_current_usage():
    """Mostra uso atual de espaço"""
    print("\n[ANALISE] Uso atual de espaço:")
    print("=" * 60)

    dirs = ["outputs", "node_modules", "htmlcov", "reports", "logs", "."]

    for dir_name in dirs:
        path = Path(dir_name)
        if path.exists():
            size = get_folder_size(path)
            print(f"  {dir_name:20s}: {format_size(size):>10s}")

    print("=" * 60)


def main():
    """Script principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Limpa arquivos temporários do OMA Video Generator"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Executar limpeza (padrão é dry-run)"
    )
    parser.add_argument(
        "--videos-days",
        type=int,
        default=7,
        help="Remover vídeos com mais de N dias (padrão: 7)"
    )
    parser.add_argument(
        "--logs-days",
        type=int,
        default=30,
        help="Remover logs com mais de N dias (padrão: 30)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Limpar tudo (vídeos, logs, temp, node_modules, etc)"
    )
    parser.add_argument(
        "--safe",
        action="store_true",
        help="Modo seguro (apenas temp files, sem vídeos)"
    )

    args = parser.parse_args()

    dry_run = not args.execute

    print("=" * 70)
    if dry_run:
        print("MODO DRY-RUN - Nenhum arquivo será removido")
        print("Use --execute para realmente remover arquivos")
    else:
        print("MODO EXECUÇÃO - Arquivos SERÃO REMOVIDOS!")
    print("=" * 70)

    show_current_usage()

    total_freed = 0

    # Sempre limpa temp files
    total_freed += cleanup_temp_files(dry_run)

    if args.safe:
        print("\n[MODO SEGURO] Apenas arquivos temporários removidos")
    elif args.all:
        total_freed += cleanup_old_videos(args.videos_days, dry_run)
        total_freed += cleanup_logs(args.logs_days, dry_run)
        total_freed += cleanup_node_modules(dry_run)
        total_freed += cleanup_test_artifacts(dry_run)
        total_freed += cleanup_screenshots(dry_run)
    else:
        total_freed += cleanup_old_videos(args.videos_days, dry_run)
        total_freed += cleanup_logs(args.logs_days, dry_run)

    print("\n" + "=" * 70)
    print(f"TOTAL A LIBERAR: {format_size(total_freed)}")
    print("=" * 70)

    if dry_run:
        print("\nPara executar a limpeza de verdade:")
        print("  python cleanup.py --execute")
        print("\nOpções:")
        print("  --all         # Limpar tudo (incluindo node_modules)")
        print("  --safe        # Apenas temp files (preserva vídeos)")
        print("  --videos-days 3  # Vídeos com mais de 3 dias")


if __name__ == "__main__":
    main()
