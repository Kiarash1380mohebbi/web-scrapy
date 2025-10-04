import scrapy
import urllib.parse
import json
import re
from scrapy_project.items import ProductItem


class ProductSearchSpider(scrapy.Spider):
    """
    A versatile spider for crawling multiple Iranian e-commerce websites.
    Supports bilingual search (English and Persian/Farsi).
    
    Usage:
    scrapy crawl product_search -a query="your search term"
    """
    
    name = 'product_search'
    allowed_domains = ['torob.com', 'digikala.com']
    
    def __init__(self, query=None, *args, **kwargs):
        super(ProductSearchSpider, self).__init__(*args, **kwargs)
        
        if not query:
            raise ValueError("Query parameter is required. Use: -a query='search term'")
        
        self.query = query
        self.logger.info(f"Starting search for: {query}")
        
        # URL-encode the query for safe inclusion in URLs
        # This handles both English and Persian characters
        encoded_query = urllib.parse.quote(query)
        
        # Generate start URLs dynamically based on the query
        self.start_urls = [
            f'https://torob.com/search/?query={encoded_query}',
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
            elif 'digikala.com' in url:
                yield from self.parse_digikala(response)
            else:
                self.logger.warning(f"No parser found for URL: {response.url}")
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {str(e)}")
    
    def parse_torob(self, response):
        """
        Parser for Torob.com search results.
        Extracts data from the __NEXT_DATA__ JSON embedded in the page.
        """
        self.logger.info(f"Parsing Torob results from: {response.url}")
        
        try:
            # Extract the JSON data from the __NEXT_DATA__ script tag
            script_data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
            
            if not script_data:
                self.logger.warning("Could not find __NEXT_DATA__ script in Torob page")
                return
            
            # Parse the JSON data
            data = json.loads(script_data)
            
            # Navigate to the products in the JSON structure
            # The structure is: props -> pageProps -> products (array)
            try:
                products = data.get('props', {}).get('pageProps', {}).get('products', [])
            except (KeyError, AttributeError) as e:
                self.logger.warning(f"Could not extract products from Torob JSON: {e}")
                return
            
            self.logger.info(f"Found {len(products)} products on Torob")
            
            for product in products[:20]:  # Limit to first 20 results
                item = ProductItem()
                
                # Extract product name
                product_name = product.get('name1') or product.get('name2')
                if not product_name:
                    continue
                
                item['product_name'] = product_name.strip()
                
                # Extract price (lowest price from shops)
                price = product.get('price')
                if price:
                    item['price'] = str(price)
                
                # Extract product URL
                product_url = product.get('web_client_absolute_url') or product.get('id')
                if product_url:
                    if not product_url.startswith('http'):
                        item['product_url'] = f"https://torob.com{product_url}"
                    else:
                        item['product_url'] = product_url
                
                # Set store name
                item['store_name'] = 'Torob'
                
                # Only yield if we have essential data
                if item.get('product_name'):
                    yield item
                    
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from Torob: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error parsing Torob page: {str(e)}")
    
    def parse_digikala(self, response):
        """
        Parser for Digikala.com search results.
        Extracts data from the __NEXT_DATA__ JSON embedded in the page.
        """
        self.logger.info(f"Parsing Digikala results from: {response.url}")
        
        try:
            # Extract the JSON data from the __NEXT_DATA__ script tag
            script_data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
            
            if not script_data:
                self.logger.warning("Could not find __NEXT_DATA__ script in Digikala page")
                return
            
            # Parse the JSON data
            data = json.loads(script_data)
            
            # Navigate to the products in the JSON structure
            # The structure may vary, so we need to explore it
            try:
                page_props = data.get('props', {}).get('pageProps', {})
                
                # Try to find products in various possible locations
                products = []
                if 'initialState' in page_props:
                    products = page_props.get('initialState', {}).get('entities', {}).get('products', [])
                elif 'searchData' in page_props:
                    products = page_props.get('searchData', {}).get('products', [])
                elif 'products' in page_props:
                    products = page_props.get('products', [])
                
                # If products is a dict, convert to list
                if isinstance(products, dict):
                    products = list(products.values())
                    
            except (KeyError, AttributeError) as e:
                self.logger.warning(f"Could not extract products from Digikala JSON: {e}")
                return
            
            self.logger.info(f"Found {len(products)} products on Digikala")
            
            for product in products[:20]:  # Limit to first 20 results
                item = ProductItem()
                
                # Extract product name (try different field names)
                product_name = product.get('title') or product.get('name') or product.get('title_fa')
                if not product_name:
                    continue
                
                item['product_name'] = product_name.strip()
                
                # Extract price
                price_data = product.get('price') or product.get('default_variant', {}).get('price')
                if price_data:
                    if isinstance(price_data, dict):
                        price = price_data.get('selling_price') or price_data.get('rrp_price')
                    else:
                        price = price_data
                    
                    if price:
                        # Convert from Rial to Toman (divide by 10)
                        item['price'] = str(int(price) // 10)
                
                # Extract product URL
                product_url = product.get('url') or product.get('url_fa')
                if product_url:
                    if not product_url.startswith('http'):
                        product_url = f"https://www.digikala.com{product_url}"
                    item['product_url'] = product_url
                
                # Set store name
                item['store_name'] = 'Digikala'
                
                # Only yield if we have essential data
                if item.get('product_name'):
                    yield item
                    
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from Digikala: {str(e)}")
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