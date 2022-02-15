import logging
from eleven.scraper import Scraper
from eleven.skytrax import SkyTraxParser

logging.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)


if __name__ == "__main__":
    scraper = Scraper()
    SkyTraxParser.run(scraper)
