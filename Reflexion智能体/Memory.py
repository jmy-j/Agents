from typing import List, Dict, Any, Optional


class Memory:
    """
    一个简单的短期记忆模块，用于存储智能体的行动与反思轨迹。
    """

    def __init__(self):
        """
        初始化一个空列表来存储所有记录。
        """
        self.records: List[Dict[str, Any]] = []

    def add_record(self, record_type: str, content: str):
        """
        向记忆中添加一条新记录。

        参数:
        - record_type (str): 记录的类型 ('execution' 或 'reflection')。
        - content (str): 记录的具体内容 (例如，生成的代码或反思的反馈)。
        """
        record = {"type": record_type, "content": content}
        self.records.append(record)
        print(f"📝 记忆已更新，新增一条 '{record_type}' 记录。")

    def get_trajectory(self) -> str:
        """
        将所有记忆记录格式化为一个连贯的字符串文本，用于构建提示词。
        """
        return self._format_records(self.records)

    def get_past_trajectory(self, exclude_last_reflection: bool = False) -> str:
        """
        返回历史轨迹，用于反思/优化时提供上下文。

        参数:
        - exclude_last_reflection (bool): 为 True 时排除最新一条反思记录（优化阶段使用）。
        """
        skip_indices: set[int] = set()

        for i in range(len(self.records) - 1, -1, -1):
            if self.records[i]['type'] == 'execution':
                skip_indices.add(i)
                break

        if exclude_last_reflection:
            for i in range(len(self.records) - 1, -1, -1):
                if self.records[i]['type'] == 'reflection':
                    skip_indices.add(i)
                    break

        past_records = [
            record for i, record in enumerate(self.records) if i not in skip_indices
        ]
        formatted = self._format_records(past_records)
        if not formatted:
            return "（尚无历史记录，这是首次尝试。）"
        return formatted

    def _format_records(self, records: List[Dict[str, Any]]) -> str:
        trajectory_parts = []
        for record in records:
            if record['type'] == 'execution':
                trajectory_parts.append(f"--- 上一轮尝试 (代码) ---\n{record['content']}")
            elif record['type'] == 'reflection':
                trajectory_parts.append(f"--- 评审员反馈 ---\n{record['content']}")

        return "\n\n".join(trajectory_parts)

    def debug_print(self, stage: str) -> None:
        """在终端打印当前完整记忆，便于调试观察。"""
        print(f"\n{'=' * 10} 记忆快照 [{stage}] {'=' * 10}")
        trajectory = self.get_trajectory()
        if trajectory:
            print(trajectory)
        else:
            print("（尚无记录）")
        print(f"{'=' * 36}\n")

    def get_last_execution(self) -> Optional[str]:
        """
        获取最近一次的执行结果 (例如，最新生成的代码)。
        如果不存在，则返回 None。
        """
        for record in reversed(self.records):
            if record['type'] == 'execution':
                return record['content']
        return None
