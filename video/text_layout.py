from pathlib import Path


def wrap_text(text: str, max_chars: int = 18) -> str:
    """Wrap Chinese/mixed text at a conservative character width."""
    text = " ".join(str(text).split())
    if len(text) <= max_chars:
        return text
    lines = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    return "\n".join(lines[:4])


def adaptive_font_size(text: str, base: int = 48, min_size: int = 28, max_chars: int = 18) -> int:
    length = len("".join(str(text).split()))
    if length <= max_chars:
        return base
    size = int(base * max_chars / min(length, max_chars * 1.8))
    return max(min_size, min(base, size))


def prepare_display_text(text: str, max_chars: int = 18) -> tuple[str, int]:
    wrapped = wrap_text(text, max_chars=max_chars)
    return wrapped, adaptive_font_size(wrapped, max_chars=max_chars)


def cleanup_render_text_files(output_dir: str) -> None:
    # Render-time helper files are hidden and live only in the output directory.
    for path in Path(output_dir).glob(".*_*.txt"):
        path.unlink(missing_ok=True)
