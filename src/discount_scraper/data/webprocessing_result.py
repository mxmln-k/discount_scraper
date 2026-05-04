from dataclasses import dataclass
from datetime import date
from typing import Literal

from discount_scraper.email_templates import TEMPLATES


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
    offer_end_date: date | None
    success: bool
    exception: str | None = None

    @classmethod
    def parse(cls, wprs: list[WebprocessingResult], kind: Literal["plain", "html"]) -> str:
        wprs = cls.get_filtered_results(wprs)
        return TEMPLATES[kind]["base"].format(
            stores="\n".join(
                (
                    TEMPLATES[kind]["store"].format(
                        name=(
                            f"{wpr.store_name} (gültig bis {wpr.offer_end_date.strftime("%d.%m.%Y") if wpr.offer_end_date else "N/A"})"
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

    @staticmethod
    def get_filtered_results(results: list["WebprocessingResult"]) -> list[Webcategory]:
        return [result for result in results if result.categories or not result.success]