import scrapy
import re


BASE_URL = 'https://en.wikipedia.org/'


class NWinnerItemBio(scrapy.Item):
    link = scrapy.Field()
    name = scrapy.Field()
    mini_bio = scrapy.Field()
    image_urls = scrapy.Field()
    bio_image = scrapy.Field()
    images = scrapy.Field()


class NWinnerSpiderBio(scrapy.Spider):
    """ 
    Scrapes the Nobel prize biography pages for portrait images and a biographical snippet
    1. name：每支爬蟲在專案中的「唯一」名稱
    2. allowed_domains：定義這支爬蟲允許的網域清單，如果清單中不包含目標網址的網域或子網域，此次請求會被略過
    3. start_urls：爬蟲啟動時爬取的網址清單，會在 scrapy.Spider 類別中的
    """
    name = 'nwinners_minibio'
    allowed_domains = ['en.wikipedia.org']
    start_urls = [
        'https://en.wikipedia.org/wiki/List_of_Nobel_laureates_by_country'
    ]

    # For Scrapy v 1.0+, custom_settings can override the item pipelines in settings
    custom_settings = {
        'ITEM_PIPELINES': {'nobel_winners.pipelines.NobelImagesPipeline':1},
    }

    # a parse method to deal with the HTTP response
    def parse(self,  response):
        filename = response.url.split('/')[-1]
        h3s = response.xpath('//h3')

        for h3 in h3s:
            country = h3.xpath('span[@class="mw-headline"]/text()').extract()  # find country name
            if country:
                winners = h3.xpath('following-sibling::ol[1]')  # find nobel prize winnner under the country name
                for w in winners.xpath('li'):
                    wdata = {}
                    wdata['link'] = BASE_URL + w.xpath('a/@href').extract()[0]
                    # process the winner's bio page with get_mini_bio method
                    request = scrapy.Request(
                                             wdata['link'],
                                             callback=self.get_mini_bio,
                                             dont_filter=True)
                    request.meta['item'] = NWinnerItemBio(**wdata)
                    # request.meta['debug_call_location'] = 'list to bio' # DEBUG
                    yield request


    def get_mini_bio(self, response):
        """
        Get the winner's bio-text and photo
        """
        BASE_URL_ESCAPED = 'https:\/\/en.wikipedia.org'
        item = response.meta['item']
        # cache image
        item['image_urls'] = []

        # Targets the first (and only) image in the table of class infobox
        # and gets its source (src) attribute (e.g., <img src=//
        # upload.wikimedia.org/…/Max_Perutz.jpg…).
        img_src = response.xpath('//table[contains(@class,"infobox")]//img/@src')
        if img_src:
            item['image_urls'] = ['https:' + img_src[0].extract()]
        mini_bio = ''

        # Get the paragraphs in the biography's body-text
        """
        This xpath gets all the paragraphs in the <div> with id mwcontent-text. 
        If the paragraphs are empty (text() == False), then the normalize-space(.)
        command is used to force the contents of the paragraph (. represents the
        p-node in question(段落節點)) to an empty string. This is to make sure any empty paragraph matches the stop-point
        marking the end of the intro section of the biography.
        """
        ps = response.xpath('//*[@id="mw-content-text"]/div/p[text() or normalize-space(.)=""]').extract()

        # Add introductory biography paragraphs till the empty breakpoint
        for p in ps:
            if p == '<p></p>':  # the bio-intros stop-point
                break
            mini_bio += p

        # correct for wiki-links
        # replaces Wikipedia’s internal hrefs (e.g., /wiki/…) with the full
        # addresses our visualization will need
        mini_bio = mini_bio.replace('href="/wiki', 'href="' + BASE_URL + '/wiki')
        mini_bio = mini_bio.replace('href="#', item['link'] + '#')
        item['mini_bio'] = mini_bio
        yield item