from discount_scraper.constants import CHAINS
from discount_scraper.processors.edeka_processor import EdekaProcessor
from discount_scraper.processors.kaufland_processor import KauflandProcessor
from discount_scraper.processors.processor import Processor


class Store:
    # Whitelisted chain names
    CHAINS = {  # TODO: maybe not instantiate yet
        "edeka": EdekaProcessor(),
        "kaufland": KauflandProcessor(),
        "rewe": None,
        "aldi": None,
        "lidl": None,
        "netto": None,
        "penny": None,
    }

    def __init__(
        self,
        chain_name: str,
        store_name: str,
        address: str,
        offers_url: str,
        store_id: str,
    ):
        self.chain_name = chain_name.lower()
        self.store_name = store_name
        self.address = address
        self.offers_url = offers_url
        self.store_id = store_id

    @property
    def processor(self) -> Processor:
        return Store.CHAINS[self.chain_name]
