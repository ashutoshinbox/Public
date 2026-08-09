import json
import platform

from agent.state import AgentState
from agent.planner import get_next_action
from agent.executor import execute_action


MAX_ITERATIONS = 10


def print_banner():

    print()

    print("=" * 70)

    print(
        "        AI OPERATING SYSTEM AGENT"
    )

    print("=" * 70)


def run_agent(user_request):

    operating_system = platform.system()

    state = AgentState(

        user_request=user_request,

        operating_system=operating_system
    )

    print_banner()

    print(
        f"\nOperating System : {operating_system}"
    )

    print(
        f"\nUser Request:\n{user_request}"
    )

    for iteration in range(MAX_ITERATIONS):

        state.iteration = iteration + 1

        print()

        print("-" * 70)

        print(
            f"AGENT ITERATION {state.iteration}"
        )

        print("-" * 70)

        # ------------------------------------------
        # LLM DECISION
        # ------------------------------------------

        decision = get_next_action(state)

        action = decision["action"]

        reason = decision["reason"]

        print("\n[LLM DECISION]")

        print(
            f"Action : {action}"
        )

        print(
            f"Reason : {reason}"
        )

        # ------------------------------------------
        # FINISH
        # ------------------------------------------

        if action == "finish":

            state.final_message = reason

            print(
                "\n[AGENT] No further action required."
            )

            break

        # ------------------------------------------
        # EXECUTE TOOL
        # ------------------------------------------

        print(
            f"\n[TOOL EXECUTION] {action}"
        )

        try:

            result = execute_action(action)

        except Exception as error:

            result = (
                f"TOOL ERROR: {error}"
            )

        # ------------------------------------------
        # SAVE OBSERVATION
        # ------------------------------------------

        state.observations[action] = result

        state.actions_taken.append(
            action
        )

        print("\n[OBSERVATION]")

        print(result)

    else:

        state.final_message = (
            "Maximum agent iterations reached."
        )

    # ------------------------------------------
    # FINAL RESULT
    # ------------------------------------------

    print()

    print("=" * 70)

    print("FINAL RESULT")

    print("=" * 70)

    print(
        state.final_message
    )

    print()

    print("Actions executed:")

    for action in state.actions_taken:

        print(
            f"  ✓ {action}"
        )

    print()

    print("Observations:")

    print(
        json.dumps(
            state.observations,
            indent=2
        )
    )


if __name__ == "__main__":

    user_request = input(
        "\nDescribe the OS problem: "
    )

    run_agent(user_request)