"""DeepSeek LLM integration for RolloForge bookmark analysis.

Replaces heuristic scoring with real LLM analysis.
"""
import os
import json
import logging
from typing import Optional
from openai import OpenAI

LOGGER = logging.getLogger(__name__)

# DeepSeek uses OpenAI-compatible API
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"  # or "deepseek-reasoner" for better reasoning


def get_deepseek_client() -> Optional[OpenAI]:
    """Initialize DeepSeek client."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        LOGGER.error("DEEPSEEK_API_KEY not set")
        return None
    
    return OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL
    )


def analyze_with_deepseek(text: str, title: str = "", url: str = "") -> Optional[dict]:
    """
    Analyze bookmark content using DeepSeek LLM.
    
    Returns analysis dict or None if failed.
    """
    client = get_deepseek_client()
    if not client:
        return None
    
    # Truncate text if too long (DeepSeek has context limits)
    max_chars = 8000
    if len(text) > max_chars:
        text = text[:max_chars] + "... [truncated]"
    
    prompt = f"""You are an AI bookmark analyzer for a user with this profile:

USER PROFILE:
- Building: OpenClaw multi-agent systems
- Interested in: AI trading, Polymarket prediction markets, stock analysis
- Stage: "building by learning" (hands-on, not theory)
- Effort preference: Quick wins (1-2 hours) to medium projects (few days)

HIGH PRIORITY TOPICS (9-10/10):
- OpenClaw setup & customization
- Multi-agent workflows  
- Polymarket/prediction markets
- AI-driven trading strategies
- Stock analysis automation

MEDIUM PRIORITY (6-8/10):
- Agent frameworks
- LLM optimization
- Automation tools

LOW PRIORITY (1-5/10):
- Pure theory without code
- Crypto (unless trading-related)

TRUSTED SOURCES (boost priority):
- Karpathy (+1.5 credibility)
- Verified AI builders

BOOKMARK TO ANALYZE:
URL: {url}
Title: {title}
Content: {text}

Analyze this bookmark and respond in valid JSON:
{{
  "title": "Polished title (concise, professional, no trailing dots)",
  "summary": "What it is + why this specific user should care (2-3 sentences)",
  "key_insights": ["3-5 bullet points of key takeaways"],
  "bucket": "test_this_week|build_later|archive|ignore",
  "priority_score": 0.0-10.0,
  "relevance": 0.0-10.0,
  "practical_value": 0.0-10.0,
  "actionability": 0.0-10.0,
  "reasoning": "Brief explanation of why you assigned this bucket and score"
}}

Rules:
- Title: Clean, professional, no hashtags, no trailing dots
- Summary: Explain what it is AND why this specific user should care
- Bucket: test_this_week (priority >=6, actionable now), build_later (priority 4-6, save for later), archive (reference), ignore (low value)
- Scores: Be honest, not everything is 10/10
- Key insights: Actionable, not generic"""

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert bookmark analyzer. You understand OpenClaw, AI agents, trading, and prediction markets. You provide honest, actionable analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        analysis = json.loads(content)
        
        # Add metadata
        analysis["analysis_source"] = "deepseek"
        analysis["model"] = DEEPSEEK_MODEL
        
        LOGGER.info(f"DeepSeek analysis complete: {analysis.get('title', 'N/A')[:50]}...")
        return analysis
        
    except Exception as e:
        LOGGER.error(f"DeepSeek analysis failed: {e}")
        return None


def deepseek_analyze_bookmark(text: str, title: str = "", url: str = "") -> dict:
    """
    Analyze bookmark with DeepSeek, fallback to heuristic if fails.
    
    Returns analysis dict.
    """
    # Try DeepSeek first
    result = analyze_with_deepseek(text, title, url)
    
    if result:
        return result
    
    # Fallback to heuristic
    LOGGER.warning("DeepSeek failed, using fallback analysis")
    return {
        "title": title or "Untitled",
        "summary": "[DeepSeek failed - basic analysis] " + text[:100],
        "key_insights": ["Analysis failed - review manually"],
        "bucket": "archive",
        "priority_score": 3.0,
        "relevance": 3.0,
        "practical_value": 3.0,
        "actionability": 3.0,
        "reasoning": "DeepSeek API failed, fallback to basic analysis",
        "analysis_source": "deepseek_fallback"
    }


if __name__ == "__main__":
    # Test
    test_text = """Karpathy open-sourced autoresearch. 42,000 GitHub stars in a week. 
    The pattern works on anything you can score with a number. Ad copy, cold emails, 
    video scripts, job posts, skill files. 12 cycles per hour, 100 overnight."""
    
    result = analyze_with_deepseek(test_text, "Test Title", "https://x.com/test")
    print(json.dumps(result, indent=2))