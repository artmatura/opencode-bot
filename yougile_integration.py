import json
import os
import aiohttp
from typing import List, Dict, Optional

class YouGileIntegration:
    def __init__(self, config_file: str = "bot_config.json"):
        self.config = self._load_config(config_file)
        self.base_url = "https://api.yougile.com/api-v2"
        self.token = os.environ.get("yougile_token", self.config.get("yougile_token", ""))

    def _load_config(self, config_file: str) -> Dict:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"yougile_token": ""}

    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{endpoint}"
            async with session.request(method, url, headers=headers, json=data) as response:
                if response.status == 401:
                    return {"error": "unauthorized", "message": "Неверный или отсутствующий токен YouGile"}
                if response.status >= 400:
                    body = await response.text()
                    return {"error": f"http_{response.status}", "message": body[:300]}
                return await response.json()

    async def get_tasks(self, limit: int = 20) -> List[Dict]:
        try:
            data = await self._request("GET", f"/task-list?limit={limit}")
            if "content" in data:
                return data["content"]
            return []
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []

    async def get_projects(self) -> List[Dict]:
        try:
            data = await self._request("GET", "/projects?limit=100")
            if "content" in data:
                return data["content"]
            return []
        except Exception as e:
            print(f"Error getting projects: {e}")
            return []

    async def get_boards(self, project_id: Optional[str] = None) -> List[Dict]:
        try:
            endpoint = "/boards?limit=100"
            if project_id:
                endpoint += f"&projectId={project_id}"
            data = await self._request("GET", endpoint)
            if "content" in data:
                return data["content"]
            return []
        except Exception as e:
            print(f"Error getting boards: {e}")
            return []

    async def get_columns(self, board_id: str) -> List[Dict]:
        try:
            data = await self._request("GET", f"/columns?boardId={board_id}&limit=100")
            if "content" in data:
                return data["content"]
            return []
        except Exception as e:
            print(f"Error getting columns: {e}")
            return []

    async def create_task(self, title: str, column_id: Optional[str] = None, description: str = "") -> Dict:
        try:
            data = {"title": title}
            if column_id:
                data["columnId"] = column_id
            if description:
                data["description"] = description
            return await self._request("POST", "/tasks", data)
        except Exception as e:
            print(f"Error creating task: {e}")
            return {"error": str(e)}

    async def get_task(self, task_id: str) -> Dict:
        try:
            return await self._request("GET", f"/tasks/{task_id}")
        except Exception as e:
            print(f"Error getting task: {e}")
            return {"error": str(e)}

    async def update_task(self, task_id: str, data: Dict) -> Dict:
        try:
            return await self._request("PUT", f"/tasks/{task_id}", data)
        except Exception as e:
            print(f"Error updating task: {e}")
            return {"error": str(e)}

    async def delete_task(self, task_id: str) -> Dict:
        try:
            return await self._request("DELETE", f"/tasks/{task_id}")
        except Exception as e:
            print(f"Error deleting task: {e}")
            return {"error": str(e)}

    def has_token(self) -> bool:
        return bool(self.token)