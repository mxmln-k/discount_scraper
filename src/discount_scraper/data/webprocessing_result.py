from dataclasses import dataclass
from typing import Literal

from discount_scraper.email_templates import PERIOD_NOT_VERIFIED, TEMPLATES


@dataclass(frozen=True)
class Webarticle:
    name: str
    info: list[str]

    def __hash__(self):
        return hash((self.name, tuple(self.info)))


@dataclass(frozen=True)
class Webcategory:
    name: str
    offers: list[Webarticle]

    def __hash__(self):
        return hash((self.name, tuple(self.offers)))


@dataclass(frozen=True)
class WebprocessingResult:
    store_name: str
    categories: list[Webcategory]
    period_verified: bool
    success: bool
    exception: str | None = None

    @staticmethod
    def parse(wprs: list[WebprocessingResult], kind: Literal["plain", "html"]) -> str:
        return TEMPLATES[kind]["base"].format(
            stores="\n".join(
                (
                    TEMPLATES[kind]["store"].format(
                        name=(
                            wpr.store_name
                            if wpr.period_verified
                            else f"{wpr.store_name} ({PERIOD_NOT_VERIFIED})"
                        ),
                        categories="\n".join(
                            TEMPLATES[kind]["category"].format(
                                name=category.name,
                                offers="\n".join(
                                    TEMPLATES[kind]["offer"].format(
                                        name=offer.name,
                                        infos="\n".join(
                                            TEMPLATES[kind]["info"].format(content=info)
                                            for info in offer.info
                                        ),
                                    )
                                    for offer in category.offers
                                ),
                            )
                            for category in wpr.categories
                        ),
                    )
                    if wpr.success
                    else TEMPLATES[kind]["failed"].format(name=wpr.store_name)
                )
                for wpr in wprs
            )
        )
