from pathlib import Path

# Generall settings
PAGE_LOAD_TIMEOUT_SECONDS = 5
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    + "Chrome/60.0.3112.50 Safari/537.36"
)

# Shop URLs
SHOPS_PATH = Path(__file__).parent / "shops.txt"
with open(SHOPS_PATH, "r") as f:
    SHOPS = []
    for line in f:
        if line.strip() and not line.strip().startswith("#"):
            url, kind = line.split("=")
            SHOPS.append((url.strip(), kind.strip()))
    SHOPS = tuple(SHOPS)

# Dictionary to save output in.
COLLECTED_DATA: dict[str, dict] = {
    shop[0]: {"kind": shop[1], "categorys": {}} for shop in SHOPS
}
