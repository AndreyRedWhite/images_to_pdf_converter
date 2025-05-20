#!/usr/bin/env python3
"""
makepdf.py — собирает JPEG из каталога (по умолчанию ./source) в один PDF.

Зависимости: Pillow, Typer  (pip install pillow typer)
"""

from pathlib import Path
import sys
import typer
from PIL import Image

app = typer.Typer(add_help_option=True, rich_help_panel="Опции команды")


def collect_jpegs(directory: Path) -> list[Path]:
    """
    Возвращает отсортированный список JPEG‑файлов в каталоге.
    """
    return sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg")
    )


@app.command()
def build_pdf(
    source_dir: Path = typer.Option(
        Path.cwd() / "source",
        "--dir",
        "-d",
        help="Каталог с JPEG‑файлами (по умолчанию ./source)",
    ),
    output: Path = typer.Option(
        Path.cwd() / "combined.pdf",
        "--output",
        "-o",
        help="Имя итогового PDF (по умолчанию combined.pdf в текущем каталоге)",
    ),
):
    """
    Собрать все JPEG из каталога, отсортировать по имени и склеить в один PDF.
    """
    if not source_dir.exists() or not source_dir.is_dir():
        typer.echo(f"❌ Директория ‘{source_dir}’ не существует или недоступна.", err=True)
        raise typer.Exit(code=1)

    image_paths = collect_jpegs(source_dir)
    if not image_paths:
        typer.echo("⚠️  JPEG‑файлы не найдены. Проверьте каталог.", err=True)
        raise typer.Exit(code=1)

    # Загружаем изображения в память
    images = []
    for path in image_paths:
        try:
            img = Image.open(path)
            if img.mode != "RGB":
                img = img.convert("RGB")
            images.append(img)
        except Exception as exc:  # noqa: BLE001
            typer.echo(f"⚠️  Пропускаю {path.name}: {exc}", err=True)

    if not images:
        typer.echo("❌ Не удалось открыть ни одного изображения.", err=True)
        raise typer.Exit(code=1)

    first, *rest = images
    try:
        first.save(output, save_all=True, append_images=rest)
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"❌ Ошибка при создании PDF: {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"✅ PDF успешно создан: {output.resolve()}")


if __name__ == "__main__":
    app()
