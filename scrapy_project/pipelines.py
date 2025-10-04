# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from itemadapter import ItemAdapter


class CleanPricePipeline:
    """
    Pipeline to clean and normalize price data.
    Enhanced to handle both English and Persian price formats.
    """
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if adapter.get('price'):
            # Remove common Persian/Farsi currency symbols and text
            price_text = str(adapter['price'])
            
            # Remove common currency symbols and text (both English and Persian)
            price_text = re.sub(r'(تومان|ریال|درهم|Toman|Rial|USD|$|€|£)', '', price_text)
            
            # Remove commas and Persian comma
            price_text = re.sub(r'[,،]', '', price_text)
            
            # Remove extra whitespace
            price_text = re.sub(r'\s+', ' ', price_text.strip())
            
            # Extract numeric values (including decimals)
            # Handle both English and Persian digits
            persian_digits = '۰۱۲۳۴۵۶۷۸۹'
            english_digits = '0123456789'
            
            # Convert Persian digits to English
            for persian, english in zip(persian_digits, english_digits):
                price_text = price_text.replace(persian, english)
            
            # Extract numeric values
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