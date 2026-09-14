import json
import os

class BotConfig:
    def __init__(self, config_file: str = "bot_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._create_default_config()

    def _create_default_config(self) -> dict:
        default_config = {
            "bot_token": "YOUR_BOT_TOKEN_HERE",
            "allowed_users": [],
            "opencode_path": "opencode",
            "yougile_token": "",
            "webhook_url": ""
        }
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: dict):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    @property
    def bot_token(self) -> str:
         return os.environ.get("bot_token", self.config.get("bot_token", ""))

    @property
     def allowed_users(self) -> list:
        env_users = os.environ.get("allowed_users", "")
        if env_users.strip():
            return [int(u.strip()) for u in env_users.split(",") if u.strip()]
        return self.config.get("allowed_users", [])

    @property
    def opencode_path(self) -> str:
        return self.config.get("opencode_path", "opencode")

    @property
    def yougile_token(self) -> str:
        return self.config.get("yougile_token", "")

    def update(self, key: str, value):
        self.config[key] = value
        self._save_config(self.config)
