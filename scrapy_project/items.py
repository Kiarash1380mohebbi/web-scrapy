# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    """
    Item definition for scraped product data.
    
    Fields:
    - product_name: The name/title of the product
    - price: The price of the product (will be cleaned to numeric format)
    - store_name: The name of the store/website selling the product
    - product_url: The URL link to the product page
    """
    
    product_name = scrapy.Field()
    price = scrapy.Field()
    store_name = scrapy.Field()
    product_url = scrapy.Field()