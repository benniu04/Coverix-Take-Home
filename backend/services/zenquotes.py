import httpx
from typing import Optional


class ZenQuotesService:
    """Service to fetch calming quotes when user is frustrated."""
    
    BASE_URL = "https://zenquotes.io/api/quotes"
    
    @staticmethod
    async def get_quote() -> str:
        """
        Fetch a random inspirational quote.
        Returns a formatted quote string.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(ZenQuotesService.BASE_URL, timeout=5.0)
                response.raise_for_status()
                data = response.json()
                
                if data and len(data) > 0:
                    quote = data[0]
                    return f'"{quote.get("q", "Stay positive!")}" - {quote.get("a", "Unknown")}'
                
                return "Take a deep breath. Everything will be okay."
                
            except Exception:
                return "Take a deep breath. We're here to help you."

