# Example 6-2. A first Scrapy spider


import scrapy
import re
# A. Define the data to be scraped
class NWinnerItem(scrapy.Item):
    country = scrapy.Field()
    name = scrapy.Field()
    link_text = scrapy.Field()

# B Create a named spider  
class NWinnerSpider(scrapy.Spider):
    """ 
    Scrapes the country and link text of the Nobel-winners.
    """
    name = 'nwinners_list'
    allowed_domains = ['en.wikipedia.org']
    start_urls = [
        "https://en.wikipedia.org /wiki/List_of_Nobel_laureates_by_country"
    ]

    # C A parse method to deal with the HTTP response
    def parse(self, response):
        # Gets all the <h3> headers on the page, most of which will be our
        # target country titles.
        h3s = response.xpath('//h3')
        for h3 in h3s:
            # Where possible, gets the text of the <h2> element’s child <span>
            # with class mw-headline.
            country = h3.xpath('span[@class="mw-headline"]/text()').extract()
            if country:
                # Gets the list of country winners.
                winners = h3.xpath('following-sibling::ol[1]')
                for w in winners.xpath('li'):
                    text = w.xpath('descendant-or-self::text()').extract()
                    yield NWinnerItem(
                        country=country[0],
                        name=text[0],
                        link_text = ' '.join(text)
                        )

