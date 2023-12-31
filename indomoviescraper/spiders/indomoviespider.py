import scrapy

from indomoviescraper.items import IndomoviescraperItem


class IndomovieSpider(scrapy.Spider):
    name = "indomoviespider"
    allowed_domains = ["www.imdb.com"]
    start_urls = ["https://www.imdb.com/search/title/?country_of_origin=ID"]

    def parse(self, response):
        movies = response.css(".lister-item")

        for movie in movies:
            item = IndomoviescraperItem()

            item["url"] = movie.css(".lister-item-header a::attr(href)").get()
            item["title"] = movie.css(".lister-item-header a::text").get()
            item["description"] = movie.xpath(
                ".//p[contains(text(), 'Director') or contains(text(), 'Stars')]/preceding-sibling::p[1]/text()"
            ).get()

            sep = movie.xpath(
                ".//p[contains(text(), 'Director')]/span[@class='ghost']"
            ).get()

            if sep:
                item["director"] = movie.xpath(
                    ".//p[contains(text(), 'Director')]/a[following-sibling::span[@class='ghost']]/text()"
                ).getall()

                director_count = len(item["director"])

                item["stars"] = movie.xpath(
                    f".//p[contains(text(), 'Director')]/a[position() > {director_count}]/text()"
                ).getall()
            else:
                item["director"] = movie.xpath(
                    ".//p[contains(text(), 'Director')]/a/text()"
                ).getall()

                item["stars"] = movie.xpath(
                    ".//p[contains(text(), 'Stars')]/a/text()"
                ).getall()

            item["year"] = movie.css(".lister-item-year::text").get()
            item["runtime"] = movie.css(".runtime::text").get()
            item["genre"] = movie.css(".genre::text").get()
            item["rating"] = movie.css(".certificate::text").get()
            item["imdb_score"] = movie.css(".ratings-imdb-rating strong::text").get()
            item["imdb_votes"] = movie.xpath(
                ".//span[contains(text(), 'Votes')]/following-sibling::span[@name='nv']/text()"
            ).get()
            item["metascore"] = movie.css(
                ".ratings-metascore span.metascore::text"
            ).get()
            item["gross"] = movie.xpath(
                ".//span[contains(text(), 'Gross')]/following-sibling::span[@name='nv']/text()"
            ).get()

            yield item

        next_page = response.css("a.lister-page-next.next-page::attr(href)").get()
        if next_page:
            MAIN_URL = "https://www.imdb.com"
            next_page_url = MAIN_URL + next_page

            yield response.follow(next_page_url, callback=self.parse)
