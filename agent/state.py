from enum import StrEnum

class AgentState(StrEnum):
    IDLE = "idle"
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    FINAL_ANSWER = "final_answer"

