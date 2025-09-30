# Iranian Product Search Engine

A high-performance web scraping application that searches for products across major Iranian e-commerce websites using Scrapy and displays results in a beautiful Streamlit interface.

## Features

- 🛒 Search across multiple Iranian e-commerce sites (Torob, Emalls)
- 🚀 High-performance concurrent scraping with Scrapy
- 📊 Beautiful Streamlit web interface
- 🔧 Advanced filtering and sorting options
- 📥 Export results to CSV
- 🌐 Support for both English and Persian search terms

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. Open your browser and navigate to the displayed URL (usually `http://localhost:8501`)

## Usage

1. Enter your product search query in English or Persian
2. Click the "Search" button
3. Wait for the scraper to gather results from multiple websites
4. Use the sidebar filters to refine your results
5. Click on product links to visit the original store pages
6. Download results as CSV if needed

## Project Structure

```
.
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── scrapy.cfg                     # Scrapy configuration
├── scrapy_project/
│   ├── __init__.py
│   ├── settings.py                # Scrapy settings with performance optimizations
│   ├── items.py                   # Data structure definitions
│   ├── pipelines.py               # Data processing pipelines
│   └── spiders/
│       ├── __init__.py
│       └── product_spider.py      # Main spider for crawling websites
└── README.md                      # This file
```

## Technical Features

### Performance Optimizations
- Concurrent requests (16 simultaneous)
- AutoThrottle to avoid overloading servers
- Efficient CSS/XPath selectors
- Automatic price cleaning and normalization
- Robust error handling

### Supported Websites
- **Torob.com** - Price comparison site
- **Emalls.ir** - E-commerce marketplace

### Data Fields
- Product Name
- Price (automatically cleaned and formatted)
- Store Name
- Product URL

## Testing the Spider Directly

You can also test the Scrapy spider directly from the command line:

```bash
cd scrapy_project
scrapy crawl product_search -a query="iPhone 14"
```

Results will be saved to `results.json`.

## Troubleshooting

1. **No results found**: Try different search terms or check if the target websites are accessible
2. **Timeout errors**: The scraper has a 2-minute timeout; try more specific search terms
3. **Missing dependencies**: Run `pip install -r requirements.txt` to ensure all packages are installed

## Customization

### Adding New Websites
1. Add the domain to `allowed_domains` in `product_spider.py`
2. Add the search URL pattern to `start_urls` generation
3. Implement a new parsing method (e.g., `parse_newsite`)
4. Add the routing logic in the main `parse` method

### Modifying Selectors
Update the CSS selectors in the parsing methods if website structures change. Each selector is documented with comments explaining its purpose.

## Legal Notice

This tool is for educational and research purposes. Please respect the robots.txt files and terms of service of target websites. The tool includes automatic throttling and robots.txt compliance to be respectful to target servers.