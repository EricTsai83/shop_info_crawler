# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

# class NobelWinnersPipeline:
#     def process_item(self, item, spider):
#         return item



# The old fashion way to write a class, but make your python 3 code
# compatible with python 2 and 3. Actually, you can just write 'class DropNonPersons:'
class DropNonPersons(object):  
    """ Remove non-person winners
    If our scraped item failed to find a gender property at Wikidata,
    it is probably an organization such as the Red Cross. Our visualization
    is focused on individual winners, so here we use DropItem to remove the
    item from our output stream.
    """
    def process_item(self, item, spider):
        if not item['gender']:
            raise DropItem("No gender for {}".format(item['name']))
        return item  # We need to return the item to further pipelines or for saving by Scrapy.




## Example 6-6. Scraping images with the image pipeline
class NobelImagesPipeline(ImagesPipeline):

    # def process_item(self, item, spider):
    #     if spider.name not in ['nwinners_minibio']:
    #         return item

    def get_media_requests(self, item, info):
        """
        This takes any image URLs scraped by our nwinners_minibio
        spider and generates an HTTP request for their content.
        """
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        """
        After the image URL requests have been made, the results are
        delivered to the item_completed method.
        """
        image_paths = [x['path'] for ok, x in results if ok]
        if image_paths:
            # these image_paths will be relative to IMAGES_STORE defined in settings.py
            item['bio_image'] = image_paths[0]
        return item





