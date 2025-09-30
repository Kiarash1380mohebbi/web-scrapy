# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from itemadapter import ItemAdapter


class CleanPricePipeline:
    """
    Pipeline to clean and normalize price data.
    Removes currency symbols, commas, and converts to numeric format.
    """
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if adapter.get('price'):
            # Remove common Persian/Farsi currency symbols and text
            price_text = str(adapter['price'])
            
            # Remove common currency symbols and text
            price_text = re.sub(r'[تومان|ریال|درهم|,،]', '', price_text)
            
            # Extract numeric values (including decimals)
            price_numbers = re.findall(r'[\d\.]+', price_text)
            
            if price_numbers:
                try:
                    # Take the first (usually largest) number found
                    cleaned_price = float(price_numbers[0])
                    adapter['price'] = cleaned_price
                except ValueError:
                    # If conversion fails, keep original text
                    spider.logger.warning(f"Could not convert price to number: {price_text}")
            else:
                spider.logger.warning(f"No numeric price found in: {price_text}")
        
        return item