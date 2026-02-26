import asyncio
import httpx
from duckduckgo_search import DDGS

async def research_topic(topic: str) -> dict:
    """Research a topic using DuckDuckGo search - completely free, no API key needed."""
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, _search, topic)
    return results

def _search(topic: str) -> dict:
    try:
        with DDGS() as ddgs:
            # Text search
            text_results = list(ddgs.text(
                f"{topic} explained facts information",
                max_results=8
            ))
            
            # News results for recency
            try:
                news_results = list(ddgs.news(topic, max_results=4))
            except Exception:
                news_results = []

        summaries = []
        for r in text_results[:6]:
            summaries.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            })

        news = []
        for r in news_results[:3]:
            news.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "date": r.get("date", ""),
            })

        combined_text = "\n\n".join([
            f"Source: {s['title']}\n{s['snippet']}"
            for s in summaries
        ])

        if news:
            combined_text += "\n\nRecent News:\n" + "\n\n".join([
                f"{n['title']}: {n['snippet']}"
                for n in news
            ])

        return {
            "topic": topic,
            "summaries": summaries,
            "news": news,
            "combined_text": combined_text[:8000],  # Limit context size
        }

    except Exception as e:
        print(f"Research error: {e}")
        # Fallback with minimal data
        return {
            "topic": topic,
            "summaries": [],
            "news": [],
            "combined_text": f"Topic: {topic}. Please generate an educational video about this subject.",
        }
