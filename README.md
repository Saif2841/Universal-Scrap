# 🌐 Universal Web Scraper

**Scrape ANY website on the internet** - Automatically detects page structure and extracts data intelligently!

## 🚀 Features

- ✅ **Auto-Detection** - Automatically identifies tables, lists, cards, articles, products
- ✅ **No Configuration Needed** - Works out of the box for most websites
- ✅ **Custom Selectors** - Use CSS selectors for precise extraction
- ✅ **Pagination Support** - Automatically scrapes multiple pages
- ✅ **Multiple Output Formats** - JSON, CSV
- ✅ **Smart Popup Handling** - Automatically dismisses cookie banners, etc.
- ✅ **Works for**:
  - 📰 News sites & blogs
  - 🛒 Ecommerce/shopping sites
  - 📊 Data tables & statistics
  - 🏠 Real estate listings
  - 💼 Job boards
  - 🍔 Restaurants & reviews
  - ⚽ Sports scores & stats
  - 🎓 Academic papers
  - 📱 Social media (public content)
  - And literally any website!

## 📦 Installation

```bash
pip install playwright beautifulsoup4 lxml

# Install browser
playwright install chromium
```

## 🎯 Quick Start

### 1. Auto-Scrape Any Website (Simplest)

```bash
# Just provide the URL - it figures out the rest!
python universal_scraper.py -u "https://example.com"

# Saves to: scraped_data_TIMESTAMP.json
```

### 2. Save to Specific File

```bash
# Save as JSON
python universal_scraper.py -u "https://example.com" -o mydata.json

# Save as CSV
python universal_scraper.py -u "https://example.com" -o mydata.csv
```

### 3. Scrape Multiple Pages (Pagination)

```bash
# Scrape up to 10 pages
python universal_scraper.py -u "https://example.com/products" --pages 10
```

### 4. Show Browser (Debug Mode)

```bash
# See what's happening
python universal_scraper.py -u "https://example.com" --no-headless
```

## 🎨 Real-World Examples

### Example 1: Scrape News Articles

```bash
python universal_scraper.py -u "https://news-website.com" -o news.json
```

**Result:**
```json
[
  {
    "title": "Breaking News Title",
    "author": "John Doe",
    "date": "2024-02-15",
    "content": "Article content here...",
    "images": ["https://..."]
  }
]
```

### Example 2: Scrape Product Listings

```bash
python universal_scraper.py -u "https://shop.com/products" --pages 5 -o products.csv
```

**Result (CSV):**
```
name,price,rating,link,image
Product 1,$29.99,4.5,https://...,https://...
Product 2,$49.99,4.8,https://...,https://...
```

### Example 3: Scrape Data Tables

```bash
python universal_scraper.py -u "https://stats-website.com/table" -o data.json
```

**Auto-detects tables and extracts:**
```json
[
  {
    "Column_1": "Value 1",
    "Column_2": "Value 2",
    "Column_3": "Value 3"
  }
]
```

### Example 4: Scrape Job Listings

```bash
python universal_scraper.py -u "https://jobs-site.com" --pages 10 -o jobs.csv
```

### Example 5: Scrape Restaurant Data

```bash
python universal_scraper.py -u "https://restaurant-reviews.com" -o restaurants.json
```

## 🔧 Advanced Usage: Custom Selectors

For precise control, create a config file with CSS selectors:

### Create config.json:

```json
{
  "container": ".product-item",
  "name": ".product-title",
  "price": ".price",
  "rating": ".stars",
  "link": "a",
  "image": "img",
  "pagination": true,
  "max_pages": 10
}
```

### Run with config:

```bash
python universal_scraper.py -u "https://example.com" --config config.json -o output.json
```

## 📚 Configuration Examples

### Ecommerce Products
```json
{
  "container": ".product",
  "name": "h3.product-name",
  "price": ".price",
  "rating": ".rating",
  "reviews": ".review-count",
  "link": "a.product-link"
}
```

### News Articles
```json
{
  "container": ".article",
  "title": "h2.headline",
  "date": ".publish-date",
  "author": ".byline",
  "excerpt": ".summary",
  "link": "a.read-more"
}
```

### Job Listings
```json
{
  "container": ".job-posting",
  "title": ".job-title",
  "company": ".company-name",
  "location": ".job-location",
  "salary": ".salary-range",
  "posted_date": ".post-date"
}
```

### Real Estate
```json
{
  "container": ".property",
  "address": ".property-address",
  "price": ".list-price",
  "bedrooms": ".bed-count",
  "bathrooms": ".bath-count",
  "sqft": ".square-feet"
}
```

## 🤖 Auto-Detection Types

The scraper automatically identifies and extracts:

1. **Tables** - Data in `<table>` tags
2. **Lists** - Items in `<ul>` or `<ol>`
3. **Cards** - Grid/card layouts
4. **Articles** - Blog posts, news articles
5. **Products** - Ecommerce listings
6. **Generic** - Headings, links, content blocks

## ⚙️ All Options

```bash
python universal_scraper.py --help

Options:
  -u, --url URL          URL to scrape (required)
  -o, --output FILE      Output file (.json or .csv)
  --pages N              Max pages to scrape (pagination)
  --headless             Run in headless mode (default)
  --no-headless          Show browser window
  --config FILE          JSON config with custom selectors
  --wait N               Wait time in seconds (default: 3)
```

## 💡 Tips & Tricks

### 1. Start Simple
```bash
# Let it auto-detect first
python universal_scraper.py -u "https://example.com" -o test.json

# Check test.json to see what it found
# Then create custom config if needed
```

### 2. Use Browser Mode for Testing
```bash
# See what's happening
python universal_scraper.py -u "https://example.com" --no-headless

# Watch it scrape in real-time!
```

### 3. Scrape Multiple Pages
```bash
# For paginated content (product catalogs, search results, etc.)
python universal_scraper.py -u "https://example.com/page1" --pages 20
```

### 4. Increase Wait Time for Slow Sites
```bash
# If content loads slowly
python universal_scraper.py -u "https://slow-site.com" --wait 10
```

### 5. Find CSS Selectors
```
1. Right-click element in browser → Inspect
2. Right-click in DevTools → Copy → Copy selector
3. Use in config.json
```

## 🌟 Use Cases

### Business Intelligence
- Competitor price monitoring
- Market research
- Product catalog updates

### Research
- Academic paper collection
- Statistics gathering
- Data analysis

### Personal
- Job hunting (scrape listings)
- Real estate search
- News aggregation
- Recipe collection

### Development
- Test data generation
- Content migration
- API alternatives

## ⚠️ Important Notes

### Legal & Ethical
- ✅ Check website's `robots.txt`
- ✅ Respect rate limits
- ✅ Only scrape public data
- ✅ Check Terms of Service
- ❌ Don't overload servers
- ❌ Don't scrape private/login-required data

### Best Practices
- Start with small tests (1-2 pages)
- Use `--wait` for slow sites
- Save data frequently
- Don't scrape too fast
- Be a good web citizen!

## 🔍 Troubleshooting

### "No data found"
- Use `--no-headless` to see the page
- Check if site requires login
- Increase `--wait` time
- Create custom config with selectors

### "Timeout errors"
- Site might be slow - increase `--wait`
- Check internet connection
- Try again later

### "Wrong data extracted"
- Create custom config file
- Use browser DevTools to find correct selectors

## 📊 Output Formats

### JSON (Structured)
```json
[
  {
    "field1": "value1",
    "field2": "value2"
  }
]
```

### CSV (Spreadsheet-friendly)
```
field1,field2,field3
value1,value2,value3
```

## 🎓 Learning Resources

### Finding CSS Selectors:
1. Open page in Chrome/Firefox
2. Right-click element → Inspect
3. Right-click in DevTools → Copy Selector
4. Use in config.json

### Common Selectors:
- `.classname` - Elements with class
- `#id` - Element with ID
- `tag` - HTML tag (div, span, etc.)
- `parent child` - Nested elements
- `[attribute="value"]` - By attribute

## 🚀 Quick Examples

```bash
# News site
python universal_scraper.py -u "https://news.com" -o news.json

# Shopping site
python universal_scraper.py -u "https://shop.com/products" --pages 10 -o products.csv

# Job board
python universal_scraper.py -u "https://jobs.com" --pages 5 -o jobs.json

# Restaurant reviews
python universal_scraper.py -u "https://reviews.com/restaurants" -o food.json

# Real estate
python universal_scraper.py -u "https://realestate.com/listings" --pages 20 -o homes.csv

# Sports scores
python universal_scraper.py -u "https://sports.com/scores" -o scores.json

# Academic papers
python universal_scraper.py -u "https://scholar.com/search?q=AI" --pages 5 -o papers.json
```

## 🎉 That's It!

You now have a universal scraper that works on **any website**. Just change the URL and scrape away!

```bash
# The only command you need:
python universal_scraper.py -u "YOUR_URL_HERE" -o output.json
```

**Happy Scraping! 🕷️**

---

**Made with ❤️ for data enthusiasts**

*Remember: Always respect websites' Terms of Service and robots.txt!*
