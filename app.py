import streamlit as st
import pandas as pd
import subprocess
import os
import json


def main():
    """
    Main Streamlit application for the Iranian Product Search Engine.
    """
    # Set page configuration
    st.set_page_config(
        page_title="Iranian Product Search Engine",
        page_icon="🛒",
        layout="wide"
    )
    
    # Display title and description
    st.title("🛒 Iranian Product Search Engine")
    st.markdown("""
    Search for products across multiple Iranian e-commerce websites including:
    - **Torob** - Price comparison platform
    - **Emalls** - Online shopping marketplace
    """)
    
    # Create search input
    search_query = st.text_input(
        "Enter product name to search:",
        placeholder="e.g., لپ تاپ, گوشی موبایل, هدفون"
    )
    
    # Create search button
    if st.button("🔍 Search", type="primary"):
        if not search_query.strip():
            st.warning("⚠️ Please enter a product name to search.")
            return
        
        # Sanitize the search query
        sanitized_query = search_query.strip()
        
        # Display searching status
        with st.spinner("🔄 Searching... please wait."):
            # Define paths
            scrapy_project_dir = os.path.join(os.getcwd(), "scrapy_project")
            results_file = os.path.join(scrapy_project_dir, "results.json")
            
            # Delete existing results file to ensure fresh results
            if os.path.exists(results_file):
                try:
                    os.remove(results_file)
                    st.info("🗑️ Cleared previous search results.")
                except Exception as e:
                    st.error(f"Error clearing previous results: {str(e)}")
            
            # Run the Scrapy spider
            try:
                # Build the command
                command = [
                    "scrapy", "crawl", "product_search",
                    "-a", f"query={sanitized_query}"
                ]
                
                # Execute the command from the scrapy_project directory
                result = subprocess.run(
                    command,
                    cwd=scrapy_project_dir,
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minute timeout
                )
                
                # Check if the command was successful
                if result.returncode != 0:
                    st.error("❌ Error running the scraper.")
                    st.error(f"Error details: {result.stderr}")
                    return
                
            except subprocess.TimeoutExpired:
                st.error("⏱️ Search timed out. Please try again with a more specific query.")
                return
            except Exception as e:
                st.error(f"❌ Error running scraper: {str(e)}")
                return
        
        # Read and display results
        if os.path.exists(results_file):
            try:
                # Read the JSON file
                with open(results_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if we have results
                if not data or len(data) == 0:
                    st.warning("😔 No results found. Try a different search term.")
                    return
                
                # Convert to DataFrame
                df = pd.DataFrame(data)
                
                # Display success message
                st.success(f"✅ Found {len(df)} products!")
                
                # Clean up and format the price column for better display
                if 'price' in df.columns:
                    df['price'] = df['price'].apply(lambda x: f"{int(x):,}" if x > 0 else "N/A")
                
                # Reorder columns for better presentation
                column_order = ['product_name', 'price', 'store_name', 'product_url']
                df = df[column_order]
                
                # Rename columns for better display
                df.columns = ['Product Name', 'Price (Toman)', 'Store', 'Product URL']
                
                # Display the DataFrame with clickable links
                st.dataframe(
                    df,
                    column_config={
                        "Product URL": st.column_config.LinkColumn(
                            "Product URL",
                            help="Click to view product",
                            display_text="View Product"
                        ),
                        "Product Name": st.column_config.TextColumn(
                            "Product Name",
                            width="large"
                        ),
                        "Price (Toman)": st.column_config.TextColumn(
                            "Price (Toman)",
                            width="medium"
                        ),
                        "Store": st.column_config.TextColumn(
                            "Store",
                            width="small"
                        )
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Option to download results as CSV
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Download results as CSV",
                    data=csv,
                    file_name=f"product_search_{sanitized_query}.csv",
                    mime="text/csv",
                )
                
            except json.JSONDecodeError:
                st.error("❌ Error reading results. The results file may be corrupted.")
            except Exception as e:
                st.error(f"❌ Error displaying results: {str(e)}")
        else:
            st.warning("😔 No results found. The search may have failed or no products matched your query.")
    
    # Add footer with instructions
    st.markdown("---")
    st.markdown("""
    ### How to use:
    1. Enter a product name in Persian or English
    2. Click the Search button
    3. Wait for results from multiple websites
    4. View prices and click links to visit product pages
    
    **Note:** Search results depend on website availability and structure.
    """)


if __name__ == "__main__":
    main()