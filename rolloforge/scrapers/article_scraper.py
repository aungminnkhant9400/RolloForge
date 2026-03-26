"""Article scraper using web_fetch - more reliable than newspaper3k."""

import subprocess
import json

def scrape_article(url: str) -> dict:
    """
    Scrape article content using web_fetch via OpenClaw.
    Falls back to basic extraction if web_fetch fails.
    
    Returns:
        {
            'success': bool,
            'title': str,
            'text': str,
            'author': str or None,
            'source': str
        }
    """
    try:
        # Try using web_fetch tool (OpenClaw's web extraction)
        # Since we're in a subprocess, use curl + basic extraction
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = None
        if soup.find('title'):
            title = soup.find('title').get_text().strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        
        # Extract main content
        # Try common article containers
        article = None
        for selector in ['article', 'main', '[role="main"]', '.article-content', '.post-content', '.entry-content', '#content']:
            article = soup.select_one(selector)
            if article:
                break
        
        # Fallback to body if no article container
        if not article:
            article = soup.find('body')
        
        # Clean up the text
        if article:
            # Remove script and style elements
            for script in article(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                script.decompose()
            
            text = article.get_text(separator='\n', strip=True)
            # Clean up excessive whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            text = text[:5000]  # Limit to 5000 chars
        else:
            text = None
        
        # Extract author
        author = None
        for meta in soup.find_all('meta'):
            if meta.get('name') in ['author', 'twitter:creator', 'article:author']:
                author = meta.get('content')
                break
        
        # Check if we got meaningful content
        if title and text and len(text) > 200:
            return {
                'success': True,
                'title': title,
                'text': text,
                'author': author,
                'source': 'requests+bs4'
            }
        else:
            return {
                'success': False,
                'title': title,
                'text': text,
                'author': author,
                'source': None
            }
            
    except Exception as e:
        return {
            'success': False,
            'title': None,
            'text': None,
            'author': None,
            'source': None,
            'error': str(e)
        }
