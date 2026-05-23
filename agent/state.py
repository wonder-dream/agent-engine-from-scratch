from enum import StrEnum


class AgentState(StrEnum):
    """Agent 状态机：IDLE → THOUGHT → (ACTION → OBSERVATION → THOUGHT)… → FINAL_ANSWER"""
    IDLE = "idle"               # 初始状态，组装 messages
    THOUGHT = "thought"         # 调 LLM，决定下一步
    ACTION = "action"           # 解析 tool_calls，执行工具
    OBSERVATION = "observation" # 把工具结果追加回 messages
    FINAL_ANSWER = "final_answer"  # 结束，返回最终文本

