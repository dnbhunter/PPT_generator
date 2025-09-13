# DNB Presentation Generator - Architecture Diagram

## Current Unified Architecture (Post-Cleanup)

```mermaid
graph TB
    %% User Interface Layer
    subgraph "Frontend"
        UI[Web Interface<br/>frontend/index.html]
        UI --> |HTTP POST| API
    end

    %% API Gateway Layer
    subgraph "Unified FastAPI Server"
        API[src/main.py<br/>Unified Entrypoint]
        API --> |Include Router| GEN[generation.py<br/>POST /api/v1/generate]
        API --> |Include Router| PRES[presentations.py<br/>GET /api/v1/presentations/{id}/download]
        API --> |Mount Static| STATIC[/frontend static files]
        API --> |Health Check| HEALTH[GET /health]
    end

    %% Agent Orchestration Layer
    subgraph "Multi-Agent System"
        ORCH[MultiAgentOrchestrator<br/>src/agents/orchestrator.py]
        
        subgraph "Specialized Agents"
            PLAN[Planner Agent<br/>Requirements Analysis]
            RES[Research Agent<br/>Content Research]
            CONT[Content Agent<br/>Slide Generation]
            ARCH[Architect Agent<br/>Structure Design]
            QA[QA/Compliance Agent<br/>Quality Control]
            EXP[Export Agent<br/>Final Processing]
        end
        
        ORCH --> PLAN
        ORCH --> RES
        ORCH --> CONT
        ORCH --> ARCH
        ORCH --> QA
        ORCH --> EXP
    end

    %% Core Services Layer
    subgraph "Core Services"
        CFG[Configuration<br/>src/core/config.py]
        LOG[Logging<br/>src/core/logging.py]
        EXC[Exceptions<br/>src/core/exceptions.py]
        CONST[Constants<br/>src/core/constants.py]
    end

    %% External Services Layer
    subgraph "External Integrations"
        AZURE[Azure Services<br/>src/services/azure_services.py]
        CACHE[Cache Service<br/>src/services/cache_service.py]
        DB[Database<br/>src/services/database.py]
    end

    %% File Generation Layer
    subgraph "PPTX Generation"
        PPTX[python-pptx Library]
        EXPORTS[exports/ Directory<br/>Generated Files]
    end

    %% Flow Connections
    GEN --> |Initialize| ORCH
    ORCH --> |Use Config| CFG
    ORCH --> |Log Events| LOG
    ORCH --> |Handle Errors| EXC
    ORCH --> |Use Constants| CONST
    
    %% Agent Service Connections
    RES --> |Query| AZURE
    CONT --> |Cache Results| CACHE
    EXP --> |Generate PPTX| PPTX
    PPTX --> |Save File| EXPORTS
    
    %% Download Flow
    PRES --> |Serve File| EXPORTS
    EXPORTS --> |FileResponse| UI

    %% Automation Script
    subgraph "Automation"
        SCRIPT[run_minimal.ps1<br/>End-to-End Testing]
        SCRIPT --> |Start Server| API
        SCRIPT --> |Test Health| HEALTH
        SCRIPT --> |Test Generation| GEN
        SCRIPT --> |Download File| PRES
    end

    %% Deprecated Components (Shown for Reference)
    subgraph "Deprecated (Marked but Preserved)" 
        style DEP fill:#ffcccc,stroke:#ff6666
        DEP[Complex Router System<br/>main.py, src/api/main.py<br/>Multiple startup scripts<br/>Test files]
    end

    %% Styling
    classDef active fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef agent fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef service fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef deprecated fill:#ffebee,stroke:#c62828,stroke-width:1px,stroke-dasharray: 5 5

    class API,GEN,PRES,UI active
    class ORCH,PLAN,RES,CONT,ARCH,QA,EXP agent
    class CFG,LOG,AZURE,CACHE,PPTX service
    class DEP deprecated
```

## Simplified Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as src/main.py
    participant Orchestrator as MultiAgentOrchestrator
    participant Agents as Specialized Agents
    participant PPTX as python-pptx
    participant Files as exports/

    User->>Frontend: Fill form & submit
    Frontend->>API: POST /api/v1/generate
    API->>Orchestrator: Initialize with request
    
    Note over Orchestrator,Agents: Multi-agent processing
    Orchestrator->>Agents: Coordinate workflow
    Agents-->>Orchestrator: Return results
    
    Orchestrator->>PPTX: Generate presentation
    PPTX->>Files: Save .pptx file
    API-->>Frontend: Return file ID
    
    Frontend->>API: GET /api/v1/presentations/{id}/download
    API->>Files: Retrieve file
    Files-->>API: File content
    API-->>Frontend: FileResponse (PPTX)
    Frontend-->>User: Download starts
```

## Component Status After Cleanup

```mermaid
pie title Component Status
    "Active Core Components" : 15
    "Deprecated but Preserved" : 12
    "Removed/Cleaned" : 3
```

## Key Architecture Decisions

### ✅ **Unified Entrypoint**
- Single `src/main.py` replaces complex router aggregation
- Direct router inclusion vs. nested API structure
- Simplified middleware stack

### ✅ **Agent Integration**
- MultiAgentOrchestrator properly initialized
- 6 specialized agents working in coordination
- State management between agents

### ✅ **Real PPTX Generation**
- python-pptx library for actual PowerPoint files
- Exports directory for file storage
- Proper MIME type handling for downloads

### ✅ **Development Automation**
- PowerShell script for end-to-end testing
- Health checks and validation
- Automated file generation and download

### ⚠️ **Networking Considerations**
- Server startup works correctly
- HTTP request handling may need investigation for production
- Core functionality validated independently
