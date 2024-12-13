flowchart 
    A(User Input) --ChatAgent.chat--> B[Interaction Loop]
    B --agent response-->C(Interaction complete)
    
    AA[interaction loop] --> AB[setup completion]
    AB --> AC[completion_running==true event]
    AC --> AD[run compeletion]
    AD --> AE[completion_running==false event]
    AE --> AF{Agent executing tools?}
        
    AF -->|Yes|AFT[[reponse streaming loop]]
    AFT --token-->AFY
    AFY{1st token this completion?}
    AFY -->|Yes|AFYY[start==true event]
    AFY -->|No|AFYN[content event]
    AFYY --> AFYN
    AFYN --> SR{intreraction complete?}
    SR --> |Yes| SRY[message event]
    SRY --> SRYE(loop end)
    SR --> |No| AB
    
    AF -->|No| AFN[build tool call array]
    AFN --> AFNA[tool_use_active=true event]
    AFNA --> AFNB[[parallel tool calls]]
    AFNB --> AFNC[tool_use_active=false event]
    AFNC --> AB
