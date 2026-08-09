To demonstrate the ai-agentic workflow:



Consider a scenario where a Linux system named "localhost" initiates a task across three target Linux systems: host-one, host-two, and host-three, using password-less SSH keys.



The process begins by querying a ServiceNow API to verify the status of Change Request CHG0001001.

Once the change status is validated and approved, the workflow sequentially executes two custom APIs: first, shutdown\_linux to safely power down the servers, followed by decom\_linux to decommission the systems. ( Execute Decom workflow to update your CMDB)

Use ServiceNow API to update the status of Change Request CHG0001001.



Upon completion or in the event of an error, an automated email notification containing the success or failure status is sent to ashutosh.mohanty@gmail.com





\[START] ──► \[Validate ServiceNow Change] ──►\[Shutdown /Decommission Hosts] ──► \[Close ServiceNow Change] ──► \[Send Success Email] ──► \[END]

