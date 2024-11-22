import asyncio
import random
import time
from flask import Flask, jsonify, request
from playwright.async_api import async_playwright, expect


from playwright.async_api import async_playwright
import asyncio



async def get_amazon_product_details(page, url):
    try:
        await page.goto(url)
        
        # Selectors for price and offers
        price_selector = "#corePriceDisplay_desktop_feature_div > div.a-section.a-spacing-none.aok-align-center.aok-relative"
        # offer_selector = "#vsxoffers_feature_div > div > dptags:querylogoperation > div > div.a-cardui-deck > div.a-cardui.vsx__offers-holder > div > div.a-section.vsx__offers.multipleProducts"
        
        # Wait for the price element to load
        await page.wait_for_selector(price_selector, timeout=10000)
        price_element = page.locator(price_selector)
        price = await price_element.inner_text() if await price_element.count() > 0 else "Price not available"
        
        # # Wait for the offer element to load
        # offers = "Offer not available"
        # if await page.locator(offer_selector).count() > 0:
        #     await page.wait_for_selector(offer_selector, timeout=10000)
        #     offer_element = page.locator(offer_selector)
        #     offers = await offer_element.inner_text() if await offer_element.count() > 0 else "Offer not available"
        
        return [url, "Amazon", price, "offers"]
    
    except Exception as e:
        return {"url": url, "error": f"Amazon Scraping Error: {str(e)}"}






async def get_flipkart_product_details(page, url):
    try:
        await page.goto(url)
        price_selector = "#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div:nth-child(2) > div"
        offer_selector = "#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div:nth-child(3)"
        
        # Wait for the elements to load
        await page.wait_for_selector(price_selector, timeout=10000)
        await page.wait_for_selector(offer_selector, timeout=10000)

        # Price
        price_element = page.locator(price_selector)
        price = await price_element.inner_text() if await price_element.count() > 0 else "Price not available"
        
        # Offers
        offer_element = page.locator(offer_selector)
        offer = await offer_element.inner_text() if await offer_element.count() > 0 else "Offer not available"

        return [url, "Flipkart", price, offer]

    except Exception as e:
        return {"url": url, "error": f"Flipkart Scraping Error: {str(e)}"}

async def scrape_product(browser, url, platform):
    page = await browser.new_page()
    result = None
    if platform == 'amazon':
        result = await get_amazon_product_details(page, url)
    elif platform == 'flipkart':
        result = await get_flipkart_product_details(page, url)
    await page.close()
    return result

async def scrape_all_products(collection):
    """Scrape all products concurrently."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        tasks = []
        for platform, url in collection.items():
            tasks.append(scrape_product(browser, url, platform))
        
        results = await asyncio.gather(*tasks)

        await browser.close()
        return results




# Flask app
app = Flask(__name__)

# Endpoint to process the device name
@app.route('/process_device', methods=['POST'])
def process_device():
    data = request.json
    collection = data.get('collection', '')
    if not collection:
        return jsonify({'error': 'Device name is required'}), 400
    
    
    flipkart_results = asyncio.run(scrape_all_products(collection))

    return jsonify({'device_info': flipkart_results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)