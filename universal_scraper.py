#!/usr/bin/env python3
"""
🌐 UNIVERSAL WEB SCRAPER
Scrape ANY website - Auto-detects structure and extracts data intelligently
"""

import argparse
import json
import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv


class UniversalScraper:
    """
    Universal web scraper that adapts to any website structure
    """
    
    def __init__(self, headless=True, wait_time=3):
        self.headless = headless
        self.wait_time = wait_time
        self.data = []
        
    def scrape_url(self, url, config=None):
        """
        Scrape a single URL
        
        Args:
            url: URL to scrape
            config: Optional configuration dict with:
                - selectors: CSS selectors to find data
                - pagination: How to handle multiple pages
                - depth: How many levels deep to crawl
        """
        print(f"\n{'='*60}")
        print(f"🌐 SCRAPING: {url}")
        print(f"{'='*60}\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = context.new_page()
            
            try:
                # Load page
                print(f"Loading page...")
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(self.wait_time)
                
                # Handle common popups
                self._handle_popups(page)
                
                # Get page content
                html = page.content()
                soup = BeautifulSoup(html, "lxml")
                
                # Auto-detect or use provided selectors
                if config and 'selectors' in config:
                    data = self._scrape_with_selectors(soup, config['selectors'])
                else:
                    data = self._auto_detect_and_scrape(soup, page, url)
                
                # Handle pagination if needed
                if config and config.get('pagination'):
                    data.extend(self._handle_pagination(page, soup, config))
                
                self.data.extend(data)
                
                print(f"\n✓ Scraped {len(data)} items from {url}")
                
            except Exception as e:
                print(f"✗ Error scraping {url}: {e}")
                import traceback
                traceback.print_exc()
            finally:
                browser.close()
        
        return self.data
    
    def _handle_popups(self, page):
        """Handle common popups (cookies, newsletters, etc.)"""
        common_popup_buttons = [
            "button:has-text('Accept')",
            "button:has-text('I Accept')",
            "button:has-text('Agree')",
            "button:has-text('Close')",
            "button:has-text('No thanks')",
            "[class*='close']",
            "[class*='dismiss']"
        ]
        
        for selector in common_popup_buttons:
            try:
                page.click(selector, timeout=2000)
                time.sleep(0.5)
            except:
                pass
    
    def _auto_detect_and_scrape(self, soup, page, url):
        """
        Automatically detect page structure and scrape intelligently
        """
        print("🤖 Auto-detecting page structure...")
        
        data = []
        
        # Detect page type
        page_type = self._detect_page_type(soup, url)
        print(f"   Detected: {page_type}")
        
        if page_type == "table":
            data = self._scrape_tables(soup)
        elif page_type == "list":
            data = self._scrape_lists(soup)
        elif page_type == "cards":
            data = self._scrape_cards(soup)
        elif page_type == "article":
            data = [self._scrape_article(soup, url)]
        elif page_type == "ecommerce":
            data = self._scrape_products(soup)
        else:
            # Generic extraction
            data = self._scrape_generic(soup)
        
        return data
    
    def _detect_page_type(self, soup, url):
        """Detect what type of page this is"""
        
        # Check for tables
        tables = soup.find_all('table')
        if len(tables) > 0:
            # Check if table has data (more than headers)
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 2:  # Header + at least 2 data rows
                    return "table"
        
        # Check for product listings (ecommerce)
        ecommerce_indicators = ['product', 'item', 'price', 'cart', 'buy']
        page_text = soup.get_text().lower()
        if any(indicator in page_text for indicator in ecommerce_indicators):
            products = soup.find_all(class_=re.compile(r'product|item'))
            if len(products) > 3:
                return "ecommerce"
        
        # Check for cards/grid layout
        card_selectors = [
            soup.find_all(class_=re.compile(r'card')),
            soup.find_all(class_=re.compile(r'tile')),
            soup.find_all(class_=re.compile(r'grid-item'))
        ]
        for cards in card_selectors:
            if len(cards) > 3:
                return "cards"
        
        # Check for lists
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            if len(items) > 5:  # Significant list
                return "list"
        
        # Check for article/blog post
        article_indicators = ['article', 'post', 'blog', 'content']
        if soup.find('article') or any(soup.find(class_=re.compile(indicator)) for indicator in article_indicators):
            return "article"
        
        return "generic"
    
    def _scrape_tables(self, soup):
        """Extract data from HTML tables"""
        print("   Extracting tables...")
        
        all_data = []
        tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            
            if len(rows) < 2:
                continue
            
            # Extract headers
            headers = []
            header_row = rows[0]
            for cell in header_row.find_all(['th', 'td']):
                headers.append(cell.get_text(strip=True))
            
            # If no headers found, create generic ones
            if not headers or all(h == '' for h in headers):
                headers = [f"Column_{i+1}" for i in range(len(rows[0].find_all(['th', 'td'])))]
            
            # Extract data rows
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 0:
                    continue
                
                row_data = {}
                for idx, cell in enumerate(cells):
                    if idx < len(headers):
                        row_data[headers[idx]] = cell.get_text(strip=True)
                
                if row_data:  # Only add if we got data
                    row_data['_table_index'] = table_idx
                    all_data.append(row_data)
        
        print(f"   ✓ Found {len(all_data)} rows across {len(tables)} tables")
        return all_data
    
    def _scrape_lists(self, soup):
        """Extract data from lists (ul/ol)"""
        print("   Extracting lists...")
        
        all_data = []
        lists = soup.find_all(['ul', 'ol'])
        
        for list_idx, lst in enumerate(lists):
            items = lst.find_all('li', recursive=False)  # Direct children only
            
            if len(items) < 3:  # Skip small lists (likely navigation)
                continue
            
            for item_idx, item in enumerate(items):
                item_data = {
                    'text': item.get_text(strip=True),
                    '_list_index': list_idx,
                    '_item_index': item_idx
                }
                
                # Extract links if present
                link = item.find('a')
                if link and link.get('href'):
                    item_data['link'] = link.get('href')
                
                all_data.append(item_data)
        
        print(f"   ✓ Found {len(all_data)} list items")
        return all_data
    
    def _scrape_cards(self, soup):
        """Extract data from card-based layouts"""
        print("   Extracting cards...")
        
        all_data = []
        
        # Find cards using various selectors
        card_selectors = [
            {'class': re.compile(r'card')},
            {'class': re.compile(r'tile')},
            {'class': re.compile(r'grid-item')},
            {'class': re.compile(r'box')}
        ]
        
        cards = []
        for selector in card_selectors:
            found = soup.find_all('div', selector)
            if len(found) > len(cards):
                cards = found
        
        for card_idx, card in enumerate(cards):
            card_data = {'_card_index': card_idx}
            
            # Extract title
            title = (card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or
                    card.find(class_=re.compile(r'title|heading')))
            if title:
                card_data['title'] = title.get_text(strip=True)
            
            # Extract description
            desc = card.find(class_=re.compile(r'description|excerpt|summary'))
            if desc:
                card_data['description'] = desc.get_text(strip=True)
            
            # Extract link
            link = card.find('a')
            if link and link.get('href'):
                card_data['link'] = link.get('href')
            
            # Extract image
            img = card.find('img')
            if img:
                card_data['image'] = img.get('src') or img.get('data-src')
            
            # Extract all text as fallback
            if 'title' not in card_data:
                card_data['text'] = card.get_text(strip=True)[:200]
            
            all_data.append(card_data)
        
        print(f"   ✓ Found {len(all_data)} cards")
        return all_data
    
    def _scrape_article(self, soup, url):
        """Extract article/blog post content"""
        print("   Extracting article...")
        
        article_data = {'url': url}
        
        # Extract title
        title = (soup.find('h1') or 
                soup.find(class_=re.compile(r'title')) or
                soup.find('title'))
        if title:
            article_data['title'] = title.get_text(strip=True)
        
        # Extract author
        author = soup.find(class_=re.compile(r'author|byline|writer'))
        if author:
            article_data['author'] = author.get_text(strip=True)
        
        # Extract date
        date = soup.find(['time', 'date']) or soup.find(class_=re.compile(r'date|published'))
        if date:
            article_data['date'] = date.get_text(strip=True)
        
        # Extract content
        content = (soup.find('article') or
                  soup.find(class_=re.compile(r'content|article|post-body')) or
                  soup.find('main'))
        if content:
            # Get paragraphs
            paragraphs = content.find_all('p')
            article_data['content'] = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
            article_data['word_count'] = len(article_data['content'].split())
        
        # Extract images
        images = soup.find_all('img')
        article_data['images'] = [img.get('src') or img.get('data-src') for img in images if img.get('src') or img.get('data-src')]
        
        return article_data
    
    def _scrape_products(self, soup):
        """Extract product listings (ecommerce)"""
        print("   Extracting products...")
        
        all_data = []
        
        # Find product containers
        products = soup.find_all(class_=re.compile(r'product|item'))
        
        for prod_idx, product in enumerate(products):
            prod_data = {'_product_index': prod_idx}
            
            # Extract product name
            name = (product.find(class_=re.compile(r'product.*name|title')) or
                   product.find(['h2', 'h3', 'h4']))
            if name:
                prod_data['name'] = name.get_text(strip=True)
            
            # Extract price
            price = product.find(class_=re.compile(r'price'))
            if price:
                prod_data['price'] = price.get_text(strip=True)
            
            # Extract rating
            rating = product.find(class_=re.compile(r'rating|stars'))
            if rating:
                prod_data['rating'] = rating.get_text(strip=True)
            
            # Extract link
            link = product.find('a')
            if link and link.get('href'):
                prod_data['link'] = link.get('href')
            
            # Extract image
            img = product.find('img')
            if img:
                prod_data['image'] = img.get('src') or img.get('data-src')
            
            if prod_data.get('name') or prod_data.get('price'):
                all_data.append(prod_data)
        
        print(f"   ✓ Found {len(all_data)} products")
        return all_data
    
    def _scrape_generic(self, soup):
        """Generic extraction - get all meaningful content"""
        print("   Using generic extraction...")
        
        data = []
        
        # Extract all headings with their content
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            item = {
                'type': heading.name,
                'text': heading.get_text(strip=True)
            }
            
            # Get next sibling content
            sibling = heading.find_next_sibling()
            if sibling:
                item['content'] = sibling.get_text(strip=True)[:500]
            
            data.append(item)
        
        # Extract all links
        links = soup.find_all('a', href=True)
        unique_links = {}
        for link in links:
            href = link.get('href')
            text = link.get_text(strip=True)
            if href and text and len(text) > 2:
                unique_links[href] = text
        
        if unique_links:
            data.append({
                'type': 'links',
                'links': [{'url': k, 'text': v} for k, v in unique_links.items()]
            })
        
        print(f"   ✓ Extracted {len(data)} generic elements")
        return data
    
    def _scrape_with_selectors(self, soup, selectors):
        """Scrape using provided CSS selectors"""
        print("   Using custom selectors...")
        
        data = []
        
        # Find all elements matching the main selector
        main_selector = selectors.get('container', 'body')
        containers = soup.select(main_selector)
        
        for container in containers:
            item = {}
            
            # Extract each field
            for field_name, selector in selectors.items():
                if field_name == 'container':
                    continue
                
                elem = container.select_one(selector)
                if elem:
                    item[field_name] = elem.get_text(strip=True)
            
            if item:
                data.append(item)
        
        print(f"   ✓ Extracted {len(data)} items with custom selectors")
        return data
    
    def _handle_pagination(self, page, soup, config):
        """Handle pagination to scrape multiple pages"""
        all_data = []
        max_pages = config.get('max_pages', 5)
        
        for page_num in range(2, max_pages + 1):
            print(f"\n   Loading page {page_num}...")
            
            # Try to find and click next button
            next_selectors = [
                "a:has-text('Next')",
                "a[class*='next']",
                "[class*='pagination'] a:last-child",
                config.get('next_button')
            ]
            
            clicked = False
            for selector in next_selectors:
                if not selector:
                    continue
                try:
                    page.click(selector, timeout=5000)
                    clicked = True
                    time.sleep(self.wait_time)
                    break
                except:
                    continue
            
            if not clicked:
                print(f"   No more pages found")
                break
            
            # Scrape this page
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            page_data = self._auto_detect_and_scrape(soup, page, page.url)
            all_data.extend(page_data)
        
        return all_data
    
    def save_to_json(self, filename):
        """Save scraped data to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved {len(self.data)} items to {filename}")
    
    def save_to_csv(self, filename):
        """Save scraped data to CSV"""
        if not self.data:
            print("No data to save")
            return
        
        # Get all unique keys
        all_keys = set()
        for item in self.data:
            all_keys.update(item.keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(self.data)
        
        print(f"\n✓ Saved {len(self.data)} items to {filename}")
    
    def print_summary(self):
        """Print summary of scraped data"""
        print(f"\n{'='*60}")
        print(f"📊 SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total items: {len(self.data)}")
        
        if self.data:
            print(f"\nFirst item preview:")
            print(json.dumps(self.data[0], indent=2, ensure_ascii=False)[:500])
            print("...")


def main():
    parser = argparse.ArgumentParser(
        description="🌐 Universal Web Scraper - Scrape ANY website!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a website (auto-detect structure)
  python universal_scraper.py -u "https://example.com"
  
  # Scrape and save to JSON
  python universal_scraper.py -u "https://example.com" -o data.json
  
  # Scrape and save to CSV
  python universal_scraper.py -u "https://example.com" -o data.csv
  
  # Scrape with pagination (max 10 pages)
  python universal_scraper.py -u "https://example.com" --pages 10
  
  # Show browser while scraping
  python universal_scraper.py -u "https://example.com" --no-headless
  
  # Use custom CSS selectors
  python universal_scraper.py -u "https://example.com" --config config.json
        """
    )
    
    parser.add_argument("-u", "--url", required=True, help="URL to scrape")
    parser.add_argument("-o", "--output", help="Output file (JSON or CSV)")
    parser.add_argument("--pages", type=int, help="Max pages to scrape (pagination)")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode (default)")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    parser.add_argument("--config", help="JSON config file with custom selectors")
    parser.add_argument("--wait", type=int, default=3, help="Wait time in seconds (default: 3)")
    
    args = parser.parse_args()
    
    # Load config if provided
    config = None
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Add pagination to config
    if args.pages:
        if not config:
            config = {}
        config['pagination'] = True
        config['max_pages'] = args.pages
    
    # Create scraper
    scraper = UniversalScraper(
        headless=not args.no_headless,
        wait_time=args.wait
    )
    
    # Scrape
    scraper.scrape_url(args.url, config=config)
    
    # Print summary
    scraper.print_summary()
    
    # Save output
    if args.output:
        if args.output.endswith('.json'):
            scraper.save_to_json(args.output)
        elif args.output.endswith('.csv'):
            scraper.save_to_csv(args.output)
        else:
            print(f"Unknown output format. Use .json or .csv")
            scraper.save_to_json(args.output + '.json')
    else:
        # Default: save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scraper.save_to_json(f"scraped_data_{timestamp}.json")


if __name__ == "__main__":
    main()
