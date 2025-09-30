import scrapy
from scrapy_project.items import ProductItem
import re
from urllib.parse import quote


class ProductSearchSpider(scrapy.Spider):
    """
    A versatile spider that crawls multiple Iranian e-commerce websites
    to search for products based on a user-provided query.
    """
    name = "product_search"
    
    def __init__(self, query="", *args, **kwargs):
        super(ProductSearchSpider, self).__init__(*args, **kwargs)
        self.query = query
        
        # URL-encode the query for safe usage in URLs
        encoded_query = quote(query)
        
        # Build start URLs dynamically based on the search query
        self.start_urls = [
            f"https://torob.com/search/?query={encoded_query}",
            f"https://emalls.ir/search/{encoded_query}",
        ]
    
    def parse(self, response):
        """
        Main parse method that routes to the appropriate parser
        based on the website being crawled.
        """
        # Route to appropriate parser based on domain
        if 'torob.com' in response.url:
            yield from self.parse_torob(response)
        elif 'emalls.ir' in response.url:
            yield from self.parse_emalls(response)
        else:
            self.logger.warning(f"No parser available for URL: {response.url}")
    
    def parse_torob(self, response):
        """
        Parser for Torob.com search results.
        Extracts product information from the search results page.
        """
        # Target: Main product containers in search results
        # Each product card contains all the information we need
        products = response.css('div.ProductListItem_container__jR3zC')
        
        if not products:
            self.logger.warning(f"No products found on Torob for query: {self.query}")
            return
        
        for product in products:
            try:
                item = ProductItem()
                
                # Target: Product name/title - usually in a heading or link
                # This selector targets the main product title link
                product_name = product.css('h2.ProductListItem_title__DPrPN a::text').get()
                if not product_name:
                    product_name = product.css('a[data-test-id="product-title"]::text').get()
                
                # Target: Price - usually displayed prominently in the product card
                # This selector targets the price text element
                price_text = product.css('div.ProductListItem_price__o93Vf span::text').get()
                if not price_text:
                    price_text = product.css('span[data-test-id="product-price"]::text').get()
                
                # Target: Product URL - link to the detailed product page
                product_url = product.css('h2.ProductListItem_title__DPrPN a::attr(href)').get()
                if not product_url:
                    product_url = product.css('a[data-test-id="product-title"]::attr(href)').get()
                
                # Clean and validate data
                if product_name and price_text:
                    item['product_name'] = product_name.strip()
                    item['price'] = self._clean_price(price_text)
                    item['store_name'] = "Torob"
                    item['product_url'] = response.urljoin(product_url) if product_url else response.url
                    
                    yield item
                else:
                    self.logger.debug(f"Incomplete product data on Torob: {product_name}")
                    
            except Exception as e:
                self.logger.error(f"Error parsing Torob product: {str(e)}")
                continue
    
    def parse_emalls(self, response):
        """
        Parser for Emalls.ir search results.
        Extracts product information from the search results page.
        """
        # Target: Main product containers in search results
        # Each product item contains the product details
        products = response.css('div.product-item, div.product-box, article.product')
        
        if not products:
            self.logger.warning(f"No products found on Emalls for query: {self.query}")
            return
        
        for product in products:
            try:
                item = ProductItem()
                
                # Target: Product name/title - typically in a heading or main link
                # This selector targets the product title
                product_name = product.css('h3.product-title a::text, h2.title a::text, a.product-name::text').get()
                if not product_name:
                    product_name = product.css('div.title::text, span.name::text').get()
                
                # Target: Price - usually in a price container or span
                # This selector targets the price element
                price_text = product.css('span.price::text, div.price span::text, span.amount::text').get()
                if not price_text:
                    price_text = product.css('div.product-price::text, span.product-price::text').get()
                
                # Target: Product URL - link to product details
                product_url = product.css('h3.product-title a::attr(href), h2.title a::attr(href)').get()
                if not product_url:
                    product_url = product.css('a.product-name::attr(href), a.product-link::attr(href)').get()
                
                # Clean and validate data
                if product_name and price_text:
                    item['product_name'] = product_name.strip()
                    item['price'] = self._clean_price(price_text)
                    item['store_name'] = "Emalls"
                    item['product_url'] = response.urljoin(product_url) if product_url else response.url
                    
                    yield item
                else:
                    self.logger.debug(f"Incomplete product data on Emalls: {product_name}")
                    
            except Exception as e:
                self.logger.error(f"Error parsing Emalls product: {str(e)}")
                continue
    
    def _clean_price(self, price_text):
        """
        Clean and convert price text to a numerical value.
        Removes currency symbols, commas, and other non-numeric characters.
        
        Args:
            price_text: Raw price string from the website
            
        Returns:
            Cleaned price as integer or float, or 0 if parsing fails
        """
        if not price_text:
            return 0
        
        try:
            # Remove common Persian/Arabic currency symbols and text
            # Remove: تومان, ریال, Toman, Rial, currency symbols
            cleaned = re.sub(r'[تومانریالTomnRial,،\s]', '', price_text)
            
            # Remove any remaining non-numeric characters except decimal point
            cleaned = re.sub(r'[^\d.]', '', cleaned)
            
            # Convert to number
            if '.' in cleaned:
                return float(cleaned)
            else:
                return int(cleaned) if cleaned else 0
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Could not parse price: {price_text} - {str(e)}")
            return 0