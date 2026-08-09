from dataclasses import dataclass, field


@dataclass
class AgentState:

    user_request: str

    operating_system: str

    observations: dict = field(
        default_factory=dict
    )

    actions_taken: list = field(
        default_factory=list
    )

    final_message: str = ""

    iteration: int = 0