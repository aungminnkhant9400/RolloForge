"""Article scraper for non-X URLs using newspaper3k."""

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

def scrape_article(url: str) -> dict:
    """
    Scrape article content using newspaper3k.
    
    Returns:
        {
            'success': bool,
            'title': str,
            'text': str,
            'author': str or None,
            'source': str
        }
    """
    if not NEWSPAPER_AVAILABLE:
        return {
            'success': False,
            'title': None,
            'text': None,
            'author': None,
            'source': None
        }
    
    try:
        article = Article(url, language='en')
        article.download()
        article.parse()
        
        # Only return if we got meaningful content
        if article.title and len(article.text) > 100:
            return {
                'success': True,
                'title': article.title,
                'text': article.text[:3000],  # Limit to 3000 chars
                'author': article.authors[0] if article.authors else None,
                'source': 'newspaper3k'
            }
        else:
            return {
                'success': False,
                'title': None,
                'text': None,
                'author': None,
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
