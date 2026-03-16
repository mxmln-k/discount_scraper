from hercynia_bar_discount_tool.constants import CHAINS
from hercynia_bar_discount_tool.processors.processor import Processor


class Shop:
    def __init__(self, chain_name: str, shop_name: str, address: str, offers_url: str):
        self.chain_name = chain_name
        self.shop_name = shop_name
        self.address = address
        self.offers_url = offers_url

    @property
    def processor(self) -> Processor:
        return CHAINS[self.chain_name.lower()]

    def as_dict(self) -> dict[str, str]:
        return self.__dict__

    @classmethod
    def from_dict(cls, in_dict: dict[str, str]) -> "Shop":
        return cls(**in_dict)
