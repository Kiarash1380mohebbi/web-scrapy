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
    allowed_domains = ['torob.com', 'emalls.ir']
    
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
            f'https://emalls.ir/search/{encoded_query}',
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
            # Targets each product card in the search results
            product_cards = response.css('div.product-card, div[data-testid="product-card"], .search-result-item')
            
            if not product_cards:
                # Alternative selectors if the main one doesn't work
                product_cards = response.css('.product-item, .result-item, [class*="product"]')
            
            self.logger.info(f"Found {len(product_cards)} product cards on Torob")
            
            for card in product_cards[:20]:  # Limit to first 20 results
                item = ProductItem()
                
                # Extract product name - targets the main product title link
                name_selector = card.css('h3 a::text, .product-title::text, .title a::text, h2 a::text').get()
                if name_selector:
                    item['product_name'] = name_selector.strip()
                else:
                    continue  # Skip if no name found
                
                # Extract price - targets price display elements
                price_selector = card.css('.price::text, .product-price::text, [class*="price"]::text').get()
                if price_selector:
                    item['price'] = price_selector.strip()
                
                # Extract product URL - targets the main product link
                url_selector = card.css('h3 a::attr(href), .product-title::attr(href), .title a::attr(href)').get()
                if url_selector:
                    item['product_url'] = response.urljoin(url_selector)
                
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