# Scrapy settings for scrapy_project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scrapy_project'

SPIDER_MODULES = ['scrapy_project.spiders']
NEWSPIDER_MODULE = 'scrapy_project.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure a realistic user agent to avoid being blocked
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Performance optimizations
# Higher concurrency for faster scraping - allows 16 simultaneous requests
CONCURRENT_REQUESTS = 16

# Allow up to 8 concurrent requests per domain to avoid overwhelming servers
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Delay between requests to the same website (0.5 seconds minimum)
DOWNLOAD_DELAY = 0.5

# Randomize download delay (0.5 * to 1.5 * DOWNLOAD_DELAY) to appear more human-like
RANDOMIZE_DOWNLOAD_DELAY = True

# Timeout for each request (15 seconds)
DOWNLOAD_TIMEOUT = 15

# Enable AutoThrottle to automatically adjust delays based on response times
# This helps avoid overwhelming target servers and reduces chances of being blocked
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 3
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Disable cookies (saves memory and processing time since we don't need session persistence)
COOKIES_ENABLED = False

# Disable Telnet Console (saves memory)
TELNETCONSOLE_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fa,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

# Configure feeds to automatically export scraped data
# Results will be saved to results.json and overwritten each time
FEEDS = {
    'results.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'overwrite': True,
    },
}

# Configure pipelines
ITEM_PIPELINES = {
    'scrapy_project.pipelines.CleanPricePipeline': 300,
}

# Enable and configure the cache
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Reduce log level to avoid spam
LOG_LEVEL = 'INFO'