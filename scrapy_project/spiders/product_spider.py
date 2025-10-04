import scrapy
import urllib.parse
from scrapy_project.items import ProductItem


class ProductSearchSpider(scrapy.Spider):
    """
    A versatile spider for crawling multiple Iranian e-commerce websites.
    
    Usage:
    scrapy crawl product_search -a query="your search term"
    """
    
    name = 'product_search'
    allowed_domains = ['torob.com', 'emalls.ir', 'digikala.com']
    
    def __init__(self, query=None, *args, **kwargs):
        super(ProductSearchSpider, self).__init__(*args, **kwargs)
        
        if not query:
            raise ValueError("Query parameter is required. Use: -a query='search term'")
        
        self.query = query
        self.logger.info(f"Starting search for: {query}")
        
        # URL-encode the query for safe inclusion in URLs
        encoded_query = urllib.parse.quote_plus(query)
        
        # Generate start URLs dynamically based on the query
        self.start_urls = [
            f'https://torob.com/search/?query={encoded_query}',
            f'https://emalls.ir/search?q={encoded_query}',
            f'https://www.digikala.com/search/?q={encoded_query}',
        ]
        
        self.logger.info(f"Generated URLs: {self.start_urls}")
    
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
            elif 'digikala.com' in url:
                yield from self.parse_digikala(response)
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
            # CSS selector for product containers on Torob
            # Try multiple selectors to find product cards
            product_cards = response.css('.product-card, .product-item, .search-result-item, .product, [class*="product"]')
            
            if not product_cards:
                # Try more generic selectors
                product_cards = response.css('div[class*="card"], div[class*="item"], .result-item')
            
            self.logger.info(f"Found {len(product_cards)} product cards on Torob")
            
            for card in product_cards[:20]:  # Limit to first 20 results
                item = ProductItem()
                
                # Extract product name - try multiple selectors
                name_selectors = [
                    'h3 a::text', 'h2 a::text', 'h1 a::text',
                    '.product-title::text', '.title::text', '.name::text',
                    'a[title]::attr(title)', '.product-name::text',
                    '[class*="title"]::text', '[class*="name"]::text'
                ]
                
                product_name = None
                for selector in name_selectors:
                    name_text = card.css(selector).get()
                    if name_text and name_text.strip():
                        product_name = name_text.strip()
                        break
                
                if not product_name:
                    continue  # Skip if no name found
                
                item['product_name'] = product_name
                
                # Extract price - try multiple selectors
                price_selectors = [
                    '.price::text', '.product-price::text', '.cost::text',
                    '[class*="price"]::text', '.amount::text', '.value::text'
                ]
                
                for selector in price_selectors:
                    price_text = card.css(selector).get()
                    if price_text and price_text.strip():
                        item['price'] = price_text.strip()
                        break
                
                # Extract product URL - try multiple selectors
                url_selectors = [
                    'h3 a::attr(href)', 'h2 a::attr(href)', 'h1 a::attr(href)',
                    '.product-title a::attr(href)', '.title a::attr(href)',
                    'a[href]::attr(href)'
                ]
                
                for selector in url_selectors:
                    url_text = card.css(selector).get()
                    if url_text:
                        item['product_url'] = response.urljoin(url_text)
                        break
                
                # Set store name
                item['store_name'] = 'Torob'
                
                # Only yield if we have essential data
                if item.get('product_name'):
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
            # Try multiple selectors to find product cards
            product_cards = response.css('.product-item, .search-item, div[class*="product"], .item-box, .product, .result-item')
            
            if not product_cards:
                # Try more generic selectors
                product_cards = response.css('div[class*="card"], div[class*="item"], [class*="product"]')
            
            self.logger.info(f"Found {len(product_cards)} product cards on Emalls")
            
            for card in product_cards[:20]:  # Limit to first 20 results
                item = ProductItem()
                
                # Extract product name - try multiple selectors
                name_selectors = [
                    'h3::text', 'h2::text', 'h1::text',
                    '.product-name::text', '.title::text', '.name::text',
                    'a[title]::attr(title)', '.product-title::text',
                    '[class*="title"]::text', '[class*="name"]::text'
                ]
                
                product_name = None
                for selector in name_selectors:
                    name_text = card.css(selector).get()
                    if name_text and name_text.strip():
                        product_name = name_text.strip()
                        break
                
                if not product_name:
                    continue  # Skip if no name found
                
                item['product_name'] = product_name
                
                # Extract price - try multiple selectors
                price_selectors = [
                    '.price::text', '.product-price::text', '.cost::text',
                    '[class*="price"]::text', '.amount::text', '.value::text'
                ]
                
                for selector in price_selectors:
                    price_text = card.css(selector).get()
                    if price_text and price_text.strip():
                        item['price'] = price_text.strip()
                        break
                
                # Extract product URL - try multiple selectors
                url_selectors = [
                    'a::attr(href)', 'h3 a::attr(href)', 'h2 a::attr(href)',
                    '.product-title a::attr(href)', '.title a::attr(href)'
                ]
                
                for selector in url_selectors:
                    url_text = card.css(selector).get()
                    if url_text:
                        item['product_url'] = response.urljoin(url_text)
                        break
                
                # Set store name
                item['store_name'] = 'Emalls'
                
                # Only yield if we have essential data
                if item.get('product_name'):
                    yield item
                    
        except Exception as e:
            self.logger.error(f"Error parsing Emalls page: {str(e)}")
    
    def parse_digikala(self, response):
        """
        Parser for Digikala.com search results.
        """
        self.logger.info(f"Parsing Digikala results from: {response.url}")
        
        try:
            # CSS selector for product containers on Digikala
            # Try multiple selectors to find product cards
            product_cards = response.css('.product-item, .product-card, .product, .c-product-box, [class*="product"]')
            
            if not product_cards:
                # Try more generic selectors
                product_cards = response.css('div[class*="card"], div[class*="item"], .result-item')
            
            self.logger.info(f"Found {len(product_cards)} product cards on Digikala")
            
            for card in product_cards[:20]:  # Limit to first 20 results
                item = ProductItem()
                
                # Extract product name - try multiple selectors
                name_selectors = [
                    'h3 a::text', 'h2 a::text', 'h1 a::text',
                    '.product-title::text', '.title::text', '.name::text',
                    'a[title]::attr(title)', '.product-name::text',
                    '[class*="title"]::text', '[class*="name"]::text',
                    '.c-product-box__title::text', '.c-product-box__title a::text'
                ]
                
                product_name = None
                for selector in name_selectors:
                    name_text = card.css(selector).get()
                    if name_text and name_text.strip():
                        product_name = name_text.strip()
                        break
                
                if not product_name:
                    continue  # Skip if no name found
                
                item['product_name'] = product_name
                
                # Extract price - try multiple selectors
                price_selectors = [
                    '.price::text', '.product-price::text', '.cost::text',
                    '[class*="price"]::text', '.amount::text', '.value::text',
                    '.c-price__value::text', '.c-price__value::text'
                ]
                
                for selector in price_selectors:
                    price_text = card.css(selector).get()
                    if price_text and price_text.strip():
                        item['price'] = price_text.strip()
                        break
                
                # Extract product URL - try multiple selectors
                url_selectors = [
                    'h3 a::attr(href)', 'h2 a::attr(href)', 'h1 a::attr(href)',
                    '.product-title a::attr(href)', '.title a::attr(href)',
                    'a[href]::attr(href)', '.c-product-box__title a::attr(href)'
                ]
                
                for selector in url_selectors:
                    url_text = card.css(selector).get()
                    if url_text:
                        item['product_url'] = response.urljoin(url_text)
                        break
                
                # Set store name
                item['store_name'] = 'Digikala'
                
                # Only yield if we have essential data
                if item.get('product_name'):
                    yield item
                    
        except Exception as e:
            self.logger.error(f"Error parsing Digikala page: {str(e)}")
    
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