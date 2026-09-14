import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class FocusManager:
    def __init__(self, data_file: str = "focus_data.json"):
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"tasks": [], "completed": [], "daily_focus": []}

    def _save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_task(self, title: str, priority: int = 1) -> Dict:
        task = {
            "id": str(len(self.data["tasks"]) + 1),
            "title": title,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "completed": False
        }
        self.data["tasks"].append(task)
        self._save_data()
        return task

    def get_current_tasks(self) -> List[Dict]:
        return [t for t in self.data["tasks"] if not t["completed"]]

    def complete_task(self, task_id: str) -> bool:
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self.data["completed"].append(task)
                self.data["tasks"].remove(task)
                self._save_data()
                return True
        return False

    def get_completed_tasks(self) -> List[Dict]:
        return self.data["completed"]

    def get_daily_focus(self) -> List[Dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [t for t in self.data["daily_focus"] if t.get("date") == today]

    def add_daily_focus(self, title: str) -> Dict:
        task = {
            "id": str(len(self.data["daily_focus"]) + 1),
            "title": title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat()
        }
        self.data["daily_focus"].append(task)
        self._save_data()
        return task

    def get_stats(self) -> Dict:
        return {
            "active_tasks": len(self.get_current_tasks()),
            "completed_today": len([t for t in self.data["completed"] 
                                   if t.get("completed_at", "").startswith(datetime.now().strftime("%Y-%m-%d"))]),
            "total_completed": len(self.data["completed"])
        }
