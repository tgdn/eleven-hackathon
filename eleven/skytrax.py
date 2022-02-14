import logging
from eleven.scraper import Scraper

logger = logging.getLogger(__name__)


class SkyTraxParser:
    def __init__(self, scraper: Scraper):
        self.scraper = scraper

    @classmethod
    def run(cls, scraper: Scraper):
        self = cls(scraper)

        return self

    def parse_airline_slug(self, tr):
        name = tr.get_text().strip()
        slug = tr.find("a").get("href").split("/")[-2].replace("-rating", "")
        return name, slug

    def get_airlines(self):
        soup = self.scraper.get(
            "https://skytraxratings.com/a-z-of-airline-ratings"
        )
        table = soup.find(id="tablepress-1")
        airlines = [self.parse_airline_slug(tr) for tr in table.find_all("tr")]
        return airlines

    def extract_rating(self, td_soup):
        # some values are N/A.
        if td_soup.get_text() == "N/A":
            return None
        total = 0
        for span in td_soup.find_all("span"):
            if "fill" not in span.get("class", []):
                break
            total += 1.0
        return total / 5.0

    def parse_article(self, article) -> dict:
        """Parse an article into a cleaner dict."""

        obj = {"author_review_count": 0}
        # rating
        rating = article.find(itemprop="reviewRating")

        try:
            obj["rating"] = float(
                rating.find(itemprop="ratingValue").next
            ) / float(rating.find(itemprop="bestRating").next)
        except Exception as e:
            logger.exception(e, "rating")

        # title
        obj["title"] = article.find(class_="text_header").next

        # author
        author = article.find(itemprop="author")

        # review count
        try:
            obj["author_review_count"] = int(
                author.find(class_="userStatusReviewCount").next.split(" ")[0]
            )
        except:
            pass

        # date
        obj["date"] = article.find(itemprop="datePublished")["content"]

        # location
        try:
            obj["location"] = (
                author.next_sibling.strip().replace("(", "").replace(")", "")
            )
        except Exception as e:
            logger.exception(e, "location")

        body = article.find(itemprop="reviewBody")
        has_link = not not body.find_all("a")
        left, *right = body.get_text().split("|")
        if has_link:
            review_body = "".join(right).strip()
        else:
            review_body = left
        obj["body"] = review_body.strip()
        # verified
        # obj["verified"] = (
        #     True
        #     if body.next.next.next.next.get_text() == "Trip Verified"
        #     else False
        # )

        # body
        # raw_body = body.next.next.next.next.next.next
        # if not obj["verified"]:
        #     raw_body = body.next.next.next.next.next
        # obj["body"] = raw_body[4:].strip()

        # table
        tabl = article.find("table", class_="review-ratings")
        for tr in tabl.find_all("tr"):
            left, right = tr.find_all("td")
            label = left.get_text()
            if "review-rating-stars" in right.get("class"):
                value = self.extract_rating(right)
            elif "rating-yes" in right.get("class"):
                value = (
                    True if right.get_text().strip().lower() == "yes" else False
                )
            else:
                value = right.get_text()
            obj[label] = value
        return obj

    def parse_page(self, soup) -> list:
        """"""
        articles = []
        for i, article in enumerate(
            soup.find_all("article", itemprop="review")
        ):
            try:
                logger.info(f"Processing article {i}")
                articles.append(self.parse_article(article))
            except Exception as e:
                logger.exception(e)

        return articles

    def scrape_airline(self, airline):
        """
        Scrape all pages of a given airline.
        FIXME: will incur an extra page request at the moment, can be easily fixed
        by checking itemprop=reviewCount dividing it by the number of articles
        per page (default=100) and finding whether there are multiple pages.
        """
        articles = []
        page = 1
        article_count = None
        logger.info(f"Scraping {airline}...")

        while True:
            url = f"https://www.airlinequality.com/seat-reviews/{airline}/page/{page}/?sortby=post_date%3ADesc&pagesize=100"
            soup = self.scraper.get(url)
            try:
                article_count = int(
                    soup.find(itemprop="reviewCount").get_text().strip()
                )
            except ValueError:
                pass
            articles += self.parse_page(soup)
            page += 1
            if len(soup.body.findAll(text="<<")) == 0:
                break

        # stats
        if article_count is not None:
            percentage_dl = len(articles) / article_count
            logger.info(
                f"Imported {len(articles)} out of {article_count} ({percentage_dl:.2%})"
            )

        return articles
