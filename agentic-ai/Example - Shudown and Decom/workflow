  [Start Run]
                     │
                     ▼
          ┌───────────────────┐
          │  Check SNOW State │
          └──────────┬────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
   [Not Approved]           [Approved State]
         │                       │
         ▼                       ▼
   ┌─────────┐     ┌──────────────┐
   │ Mail Fail │        │ Shutdown     │
   └────┬────┘      │ (Parallel)   │
         │             └──────┬───────┘
         ▼                      │
       [End]                     ▼
                          ┌────────────┐
                          │ Decommission │
                          │ (Parallel)   │
                          └─────┬──────┘
                                 │
                       ┌─────────┴─────────┐
                       ▼                   ▼
                   [Success]           [Failure]
                       │                   │
                       ▼                   ▼
                ┌──────────┐     ┌───────────┐
                │ Close Ticket │     │ Mail Fail │
                └──────┬───┘     └─────┬─────┘
                       │                   │
                       ▼                   ▼
                 ┌────────┐           [End]
                 │Mail Success │
                 └───┬────┘
                       │
                       ▼
                     [End]