import os
import requests
import urllib3

from dotenv import load_dotenv
from typing import Dict, Any

from src.log import Logger

logger = Logger().get_logger()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

API_BASE_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

class PortalAPIClient:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = API_BASE_URL
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def get_contagem_total(
            self, 
            start_date: str, 
            end_date: str, 
            status: str = "", 
            search_term: str = "", 
            page: int = 1, 
            page_size: int = 5
        ) -> Dict[str, Any]:
        url = self.base_url + "/api/contagemTotal/3/desempenho"
        all_items = []

        while True:
            params = {
                "page": page,
                "pageSize": page_size,
                "status": status,
                "searchTerm": search_term,
                "startDate": start_date,
                "endDate": end_date
            }
            response = requests.get(url, headers=self.headers, params=params, verify=False)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            all_items.extend(items)

            total_items = data.get("totalItems", 0)
            # Checar se já pegou todos os itens
            if page * page_size >= total_items:
                break
            page += 1

        logger.info(f"Fetched {len(all_items)} items from {start_date} to {end_date}")
        return all_items
