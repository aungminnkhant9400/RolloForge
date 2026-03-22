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
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
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
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.user_agent,
                    viewport={"width": 1280, "height": 800}
                )
                page = await context.new_page()
                
                # Navigate to tweet
                LOGGER.info(f"Fetching X content: {url}")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Wait for tweet to load
                await page.wait_for_selector("article[data-testid='tweet']", timeout=10000)
                
                # Extract tweet text
                tweet_text = await page.eval_on_selector(
                    "article[data-testid='tweet'] div[data-testid='tweetText']",
                    "el => el.innerText"
                )
                
                # Extract author
                author_elem = await page.query_selector("article[data-testid='tweet'] a[href^='/']")
                author = None
                if author_elem:
                    href = await author_elem.get_attribute("href")
                    if href:
                        author = href.strip("/").split("/")[0]
                
                await browser.close()
                
                return {
                    "success": True,
                    "text": tweet_text or "",
                    "author": author,
                    "title": self._generate_title(tweet_text or ""),
                    "error": None
                }
                
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
    # Test
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        result = fetch_x_content_sync(url)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python x_scraper.py <x_url>")