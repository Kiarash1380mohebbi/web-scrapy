import scrapy
import urllib.parse
import unicodedata
from scrapy_project.items import ProductItem


class ProductSearchSpider(scrapy.Spider):
    """
    A versatile spider for crawling multiple Iranian e-commerce websites.
    
    Usage:
    scrapy crawl product_search -a query="your search term"
    """
    
    name = 'product_search'
    allowed_domains = ['torob.com', 'emalls.ir']
    
    def __init__(self, query=None, *args, **kwargs):
        super(ProductSearchSpider, self).__init__(*args, **kwargs)
        
        if not query:
            raise ValueError("Query parameter is required. Use: -a query='search term'")
        
        # Normalize query for bilingual support (FA/EN)
        self.query = self._normalize_query(query)
        self.logger.info(f"Starting search for: {query}")
        
        # URL-encode the query for safe inclusion in URLs
        encoded_query = urllib.parse.quote_plus(self.query)
        
        # Generate start URLs dynamically based on the query
        self.start_urls = [
            f'https://torob.com/search/?query={encoded_query}',
            f'https://emalls.ir/search/{encoded_query}',
        ]
        
        self.logger.info(f"Generated URLs: {self.start_urls}")

    def _normalize_query(self, raw_query: str) -> str:
        # Remove zero-width characters and tatweel
        zero_width = ["\u200c", "\u200f", "\u200e", "\u202a", "\u202b", "\u202c", "\u0640"]
        q = raw_query
        for ch in zero_width:
            q = q.replace(ch, " ")
        # Normalize Arabic Yeh/Kaf to Persian forms
        q = q.replace("ي", "ی").replace("ك", "ک")
        # Normalize digits to ASCII
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"; arabic_digits = "٠١٢٣٤٥٦٧٨٩"; ascii_digits = "0123456789"
        trans_map = {ord(p): ord(a) for p, a in zip(persian_digits, ascii_digits)}
        trans_map.update({ord(p): ord(a) for p, a in zip(arabic_digits, ascii_digits)})
        q = q.translate(trans_map)
        # Collapse whitespace
        q = " ".join(q.split())
        return q
    
    def parse(self, response):
        """
        Main parsing method that routes to specific parsers based on the website.
        """
        url = response.url.lower()
        
        try:
            if 'torob.com' in url:
                yield from self.parse_torob(response)
            elif 'emalls.ir' in url:
                yield from self.parse_emalls(response)
            else:
                self.logger.warning(f"No parser found for URL: {response.url}")
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {str(e)}")
    
    def parse_torob(self, response):
        """
        Parser for Torob.com search results.
        """
        self.logger.info(f"Parsing Torob results from: {response.url}")
        
        try:
            # Torob renders anchors linking to product pages at paths starting with /p/
            product_links = response.css('a[href^="/p/"], a[href*="/p/"]')
            self.logger.info(f"Found {len(product_links)} product links on Torob")

            seen = set()
            for a in product_links[:30]:  # Limit to first 30 results
                href = a.attrib.get('href') or ''
                if not href:
                    continue
                if href in seen:
                    continue
                seen.add(href)

                name = a.attrib.get('title') or a.css('::text').get()
                if name:
                    name = name.strip()
                if not name:
                    # Fallback: check parent container text
                    parent_text = a.xpath('..//text()').get()
                    name = (parent_text or '').strip()

                if not name:
                    continue

                item = ProductItem()
                item['product_name'] = name
                item['product_url'] = response.urljoin(href)
                item['store_name'] = 'Torob'

                # Try to infer a nearby price text
                price = a.xpath('ancestor-or-self::*[1]//following::text()[contains(., "تومان") or contains(., "ريال") or contains(., "ریال")][1]').get()
                if price:
                    item['price'] = price.strip()

                yield item
                    
        except Exception as e:
            self.logger.error(f"Error parsing Torob page: {str(e)}")
    
    def parse_emalls(self, response):
        """
        Parser for Emalls.ir search results.
        """
        self.logger.info(f"Parsing Emalls results from: {response.url}")
        
        try:
            # CSS selector for product containers on Emalls
            # Targets each product item in the search results grid
            product_cards = response.css('.product-item, .search-item, div[class*="product"], .item-box')
            
            if not product_cards:
                # Alternative selectors for different page layouts
                product_cards = response.css('.product, .result-item, [class*="item"]')
            
            self.logger.info(f"Found {len(product_cards)} product cards on Emalls")
            
            for card in product_cards[:20]:  # Limit to first 20 results
                item = ProductItem()
                
                # Extract product name - targets the product title
                name_selector = card.css('h3::text, .product-name::text, .title::text, h2::text, a[title]::attr(title)').get()
                if name_selector:
                    item['product_name'] = name_selector.strip()
                else:
                    continue  # Skip if no name found
                
                # Extract price - targets various price display formats
                price_selector = card.css('.price::text, .product-price::text, .cost::text, [class*="price"]::text').get()
                if price_selector:
                    item['price'] = price_selector.strip()
                
                # Extract product URL - targets the main product link
                url_selector = card.css('a::attr(href)').get()
                if url_selector:
                    item['product_url'] = response.urljoin(url_selector)
                
                # Set store name
                item['store_name'] = 'Emalls'
                
                # Only yield if we have essential data
                if item.get('product_name'):
                    yield item
                    
        except Exception as e:
            self.logger.error(f"Error parsing Emalls page: {str(e)}")
    
    def parse_error(self, failure):
        """
        Handle request failures gracefully.
        """
        self.logger.error(f"Request failed: {failure.request.url} - {failure.value}")
        
    def closed(self, reason):
        """
        Called when the spider closes.
        """
        self.logger.info(f"Spider closed: {reason}")
        stats = self.crawler.stats
        item_count = stats.get_value('item_scraped_count', 0)
        self.logger.info(f"Total items scraped: {item_count}")