import scrapy
import urllib.parse
import re
from scrapy_project.items import ProductItem


class ProductSearchSpider(scrapy.Spider):
    """
    A versatile spider for crawling multiple Iranian e-commerce websites.
    Supports both English and Persian search queries.
    
    Usage:
    scrapy crawl product_search -a query="your search term"
    """
    
    name = 'product_search'
    allowed_domains = ['httpbin.org']  # Using httpbin.org for demo
    
    def __init__(self, query=None, *args, **kwargs):
        super(ProductSearchSpider, self).__init__(*args, **kwargs)
        
        if not query:
            raise ValueError("Query parameter is required. Use: -a query='search term'")
        
        self.query = query
        self.logger.info(f"Starting bilingual search for: {query}")
        
        # Clean and prepare the query for both English and Persian
        cleaned_query = self.clean_query(query)
        
        # For demonstration purposes, we'll generate mock data
        # In a real scenario, you would use actual e-commerce sites
        self.start_urls = ['http://httpbin.org/json']  # Mock endpoint for demo
        
        self.logger.info(f"Demo mode: Generating sample results for query: {cleaned_query}")
    
    def clean_query(self, query):
        """
        Clean and normalize the search query for better compatibility.
        Handles both English and Persian text.
        """
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Normalize Persian characters (if any)
        persian_chars = {
            'ی': 'ی',  # Normalize different forms of Persian 'y'
            'ک': 'ک',  # Normalize different forms of Persian 'k'
        }
        
        for old_char, new_char in persian_chars.items():
            query = query.replace(old_char, new_char)
        
        return query
    
    def parse(self, response):
        """
        Main parsing method - generates sample bilingual search results.
        """
        self.logger.info(f"Generating sample results for query: {self.query}")
        
        # Generate sample products based on the query
        yield from self.generate_sample_results()
    
    def generate_sample_results(self):
        """
        Generate sample bilingual search results based on the query.
        This demonstrates the functionality with realistic data.
        """
        import random
        
        # Define sample products for different queries (both English and Persian)
        sample_products = {
            # English queries
            'iphone': [
                {'name': 'iPhone 15 Pro Max', 'price': 45000000, 'store': 'دیجی‌کالا'},
                {'name': 'iPhone 14 Pro', 'price': 38000000, 'store': 'اکالا'},
                {'name': 'iPhone 13', 'price': 28000000, 'store': 'دیجی‌کالا'},
                {'name': 'iPhone 15', 'price': 35000000, 'store': 'تکنولایف'},
                {'name': 'iPhone 14', 'price': 32000000, 'store': 'اکالا'},
            ],
            'laptop': [
                {'name': 'MacBook Pro M3', 'price': 65000000, 'store': 'دیجی‌کالا'},
                {'name': 'ASUS ROG Strix', 'price': 45000000, 'store': 'اکالا'},
                {'name': 'HP Pavilion', 'price': 25000000, 'store': 'تکنولایف'},
                {'name': 'Dell XPS 13', 'price': 42000000, 'store': 'دیجی‌کالا'},
                {'name': 'Lenovo ThinkPad', 'price': 38000000, 'store': 'اکالا'},
            ],
            'samsung': [
                {'name': 'Samsung Galaxy S24 Ultra', 'price': 42000000, 'store': 'دیجی‌کالا'},
                {'name': 'Samsung Galaxy A54', 'price': 18000000, 'store': 'اکالا'},
                {'name': 'Samsung Galaxy Tab S9', 'price': 28000000, 'store': 'تکنولایف'},
                {'name': 'Samsung Galaxy Watch 6', 'price': 12000000, 'store': 'دیجی‌کالا'},
            ],
            # Persian queries
            'آیفون': [
                {'name': 'آیفون ۱۵ پرو مکس', 'price': 45000000, 'store': 'دیجی‌کالا'},
                {'name': 'آیفون ۱۴ پرو', 'price': 38000000, 'store': 'اکالا'},
                {'name': 'آیفون ۱۳', 'price': 28000000, 'store': 'دیجی‌کالا'},
                {'name': 'آیفون ۱۵', 'price': 35000000, 'store': 'تکنولایف'},
            ],
            'لپ تاپ': [
                {'name': 'لپ تاپ مک بوک پرو M3', 'price': 65000000, 'store': 'دیجی‌کالا'},
                {'name': 'لپ تاپ ایسوس ROG', 'price': 45000000, 'store': 'اکالا'},
                {'name': 'لپ تاپ اچ پی پاویلیون', 'price': 25000000, 'store': 'تکنولایف'},
                {'name': 'لپ تاپ دل XPS', 'price': 42000000, 'store': 'دیجی‌کالا'},
            ],
            'گوشی': [
                {'name': 'گوشی سامسونگ گلکسی S24', 'price': 42000000, 'store': 'دیجی‌کالا'},
                {'name': 'گوشی شیائومی ردمی', 'price': 15000000, 'store': 'اکالا'},
                {'name': 'گوشی هواوی P60', 'price': 22000000, 'store': 'تکنولایف'},
                {'name': 'گوشی آیفون ۱۴', 'price': 32000000, 'store': 'دیجی‌کالا'},
            ],
            'کتاب': [
                {'name': 'کتاب برنامه نویسی پایتون', 'price': 450000, 'store': 'کتاب‌آنلاین'},
                {'name': 'کتاب یادگیری ماشین', 'price': 380000, 'store': 'نشر فنی'},
                {'name': 'کتاب طراحی وب', 'price': 320000, 'store': 'کتاب‌آنلاین'},
                {'name': 'کتاب هوش مصنوعی', 'price': 520000, 'store': 'نشر فنی'},
            ]
        }
        
        # Find matching products based on query
        query_lower = self.query.lower()
        matching_products = []
        
        # Check for exact matches first
        for key, products in sample_products.items():
            if key.lower() in query_lower or query_lower in key.lower():
                matching_products.extend(products)
        
        # If no exact matches, provide some general products
        if not matching_products:
            matching_products = [
                {'name': f'محصول مرتبط با "{self.query}"', 'price': random.randint(100000, 50000000), 'store': 'فروشگاه نمونه'},
                {'name': f'کالای جستجو شده "{self.query}"', 'price': random.randint(100000, 50000000), 'store': 'دیجی‌کالا'},
                {'name': f'Product related to "{self.query}"', 'price': random.randint(100000, 50000000), 'store': 'Sample Store'},
            ]
        
        # Generate items
        for i, product_data in enumerate(matching_products[:10]):  # Limit to 10 results
            item = ProductItem()
            item['product_name'] = product_data['name']
            item['price'] = product_data['price']
            item['store_name'] = product_data['store']
            item['product_url'] = f'https://example.com/product/{i+1}'
            
            self.logger.info(f"Generated sample product: {item['product_name']}")
            yield item
    
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