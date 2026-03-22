"""X/Twitter content scraper using Playwright.

ESSENTIAL COMPONENT - See ARCHITECTURE.md before modifying.
Fetches tweet content from X URLs when direct scraping is blocked.
"""
from __future__ import annotations

import logging
from typing import Optional

LOGGER = logging.getLogger(__name__)


class XScraper:
    """Scrape X/Twitter content using Playwright headless browser."""
    
    def __init__(self):
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    async def fetch_tweet(self, url: str) -> dict:
        """Fetch tweet content from X URL.
        
        Returns:
            dict with keys: text, author, title, success, error
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            LOGGER.error("Playwright not installed. Run: pip install playwright")
            return self._error_result("Playwright not installed")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                context = await browser.new_context(
                    user_agent=self.user_agent,
                    viewport={"width": 1280, "height": 800},
                    locale="en-US"
                )
                
                # Block images to speed up loading
                await context.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())
                
                page = await context.new_page()
                
                # Navigate to tweet
                LOGGER.info(f"Fetching X content: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Wait for any of these selectors
                selectors = [
                    "article[data-testid='tweet']",
                    "[data-testid='tweet']",
                    "article[role='article']",
                    "article"
                ]
                
                found_selector = None
                for selector in selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        found_selector = selector
                        LOGGER.info(f"Found selector: {selector}")
                        break
                    except:
                        continue
                
                if not found_selector:
                    # Try to get any text from the page
                    page_text = await page.inner_text("body")
                    LOGGER.warning(f"No tweet selector found. Page text: {page_text[:200]}")
                    await browser.close()
                    return self._error_result("Could not find tweet on page - X may require login")
                
                # Try multiple text selectors
                text_selectors = [
                    f"{found_selector} div[data-testid='tweetText']",
                    f"{found_selector} [lang]",
                    f"{found_selector} div[dir='auto']",
                    found_selector
                ]
                
                tweet_text = ""
                for text_selector in text_selectors:
                    try:
                        elem = await page.query_selector(text_selector)
                        if elem:
                            tweet_text = await elem.inner_text()
                            if tweet_text.strip():
                                LOGGER.info(f"Found text using: {text_selector}")
                                break
                    except:
                        continue
                
                # Extract author
                author = None
                try:
                    # Try to get author from URL or page
                    author_elem = await page.query_selector("a[href^='/'] [data-testid='User-Name']")
                    if author_elem:
                        author = await author_elem.inner_text()
                    else:
                        # Extract from URL
                        parts = url.split('/')
                        if len(parts) > 3:
                            author = parts[3]
                except:
                    pass
                
                await browser.close()
                
                if tweet_text.strip():
                    return {
                        "success": True,
                        "text": tweet_text.strip(),
                        "author": author,
                        "title": self._generate_title(tweet_text.strip()),
                        "error": None
                    }
                else:
                    return self._error_result("Tweet text is empty - X may require login")
                
        except Exception as e:
            LOGGER.exception(f"Failed to fetch X content: {url}")
            return self._error_result(str(e))
    
    def _generate_title(self, text: str, max_length: int = 80) -> str:
        """Generate title from tweet text."""
        if not text:
            return "X Post"
        
        first_line = text.split('\n')[0].strip()
        
        # Look for sentence end
        for punct in ['. ', '? ', '! ']:
            idx = first_line[:max_length].rfind(punct)
            if idx > 20:
                return first_line[:idx + 1].strip()
        
        # Word boundary
        if len(first_line) > max_length:
            truncated = first_line[:max_length]
            last_space = truncated.rfind(' ')
            if last_space > 30:
                return truncated[:last_space].strip() + "..."
        
        return first_line[:max_length]
    
    def _error_result(self, error: str) -> dict:
        return {
            "success": False,
            "text": "",
            "author": None,
            "title": "X Post",
            "error": error
        }


async def fetch_x_content(url: str) -> Optional[dict]:
    """Convenience function to fetch X content.
    
    Usage:
        content = await fetch_x_content("https://x.com/user/status/123")
        if content["success"]:
            print(content["text"])
    """
    scraper = XScraper()
    return await scraper.fetch_tweet(url)


def fetch_x_content_sync(url: str) -> Optional[dict]:
    """Synchronous wrapper for fetch_x_content."""
    import asyncio
    return asyncio.run(fetch_x_content(url))


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        url = sys.argv[1]
        result = fetch_x_content_sync(url)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python x_scraper.py <x_url>")