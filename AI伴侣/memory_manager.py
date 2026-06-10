
"""Memory management for AI Companion — JSON file-based persistence."""
import json
import os
from datetime import datetime


class MemoryManager:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.memory_file = os.path.join(data_dir, "memories.json")
        os.makedirs(data_dir, exist_ok=True)
        self.memories = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return self._ensure_structure(data)
            except (json.JSONDecodeError, IOError):
                pass
        return self._default_structure()

    def _default_structure(self) -> dict:
        return {
            "user_name": "",
            "preferences": [],
            "habits": [],
            "important_events": [],
            "current_concerns": [],
            "other_facts": [],
            "last_updated": datetime.now().isoformat(),
        }

    def _ensure_structure(self, data: dict) -> dict:
        default = self._default_structure()
        for key in default:
            if key not in data:
                data[key] = default[key]
        return data

    def save(self):
        self.memories["last_updated"] = datetime.now().isoformat()
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def add_fact(self, category: str, content):
        if category in self.memories and isinstance(self.memories[category], list):
            if content not in self.memories[category]:
                self.memories[category].append(content)
                self.save()

    def set_info(self, key: str, value):
        if key in self.memories:
            self.memories[key] = value
            self.save()

    def remove_fact(self, category: str, content):
        if category in self.memories and isinstance(self.memories[category], list):
            if content in self.memories[category]:
                self.memories[category].remove(content)
                self.save()

    def clear_category(self, category: str):
        if category in self.memories and isinstance(self.memories[category], list):
            self.memories[category] = []
            self.save()

    def reset_all(self):
        self.memories = self._default_structure()
        self.save()

    def get_context_string(self) -> str:
        parts = []
        m = self.memories

        if m.get("user_name"):
            parts.append(f"用户的名字是：{m['user_name']}")

        if m.get("preferences"):
            parts.append(f"用户的偏好：{'；'.join(m['preferences'])}")

        if m.get("habits"):
            parts.append(f"用户的生活习惯：{'；'.join(m['habits'])}")

        if m.get("important_events"):
            events = []
            for e in m["important_events"]:
                if isinstance(e, dict):
                    events.append(f"{e.get('date', '')}: {e.get('event', '')}")
                else:
                    events.append(str(e))
            parts.append(f"用户的重要事件：{'；'.join(events)}")

        if m.get("current_concerns"):
            parts.append(f"用户近期关注/烦恼的事：{'；'.join(m['current_concerns'])}")

        if m.get("other_facts"):
            parts.append(f"关于用户的其他信息：{'；'.join(m['other_facts'])}")

        if parts:
            return "以下是关于用户的重要记忆，请在对话中自然地融入这些信息：\n" + "\n".join(parts)
        return ""

    def get_all_memories(self) -> dict:
        return self.memories
