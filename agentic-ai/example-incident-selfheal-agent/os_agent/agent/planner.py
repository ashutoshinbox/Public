import json

from agent.llm import ask_llm


AVAILABLE_ACTIONS = [
    "check_cpu",
    "check_memory",
    "check_disk",
    "check_uptime",
    "cleanup_tmp",
    "verify_disk",
    "finish"
]


def get_next_action(state):

    prompt = f"""
You are an intelligent Operating System troubleshooting agent.

Operating System:

{state.operating_system}


USER REQUEST:

{state.user_request}


OBSERVATIONS FROM PREVIOUS ACTIONS:

{json.dumps(state.observations, indent=2)}


ACTIONS AVAILABLE:

{json.dumps(AVAILABLE_ACTIONS, indent=2)}


Your job is to decide the NEXT action.

Rules:

1. Only select an action from the allowed actions.

2. Never invent shell commands.

3. If CPU information is required, use check_cpu.

4. If memory information is required, use check_memory.

5. If disk information is required, use check_disk.

6. If uptime information is required, use check_uptime.

7. If disk usage appears critically high,
   cleanup_tmp can be selected.

8. After cleanup, use verify_disk.

9. Do not cleanup files unless there is evidence
   that disk usage is a problem.

10. Avoid repeating diagnostic actions unnecessarily.

11. When the problem has been investigated and
    no further action is required, choose finish.

12. Remember that this machine is:

{state.operating_system}

Return ONLY JSON.

Example:

{{
    "action": "check_disk",
    "reason": "Disk utilization needs to be checked."
}}
"""

    result = ask_llm(prompt)

    try:

        decision = json.loads(result)

    except json.JSONDecodeError:

        raise RuntimeError(
            "LLM did not return valid JSON:\n"
            + result
        )

    action = decision.get("action")

    if action not in AVAILABLE_ACTIONS:

        raise RuntimeError(
            f"LLM selected invalid action: {action}"
        )

    return decision