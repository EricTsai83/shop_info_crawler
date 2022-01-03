import scrapy
import re

BASE_URL = "https://en.wikipedia.org"


class NWinnerItem(scrapy.Item):
    name = scrapy.Field()
    link = scrapy.Field()
    year = scrapy.Field()
    category = scrapy.Field()
    country = scrapy.Field()
    gender = scrapy.Field()
    born_in = scrapy.Field()
    date_of_birth = scrapy.Field()
    date_of_death = scrapy.Field()
    place_of_birth = scrapy.Field()
    place_of_death = scrapy.Field()
    text = scrapy.Field()


class NWinnerSpider(scrapy.Spider):
    """
    This spider uses Wikipedia's  Nobel laureates list to generate requests which scrape the winners' pages for basic biographical data
    1. name：每支爬蟲在專案中的「唯一」名稱
    2. allowed_domains：定義這支爬蟲允許的網域清單，如果清單中不包含目標網址的網域或子網域，此次請求會被略過
    3. start_urls：爬蟲啟動時爬取的網址清單，會在 scrapy.Spider 類別中的
    """

    name = "nwinners_full"  # this spyder's name
    allowed_domains = ["en.wikipedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/List_of_Nobel_laureates_by_country"]

    def parse(self, response):
        """
        parse(): a method of the spider, which will be called with the downloaded
        Response object of each start URL. The response is passed to the method as
        the first and only argument.
        """
        filename = response.url.split("/")[-1]
        h3s = response.xpath("//h3")

        for h3 in h3s:
            country = h3.xpath(
                'span[@class="mw-headline"]/text()'
            ).extract()  # find country name
            if country:
                winners = h3.xpath(
                    "following-sibling::ol[1]"
                )  # find nobel prize winnner under the country name
                for w in winners.xpath("li"):
                    wdata = process_winner_li(w, country[0])

                    # callback: the function that will be called with the response of
                    #           this request (once it’s downloaded) as its first parameter
                    # dont_filter: Scrapy also has a built in filter which stops duplicate requests.
                    #              That is if Scrapy has already crawled a site and parsed the response, even if you yield another request with that url, scrapy will not process it.
                    # Sets the callback function to handle the response.
                    request = scrapy.Request(
                        wdata["link"], callback=self.parse_bio, dont_filter=True
                    )

                    # Creates a Scrapy Item to hold our Nobel data and initializes it
                    # with the data just scraped from process_winner_li. This Item
                    # data is attached to the metadata of the request to allow any
                    # response access to it.
                    # note: scrapy.Request請求url後生成一個"Request對象"，該對象帶有 meta(字典)的屬性，所以底下就是對字典增加一個key並賦值
                    request.meta["item"] = NWinnerItem(
                        **wdata
                    )  # wdata is a dictionary,  parameters value will set by value which key is same as parameter name
                    yield request  # we make the parse method a generator of consumable requests

    def parse_bio(self, response):  # for personal biography page
        """
        This method handles the callback from our bio-link request. In
        order to add scraped data to our Scrapy Item, we first retrieve it
        from the response metadata.
        """
        # 這個response已含有前一個 function(parse) 下 request "wdata['link']" 所產生的 meta 字典
        # ，此句將這個字典賦值給item， 完成信息傳遞
        item = response.meta["item"]  # meta是隨著Request產生時傳遞的
        href = response.xpath(
            "//li[@id='t-wikibase']/a/@href"
        ).extract()  # Extracts the link to Wikidata
        if href:
            # Uses the Wikidata link to generate a request with our spider’s
            # parse_wikidata as a callback to deal with the response.
            url = href[0]
            request = scrapy.Request(
                url, callback=self.parse_wikidata, dont_filter=True
            )
            request.meta["item"] = item
            yield request

    def parse_wikidata(self, response):
        item = response.meta["item"]
        property_codes = [  # 因為我們要爬的資料id是用代碼表示，所以我們建一個對照表
            {"name": "date_of_birth", "code": "P569"},
            {"name": "date_of_death", "code": "P570"},
            {"name": "place_of_birth", "code": "P19", "link": True},  # has hyperlink
            {"name": "place_of_death", "code": "P20", "link": True},  # has hyperlink
            {"name": "gender", "code": "P21", "link": True},
        ]

        p_template = '//*[@id="{code}"]/div[2]/div/div/div[2]/div[1]/div/div[2]/div[2]/div[1]{link_html}/text()'

        for prop in property_codes:
            link_html = ""
            if prop.get("link"):
                link_html = "/a"
            sel = response.xpath(
                p_template.format(code=prop["code"], link_html=link_html)
            )
            if sel:
                item[prop["name"]] = sel[0].extract()

        yield item


def get_persondata(table, item):
    fields = ["Date of birth", "Place of birth", "Date of death", "Place of death"]
    for tr in table.xpath("tr"):
        label = tr.xpath('td[@class="persondata-label"]/text()').extract()
        if label and label[0] in fields:
            text = " ".join(
                tr.xpath("td[not(@class)]/descendant-or-self::text()").extract()
            )
            print(text)
            item[label[0].lower().replace(" ", "_")] = text


def guess_gender(text, threshold=0):
    import re

    he = len(list(re.finditer(" he ", text)))
    she = len(list(re.finditer(" she ", text)))
    diff = she - he

    print("she %d, he %d, diff %d" % (she, he, diff))
    if diff > threshold:
        return "female"
    elif diff < -threshold:
        return "male"
    else:
        return None


def process_winner_li(w, country=None):
    """
    Process a winner's <li> tag, adding country of birth or nationality,
    as applicable.
    """
    wdata = {}
    # get the href link-adress from the <a> tag
    wdata["link"] = BASE_URL + w.xpath("a/@href").extract()[0]
    text = " ".join(w.xpath("descendant-or-self::text()").extract())
    # we use the comma-delimited text-elements, stripping whitespace from the ends.
    # split the text at the commas and take the first (name) string
    wdata["name"] = text.split(",")[0].strip()

    year = re.findall("\d{4}", text)
    if year:
        wdata["year"] = int(year[0])
    else:
        wdata["year"] = 0
        print("Oops, no year in ", text)

    # return all non-overlapping matches of pattern in string, as a list of strings
    category = re.findall(
        "Physics|Chemistry|Physiology or Medicine|Literature|Peace|Economics", text
    )
    if category:
        wdata["category"] = category[0]
    else:
        wdata["category"] = ""
        print("Oops, no category in ", text)

    if country:
        # if find * in text, means the country is the winner’s by birth not nationality at the time of the prize
        if text.find("*") != -1:
            wdata["country"] = ""
            wdata["born_in"] = country
        else:
            wdata["country"] = country
            wdata["born_in"] = ""

    # store a copy of the link's text-string for any manual corrections
    wdata["text"] = text
    return wdata
