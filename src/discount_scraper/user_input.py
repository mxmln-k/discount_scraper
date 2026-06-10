from pathlib import Path
import re
from typing import Any, Callable

from discount_scraper.constants import normalize_text


def get_list(
    path: Path, encoding: str | None = None, modify: Callable[[str], Any] = lambda x: x
) -> tuple[Any, ...]:
    with open(path, "r", encoding=encoding) as f:
        content = (line.strip() for line in f.readlines())

    return tuple(modify(line) for line in content if line)


def get_kwds(path: Path, encoding: str | None = None) -> tuple[re.Pattern, ...]:
    return get_list(
        path,
        encoding,
        lambda x: re.compile(rf"\b{re.escape(normalize_text(x.lower()))}\b"),
    )
