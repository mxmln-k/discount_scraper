from dataclasses import dataclass


@dataclass(frozen=True)
class Webarticle:
    name: str
    info: list[str]


@dataclass(frozen=True)
class Webcategory:
    name: str
    offers: list[Webarticle]


@dataclass(frozen=True)
class WebprocessingResult:
    shop_name: str
    categories: list[Webcategory]
    success: bool
