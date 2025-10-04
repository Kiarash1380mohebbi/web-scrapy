import streamlit as st
import pandas as pd
import subprocess
import os
import json
import time
from pathlib import Path


def main():
    """
    Main Streamlit application for the Iranian Product Search Engine.
    """
    # Set page configuration
    st.set_page_config(
        page_title="Iranian Product Search Engine",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Main title and description
    st.title("🛒 Iranian Product Search Engine")
    st.markdown("Search for products across major Iranian e-commerce websites")
    
    # Create input form
    with st.form("search_form"):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            query = st.text_input(
                "Enter your product search query:",
                placeholder="e.g., iPhone 14, لپ تاپ ایسوس, کتاب برنامه نویسی",
                help="Enter the product name in English or Persian"
            )
        
        with col2:
            st.write("")  # Add spacing
            search_button = st.form_submit_button("🔍 Search", use_container_width=True)
    
    # Handle search functionality
    if search_button and query.strip():
        search_products(query.strip())
    elif search_button and not query.strip():
        st.warning("⚠️ Please enter a search query")


def search_products(query):
    """
    Execute the product search using Scrapy spider.
    
    Args:
        query (str): The search query entered by user
    """
    # Display loading state
    with st.spinner("🔍 Searching for products... Please wait..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Clean up previous results
            results_file = Path("scrapy_project/results.json")
            if results_file.exists():
                results_file.unlink()
                status_text.text("🧹 Cleaning previous results...")
                progress_bar.progress(10)
            
            # Prepare the scrapy command
            status_text.text("🚀 Starting web scraping...")
            progress_bar.progress(20)
            
            # Change to scrapy project directory and run the spider
            scrapy_cmd = [
                os.path.expanduser("~/.local/bin/scrapy"), "crawl", "product_search", 
                "-a", f"query={query}",
                "-L", "WARNING"  # Reduce log verbosity
            ]
            
            status_text.text("🕷️ Crawling websites...")
            progress_bar.progress(40)
            
            # Execute scrapy command
            result = subprocess.run(
                scrapy_cmd,
                cwd="scrapy_project",  # Run from scrapy project directory
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            progress_bar.progress(80)
            status_text.text("📊 Processing results...")
            
            # Check for command execution errors
            if result.returncode != 0:
                st.error(f"❌ Error running scraper: {result.stderr}")
                return
            
            progress_bar.progress(90)
            
            # Load and display results
            display_results(query)
            progress_bar.progress(100)
            status_text.text("✅ Search completed!")
            
            # Clean up status elements after a short delay
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            
        except subprocess.TimeoutExpired:
            st.error("⏰ Search timed out. Please try again with a more specific query.")
        except FileNotFoundError:
            st.error("❌ Scrapy not found. Please ensure Scrapy is installed: `pip install scrapy`")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")


def display_results(query):
    """
    Load and display the scraped results in a Streamlit dataframe.
    
    Args:
        query (str): The original search query
    """
    results_file = Path("scrapy_project/results.json")
    
    if not results_file.exists():
        st.warning("🔍 No results file found. The search may not have completed successfully.")
        return
    
    try:
        # Read the results JSON file
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            st.info(f"🤷 No products found for '{query}'. Try a different search term.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Clean and format the dataframe
        df = clean_dataframe(df)
        
        if df.empty:
            st.info(f"🤷 No valid products found for '{query}'. Try a different search term.")
            return
        
        # Display results summary
        st.success(f"✅ Found {len(df)} products for '{query}'")
        
        # Display filter options
        display_filters(df)
        
    except json.JSONDecodeError:
        st.error("❌ Error reading results file. The data may be corrupted.")
    except Exception as e:
        st.error(f"❌ Error processing results: {str(e)}")


def clean_dataframe(df):
    """
    Clean and format the dataframe for better display.
    
    Args:
        df (pd.DataFrame): Raw dataframe from JSON
        
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    # Remove rows with missing essential data
    df = df.dropna(subset=['product_name'])
    
    # Clean product names
    df['product_name'] = df['product_name'].str.strip()
    df = df[df['product_name'].str.len() > 0]
    
    # Format price column
    if 'price' in df.columns:
        # Convert price to numeric, handling any remaining text
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        # Remove rows with invalid prices
        df = df.dropna(subset=['price'])
        # Format price display
        df['price_display'] = df['price'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
    
    # Ensure URL column exists
    if 'product_url' not in df.columns:
        df['product_url'] = ""
    
    # Reorder columns for better display
    column_order = ['product_name', 'price_display', 'store_name', 'product_url']
    available_columns = [col for col in column_order if col in df.columns]
    df = df[available_columns]
    
    # Rename columns for display
    df = df.rename(columns={
        'product_name': 'Product Name',
        'price_display': 'Price (Toman)',
        'store_name': 'Store',
        'product_url': 'Product Link'
    })
    
    return df


def display_filters(df):
    """
    Display the results with filtering and sorting options.
    
    Args:
        df (pd.DataFrame): Cleaned dataframe to display
    """
    # Add filtering options in sidebar
    with st.sidebar:
        st.header("🔧 Filter Options")
        
        # Store filter
        if 'Store' in df.columns:
            stores = df['Store'].unique()
            selected_stores = st.multiselect(
                "Select Stores:",
                options=stores,
                default=stores,
                help="Filter results by store"
            )
            df = df[df['Store'].isin(selected_stores)]
        
        # Price range filter
        if 'Price (Toman)' in df.columns and len(df) > 0:
            # Extract numeric prices for filtering
            numeric_prices = pd.to_numeric(df.index.map(lambda x: 
                df.loc[x, 'Price (Toman)'].replace(',', '') 
                if pd.notna(df.loc[x, 'Price (Toman)']) and df.loc[x, 'Price (Toman)'] != 'N/A' 
                else 0
            ), errors='coerce').fillna(0)
            
            if numeric_prices.max() > 0:
                min_price, max_price = st.slider(
                    "Price Range (Toman):",
                    min_value=int(numeric_prices.min()),
                    max_value=int(numeric_prices.max()),
                    value=(int(numeric_prices.min()), int(numeric_prices.max())),
                    help="Filter products by price range"
                )
                
                # Apply price filter
                price_mask = (numeric_prices >= min_price) & (numeric_prices <= max_price)
                df = df[price_mask]
        
        # Sort options
        sort_options = {
            "Price (Low to High)": ("price", True),
            "Price (High to Low)": ("price", False),
            "Product Name (A-Z)": ("Product Name", True),
            "Store Name": ("Store", True)
        }
        
        selected_sort = st.selectbox(
            "Sort by:",
            options=list(sort_options.keys()),
            help="Choose how to sort the results"
        )
    
    # Apply sorting
    if selected_sort in sort_options:
        sort_col, ascending = sort_options[selected_sort]
        if sort_col == "price" and 'Price (Toman)' in df.columns:
            # Sort by numeric price value
            df_copy = df.copy()
            df_copy['sort_price'] = pd.to_numeric(
                df_copy['Price (Toman)'].str.replace(',', ''),
                errors='coerce'
            ).fillna(0)
            df = df_copy.sort_values('sort_price', ascending=ascending).drop('sort_price', axis=1)
        elif sort_col in df.columns:
            df = df.sort_values(sort_col, ascending=ascending)
    
    # Display the results table
    if len(df) == 0:
        st.info("🔍 No products match your current filters.")
        return
    
    st.subheader(f"📊 Results ({len(df)} products)")
    
    # Convert URLs to clickable links
    if 'Product Link' in df.columns:
        df_display = df.copy()
        df_display['Product Link'] = df_display['Product Link'].apply(
            lambda x: f'<a href="{x}" target="_blank">🔗 View Product</a>' if pd.notna(x) and x else ''
        )
        
        # Display with clickable links
        st.write(
            df_display.to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
    else:
        # Display regular dataframe
        st.dataframe(df, use_container_width=True)
    
    # Download option
    if st.button("📥 Download Results as CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"product_search_results_{int(time.time())}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()