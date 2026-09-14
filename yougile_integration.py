import json
import os
import aiohttp
from typing import List, Dict, Optional

class YouGileIntegration:
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.base_url = "https://api.yougile.com"

    def _load_config(self, config_file: str) -> Dict:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"yougile_token": ""}

    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.config.get('yougile_token', '')}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{endpoint}"
            async with session.request(method, url, headers=headers, json=data) as response:
                return await response.json()

    async def get_tasks(self) -> List[Dict]:
        try:
            data = await self._request("GET", "/api/tasks")
            return data.get("tasks", [])
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []

    async def create_task(self, title: str, description: str = "") -> Dict:
        try:
            data = {"title": title, "description": description}
            return await self._request("POST", "/api/tasks", data)
        except Exception as e:
            print(f"Error creating task: {e}")
            return {"error": str(e)}

    async def get_projects(self) -> List[Dict]:
        try:
            data = await self._request("GET", "/api/projects")
            return data.get("projects", [])
        except Exception as e:
            print(f"Error getting projects: {e}")
            return []

    async def get_task(self, task_id: str) -> Dict:
        try:
            return await self._request("GET", f"/api/tasks/{task_id}")
        except Exception as e:
            print(f"Error getting task: {e}")
            return {"error": str(e)}

    async def update_task(self, task_id: str, data: Dict) -> Dict:
        try:
            return await self._request("PATCH", f"/api/tasks/{task_id}", data)
        except Exception as e:
            print(f"Error updating task: {e}")
            return {"error": str(e)}

    async def delete_task(self, task_id: str) -> Dict:
        try:
            return await self._request("DELETE", f"/api/tasks/{task_id}")
        except Exception as e:
            print(f"Error deleting task: {e}")
            return {"error": str(e)}
