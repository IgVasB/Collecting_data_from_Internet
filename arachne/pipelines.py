import scrapy
from scrapy.pipelines.images import ImagesPipeline


class ArachnePipeline:
    def process_item(self, item, spider):
        return item


class ArachnePhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item


    def file_path(self, request, item, response=None, info=None):
        file_name = item['name']
        return f'{file_name}.jpg'
