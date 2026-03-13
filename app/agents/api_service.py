import requests
from typing import Dict, Any
from functools import lru_cache

class APIService:
    """Service to manage external API connections and requests"""
    
    def __init__(self):
        self.api_configs: Dict[str, Dict[str, str]] = {}
        self.session = requests.Session()
    
    def add_api_config(self, api_name: str, config: Dict[str, str]):
        """
        Add a new API configuration
        config should include:
        - base_url: Base URL of the API
        - api_key: API key if required
        - headers: Additional headers if needed
        """
        self.api_configs[api_name] = config
        if config.get('api_key'):
            self.api_configs[api_name]['headers'] = {
                'Authorization': f"Bearer {config['api_key']}",
                **(config.get('headers', {}))
            }
    
    @lru_cache(maxsize=100)
    async def cached_request(self, api_name: str, endpoint: str, cache_key: str) -> Dict[str, Any]:
        """
        Make a cached API request - useful for frequently accessed endpoints
        """
        return await self.make_request(api_name, endpoint)

# Initialize the API service
api_service = APIService()
