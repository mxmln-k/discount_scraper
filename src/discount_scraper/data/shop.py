from discount_scraper.constants import CHAINS
from discount_scraper.processors.processor import Processor


class Shop:
    def __init__(self, chain_name: str, shop_name: str, address: str, offers_url: str):
        self.chain_name = chain_name.lower()
        self.shop_name = shop_name
        self.address = address
        self.offers_url = offers_url

    @property
    def processor(self) -> Processor:
        return CHAINS[self.chain_name]
