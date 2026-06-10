from dataclasses import dataclass
from datetime import date
from html import escape
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
    def parse(
        cls, wprs: list["WebprocessingResult"], kind: Literal["plain", "html"]
    ) -> str:
        wprs = cls.get_filtered_results(wprs)

        def format_value(value: str) -> str:
            return escape(value) if kind == "html" else value

        return TEMPLATES[kind]["base"].format(
            stores="\n".join(
                (
                    TEMPLATES[kind]["store"].format(
                        name=(
                            format_value(
                                f"{wpr.store_name} (gültig bis {wpr.offer_end_date.strftime('%d.%m.%Y') if wpr.offer_end_date else 'N/A'})"
                            )
                        ),
                        categories="\n".join(
                            TEMPLATES[kind]["category"].format(
                                name=format_value(category.name),
                                offers="\n".join(
                                    TEMPLATES[kind]["offer"].format(
                                        name=format_value(offer.name),
                                        infos="\n".join(
                                            TEMPLATES[kind]["info"].format(
                                                content=format_value(info)
                                            )
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
                    else TEMPLATES[kind]["failed"].format(
                        name=format_value(wpr.store_name)
                    )
                )
                for wpr in wprs
            )
        )

    @staticmethod
    def get_filtered_results(
        results: list["WebprocessingResult"],
    ) -> list["WebprocessingResult"]:
        return [result for result in results if result.categories or not result.success]
