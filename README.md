# Iranian Product Search Engine 🛒

A high-performance web scraping application that searches for products across multiple Iranian e-commerce websites in parallel.

## Features

- **Multi-site Scraping**: Searches across Torob and Emalls simultaneously
- **Modern UI**: Clean Streamlit interface with real-time results
- **High Performance**: Optimized Scrapy settings for fast concurrent requests
- **Export Results**: Download search results as CSV
- **Robust Parsing**: Error handling and fallback selectors

## Tech Stack

- **Frontend**: Streamlit
- **Scraping**: Scrapy
- **Data Processing**: Pandas

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser to the provided URL (usually `http://localhost:8501`)

3. Enter a product name in the search box (supports Persian and English)

4. Click "Search" and wait for results

5. View results in a formatted table with clickable product links

6. Optionally download results as CSV

## Project Structure

```
.
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── scrapy_project/
│   ├── scrapy.cfg                 # Scrapy configuration
│   └── scrapy_project/
│       ├── __init__.py
│       ├── settings.py            # Scrapy settings with performance optimizations
│       ├── items.py               # Data structure definitions
│       └── spiders/
│           ├── __init__.py
│           └── product_spider.py  # Main spider with parsing logic
└── README.md
```

## Scrapy Settings Highlights

- **Concurrent Requests**: 16 (for fast parallel scraping)
- **Per-Domain Concurrency**: 8 requests
- **AutoThrottle**: Enabled to prevent server overload
- **Download Timeout**: 15 seconds
- **Cookies**: Disabled for reduced overhead
- **Results Export**: Automatic JSON export to `results.json`

## Supported Websites

1. **Torob** (torob.com) - Price comparison platform
2. **Emalls** (emalls.ir) - Online shopping marketplace

## Notes

- The spider respects `robots.txt` rules
- CSS selectors include fallbacks for different page structures
- Prices are automatically cleaned and formatted
- Search queries are URL-encoded for safety
- The app clears previous results before each new search

## Troubleshooting

If you encounter issues:

1. **No results found**: The website structure may have changed. Check the CSS selectors in `product_spider.py`
2. **Timeout errors**: Increase the timeout in `app.py` or reduce concurrent requests in `settings.py`
3. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

## Future Enhancements

- Add more Iranian e-commerce sites
- Implement price filtering and sorting
- Add product image display
- Create price history tracking
- Add export to Excel format