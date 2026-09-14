import json
import os
import subprocess
import asyncio
from typing import List, Dict, Optional

class OpenCodeIntegration:
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.agents = self._get_default_agents()

    def _load_config(self, config_file: str) -> Dict:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"opencode_path": "opencode"}

    def _get_default_agents(self) -> List[Dict]:
        return [
            {"id": "focus", "name": "🎯 Фокус-ассистент", "running": False, "command": "focus-assistant"},
            {"id": "yougile", "name": "📋 YouGile менеджер", "running": False, "command": "yougile-manager"},
            {"id": "opencode", "name": "🤖 OpenCode основной", "running": False, "command": "opencode-main"}
        ]

    async def get_agents_status(self) -> List[Dict]:
        return self.agents

    async def start_agent(self, agent_id: str) -> Dict:
        for agent in self.agents:
            if agent["id"] == agent_id:
                if agent["running"]:
                    return {"status": "already_running", "agent": agent["name"]}
                
                try:
                    opencode_path = self.config.get("opencode_path", "opencode")
                    process = await asyncio.create_subprocess_exec(
                        opencode_path, "agent", "start", agent["command"],
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    agent["running"] = True
                    agent["process"] = process
                    return {"status": "started", "agent": agent["name"]}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
        
        return {"status": "not_found"}

    async def stop_agent(self, agent_id: str) -> Dict:
        for agent in self.agents:
            if agent["id"] == agent_id:
                if not agent["running"]:
                    return {"status": "not_running", "agent": agent["name"]}
                
                try:
                    if "process" in agent:
                        agent["process"].terminate()
                    agent["running"] = False
                    return {"status": "stopped", "agent": agent["name"]}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
        
        return {"status": "not_found"}

    async def send_command(self, agent_id: str, command: str) -> Dict:
        for agent in self.agents:
            if agent["id"] == agent_id and agent["running"]:
                try:
                    opencode_path = self.config.get("opencode_path", "opencode")
                    result = subprocess.run(
                        [opencode_path, "agent", "send", agent["command"], command],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    return {"status": "success", "output": result.stdout}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
        
        return {"status": "not_found_or_not_running"}
