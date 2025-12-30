import httpx
import urllib.parse
from typing import Optional

BASE_URL = "https://pub-api.tpirates.com/v2/www/retail-price"

async def get_market_price(fish_name: str) -> Optional[float]:
    """
    Fetches the market price (avgPrice per kg) from 'The Pirates' (tpirates.com) public API.
    Ref: test/tpriateWrapper/apitest.ipynb
    """
    try:
        encoded_name = urllib.parse.quote(fish_name)
        endpoint = f"/price/aggregate/region?keyword={encoded_name}&orderState=default&page=0&size=6"
        url = f"{BASE_URL}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            
            if response.status_code != 200:
                print(f"Market Price API Error: {response.status_code}")
                return None
            
            data = response.json()
            # The structure is data['content'] which is a list.
            content = data.get("content", [])
            
            if not content:
                print(f"No price data found for {fish_name}")
                return None
            
            # Notebook logic: "Most relevant result is at index 0. First avgPrice is per kg."
            # content[0] usually contains keys like "name", "avgPrice", "minPrice", etc.
            avg_price = content[0].get("avgPrice")
            
            if avg_price is not None:
                return float(avg_price)
            
            return None
            
    except Exception as e:
        print(f"Error fetching market price: {e}")
        return None
