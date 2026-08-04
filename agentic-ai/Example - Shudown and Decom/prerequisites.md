Set up a Python Virtual Environment
-----------------------------------

#python3 -m venv venv
#source venv/bin/activate

Install LangGraph and SDK dependencies
--------------------------------------

#pip install --upgrade pip
#pip install langgraph langchain-core langchain-openai requests pydantic psutil


Export your LLM API Credentials 
----------------------------------
#export OPENAI_API_KEY="your-actual-api-key-here"


Generate an SSH key pair on localhost (press Enter to accept defaults and leave the passphrase blank):
------------------------------------------------------------------------------------------------------

#ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""


Copy the public key to all three remote hosts:
----------------------------------------------

#ssh-copy-id ashutosh@host-one
#ssh-copy-id ashutosh@host-two
#ssh-copy-id ashutosh@host-three


Verify password-less access by running a test command. It should return instantly without asking for a password:
--------------------------------------------------------------------------------------------------------------
#ssh -o StrictHostKeyChecking=no host-one "hostname"