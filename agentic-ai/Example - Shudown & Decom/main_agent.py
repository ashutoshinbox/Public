import os
import subprocess
import smtplib
import requests
from email.mime.text import MIMEText
from typing import List, Dict, Literal
from typing_extensions import TypedDict
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, START, END

# ==========================================
# PRODUCTION CONFIGURATION
# ==========================================
TARGET_HOSTS = ["host-one", "host-two", "host-three"]
CHANGE_ID = "CHG0001001"
MY_EMAIL = "ashutosh.mohanty@gmail.com"

# ServiceNow Instance Credentials
SNOW_INSTANCE = "https://service-now.com"
SNOW_USER = "api_automation_user"
SNOW_PASSWORD = "YourSecurePasswordHere"

# Outbound Mail Server Configurations (e.g., SMTP Relay or Gmail)
SMTP_SERVER = "://gmail.com" 
SMTP_PORT = 587
SMTP_USER = "your_sender_email@gmail.com"
SMTP_PASSWORD = "your_app_specific_password" 

# ==========================================
# AGENT STATE
# ==========================================
class AgentState(TypedDict):
    hosts: List[str]
    change_id: str
    change_status: str
    shutdown_results: Dict[str, str]
    decom_results: Dict[str, str]
    ticket_close_result: str
    execution_errors: List[str]

# ==========================================
# REAL-TIME API CORE TOOLS
# ==========================================

def get_servicenow_status(change_id: str) -> str:
    """Queries your live ServiceNow Instance for the Change State."""
    url = f"{SNOW_INSTANCE}/api/now/table/change_request"
    params = {"sysparm_query": f"number={change_id}", "sysparm_limit": "1"}
    
    try:
        response = requests.get(url, auth=(SNOW_USER, SNOW_PASSWORD), params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            results = data.get("result", [])
            if results:
                return results[0].get("state", "Unknown")
            return "NOT_FOUND"
        return f"HTTP_ERROR_{response.status_code}"
    except Exception as e:
        return f"CONN_FAILURE: {str(e)}"

def patch_servicenow_close(change_id: str) -> str:
    """Updates the ticket state to Closed and adds work notes."""
    # First, we need to fetch the unique system ID (sys_id) of the ticket
    search_url = f"{SNOW_INSTANCE}/api/now/table/change_request"
    params = {"sysparm_query": f"number={change_id}", "sysparm_limit": "1"}
    
    try:
        response = requests.get(search_url, auth=(SNOW_USER, SNOW_PASSWORD), params=params, timeout=15)
        if response.status_code != 200 or not response.json().get("result"):
            return f"FAILED_TO_FIND_SYS_ID (Code {response.status_code})"
        
        sys_id = response.json()["result"][0]["sys_id"]
        
        # Now perform the PATCH update using the sys_id
        update_url = f"{SNOW_INSTANCE}/api/now/table/change_request/{sys_id}"
        
        # Note: '3' or 'closed' depends on your ServiceNow choice list values
        payload = {
            "state": "closed", 
            "close_code": "successful",
            "close_notes": "Automated Agentic AI workflow completed host shutdowns and decommissions successfully.",
            "work_notes": "Infrastructure decommission complete. Closing ticket automatically."
        }
        
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        patch_response = requests.patch(
            update_url, 
            auth=(SNOW_USER, SNOW_PASSWORD), 
            json=payload, 
            headers=headers, 
            timeout=15
        )
        
        if patch_response.status_code in:
            return "SUCCESSFULLY_CLOSED_IN_SNOW"
        return f"PATCH_FAILED_HTTP_{patch_response.status_code}: {patch_response.text}"
        
    except Exception as e:
        return f"PATCH_EXCEPTION: {str(e)}"

def send_real_email(subject: str, body: str):
    """Dispatches transaction records to your inbox using secure TLS."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = MY_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"📧 Notification sent successfully to {MY_EMAIL}")
    except Exception as e:
        print(f"🚨 Critical Failure writing to Mail Server: {e}")

def run_remote_ssh(host: str, command: str) -> str:
    """Executes host utilities via passwordless SSH."""
    ssh_target = f"ssh -o StrictHostKeyChecking=no {host} '{command}'"
    try:
        res = subprocess.run(ssh_target, shell=True, capture_output=True, text=True, timeout=90)
        if res.returncode == 0:
            return "SUCCESS"
        return f"FAILED (Code {res.returncode}): {res.stderr.strip()}"
    except Exception as e:
        return f"EXC_ERROR: {str(e)}"

# ==========================================
# LANGGRAPH NODE DESIGN
# ==========================================

def check_change_node(state: AgentState) -> AgentState:
    print(f"🔎 Agent verifying validation status for ticket: {state['change_id']}")
    status = get_servicenow_status(state['change_id'])
    state['change_status'] = status
    print(f"📈 ServiceNow Ticket State evaluation: {status}")
    return state

def shutdown_hosts_node(state: AgentState) -> AgentState:
    print("⚡ Executing parallel server shutdowns...")
    results = {}
    errors = []
    
    with ThreadPoolExecutor(max_workers=len(state['hosts'])) as exec_pool:
        future_map = {
            exec_pool.submit(run_remote_ssh, srv, "shutdown_linux"): srv for srv in state['hosts']
        }
        for future in future_map:
            srv = future_map[future]
            res = future.result()
            results[srv] = res
            if "FAILED" in res or "EXC_ERROR" in res:
                errors.append(f"Shutdown failed on {srv}: {res}")

    state['shutdown_results'] = results
    state['execution_errors'].extend(errors)
    return state

def decommission_hosts_node(state: AgentState) -> AgentState:
    print("⚙️ Systems stopped. Beginning decommissioning pipelines...")
    results = {}
    errors = []
    
    with ThreadPoolExecutor(max_workers=len(state['hosts'])) as exec_pool:
        future_map = {
            exec_pool.submit(run_remote_ssh, srv, "decom_linux"): srv for srv in state['hosts']
        }
        for future in future_map:
            srv = future_map[future]
            res = future.result()
            results[srv] = res
            if "FAILED" in res or "EXC_ERROR" in res:
                errors.append(f"Decom failed on {srv}: {res}")

    state['decom_results'] = results
    state['execution_errors'].extend(errors)
    return state

def close_ticket_node(state: AgentState) -> AgentState:
    print(f"🔒 Tasks finished. Attempting to auto-close ServiceNow Change: {state['change_id']}")
    close_status = patch_servicenow_close(state['change_id'])
    state['ticket_close_result'] = close_status
    print(f"📝 ServiceNow Closure System Output: {close_status}")
    
    if "SUCCESS" not in close_status:
        state['execution_errors'].append(f"Infrastructure succeeded but ServiceNow closure failed: {close_status}")
    return state

def success_handler_node(state: AgentState) -> AgentState:
    body = (
        f"Hi Ashutosh,\n\n"
        f"Decommission run succeeded and ticket has been processed.\n"
        f"Hosts cleaned: {state['hosts']}\n\n"
        f"ServiceNow Ticket Update: {state['ticket_close_result']}\n\n"
        f"Logs:\n"
        f"Shutdowns: {state['shutdown_results']}\n"
        f"Decoms: {state['decom_results']}"
    )
    send_real_email(f"✅ Run Success & Closed: {state['change_id']}", body)
    return state

def failure_handler_node(state: AgentState) -> AgentState:
    body = (
        f"Hi Ashutosh,\n\n"
        f"Decommission aborted/failed for {state['change_id']}.\n"
        f"Ticket Status: {state['change_status']}\n\n"
        f"Errors encountered:\n" + "\n".join(state['execution_errors'])
    )
    send_real_email(f"❌ Run Aborted/Failed: {state['change_id']}", body)
    return state

# ==========================================
# CONDITIONALS & COMPOSITION
# ==========================================

def route_ticket_check(state: AgentState):
    if state['change_status'].lower() in ["implement", "authorized", "work_in_progress"]:
        return "shutdown_hosts"
    state['execution_errors'].append(f"Aborted: Ticket state is '{state['change_status']}', not approved for implementation.")
    return "notify_failure"

def route_shutdown_check(state: AgentState):
    return "notify_failure" if state['execution_errors'] else "decommission_hosts"

def route_decom_check(state: AgentState):
    return "notify_failure" if state['execution_errors'] else "close_ticket"

def route_close_check(state: AgentState):
    # Even if closure failed, we route to proper template based on severe errors
    return "notify_failure" if any("FAILED" in err or "EXC" in err for err in state['execution_errors']) else "notify_success"

# Graph Blueprint Building
builder = StateGraph(AgentState)
builder.add_node("check_change_status", check_change_node)
builder.add_node("shutdown_hosts", shutdown_hosts_node)
builder.add_node("decommission_hosts", decommission_hosts_node)
builder.add_node("close_ticket", close_ticket_node)
builder.add_node("notify_success", success_handler_node)
builder.add_node("notify_failure", failure_handler_node)

builder.add_edge(START, "check_change_status")
builder.add_conditional_edges("check_change_status", route_ticket_check)
builder.add_conditional_edges("shutdown_hosts", route_shutdown_check)
builder.add_conditional_edges("decommission_hosts", route_decom_check)
builder.add_conditional_edges("close_ticket", route_close_check)
builder.add_edge("notify_success", END)
builder.add_edge("notify_failure", END)

app = builder.compile()

if __name__ == "__main__":
