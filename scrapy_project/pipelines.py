# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from itemadapter import ItemAdapter


class CleanPricePipeline:
    """
    Pipeline to clean and normalize price data.
    - Normalizes Persian/Arabic digits to ASCII
    - Removes currency words and separators
    - Converts to integer Tomans; converts Rial to Toman by dividing by 10
    """

    PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
    ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
    ASCII_DIGITS = "0123456789"

    def _normalize_digits(self, text: str) -> str:
        trans_map = {ord(p): ord(a) for p, a in zip(self.PERSIAN_DIGITS, self.ASCII_DIGITS)}
        trans_map.update({ord(p): ord(a) for p, a in zip(self.ARABIC_DIGITS, self.ASCII_DIGITS)})
        return text.translate(trans_map)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('price'):
            original_text = str(adapter['price'])
            text = original_text

            # Detect currency unit before stripping
            has_rial = any(sym in text for sym in ["ریال", "ريال", "﷼"])  # Rial

            # Normalize digits to ASCII
            text = self._normalize_digits(text)

            # Remove currency words/symbols and common separators
            # Also strip non-breaking spaces and Arabic thousands separator
            text = text.replace('\u00a0', ' ').replace('٬', '')
            text = re.sub(r'(تومان|تومن|ریال|ريال|﷼|درهم)', ' ', text)
            text = re.sub(r'[،,]', '', text)

            # Extract the largest numeric chunk
            numbers = re.findall(r'(\d+(?:\.\d+)?)', text)
            if numbers:
                try:
                    value = float(max(numbers, key=lambda n: len(n)))
                    # Convert Rial to Toman if detected
                    if has_rial:
                        value = value / 10.0
                    adapter['price'] = int(round(value))
                except Exception:
                    spider.logger.warning(f"Could not convert price to number: {original_text}")
            else:
                spider.logger.warning(f"No numeric price found in: {original_text}")

        return item