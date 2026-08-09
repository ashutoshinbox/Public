OS Troubleshooting Agent

Check this server and determine whether CPU, memory, or disk could be causing performance problems.
If disk usage is critical, clean old temporary files and verify the result.


                    USER
                      │
                      ▼
              ┌───────────────┐
              │   LLM Agent        │
              │                    │
              │ Analyze            │
              │ Decide             │
              │ Next action        │
              └───────┬───────┘
                         │
             ┌────────┴────────┐
             ▼                       ▼
           LINUX                   WINDOWS
             │                       │
     ┌─────┴─────┐      ┌─────┴─────┐
       │ OS Tools  │         │ OS Tools   │
       │           │         │            │
       │ CPU       │         │ CPU        │
       │ Memory    │         │ Memory     │
       │ Disk      │         │ Disk       │
       │ Cleanup   │         │ Cleanup    │
      └─────┬─────┘     └─────┬─────┘
             │                       │
             └────────┬────────┘
                         ▼
                     OBSERVATION
                         │
                         ▼
                 ┌───────────┐
                 │      LLM     │
                 │              │
                 │   What next? │
                 └─────┬─────┘
                         │
                         ▼
                       VERIFY
                         │
                         ▼
                       FINISH