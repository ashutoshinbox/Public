import platform


def get_tools():

    operating_system = platform.system()

    if operating_system == "Linux":

        from tools.linux_tools import TOOLS

        return TOOLS

    elif operating_system == "Windows":

        from tools.windows_tools import TOOLS

        return TOOLS

    else:

        raise RuntimeError(
            f"Unsupported operating system: {operating_system}"
        )


def execute_action(action: str):

    tools = get_tools()

    if action not in tools:

        raise ValueError(
            f"Action '{action}' is not allowed."
        )

    tool = tools[action]

    return tool()