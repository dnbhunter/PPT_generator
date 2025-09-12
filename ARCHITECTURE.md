# Architecture Documentation - Text-to-Presentation Generator

## Executive Summary
Enterprise-grade text-to-presentation generator designed for private banking with multi-agent architecture, built on LangGraph and Azure OpenAI, meeting strict compliance and security requirements.

## System Context (C4 Level 1)

```mermaid
graph TB
    Users[Bank Employees] --> WebUI[Presentation Generator Web UI]
    WebUI --> API[API Gateway]
    API --> Core[Core Orchestrator]
    
    Core --> Azure[Azure OpenAI Service]
    Core --> Storage[Enterprise Storage]
    Core --> SSO[Corporate SSO/IdP]
    Core --> Assets[Digital Asset Management]
    Core --> KnowledgeBase[Bank Knowledge Base]
    
    subgraph "External Bank Systems"
        SSO
        Assets
        KnowledgeBase
        PolicyEngine[DLP/Policy Engine]
    end
    
    subgraph "Azure Cloud (Private VNet)"
        Azure
        Storage
        AuditLog[Audit & Compliance]
    end
```

## Container Architecture (C4 Level 2)

```mermaid
graph TB
    subgraph "Presentation Layer"
        WebApp[React Web Application]
        Preview[Live Preview Service]
    end
    
    subgraph "API & Orchestration"
        Gateway[API Gateway]
        Auth[Authentication Service]
        Orchestrator[Multi-Agent Orchestrator]
    end
    
    subgraph "Multi-Agent System (LangGraph)"
        Planner[Planner Agent]
        Research[Research Agent]
        Content[Content Agent]
        Architect[Architect Agent]
        QA[QA/Compliance Agent]
        Export[Export Agent]
    end
    
    subgraph "Core Services"
        DocProcessor[Document Processing]
        PIIRedactor[PII Redaction]
        ChartGen[Chart Generator]
        ThemeEngine[Theme Engine]
        AssetMgr[Asset Manager]
    end
    
    subgraph "Infrastructure"
        Queue[Job Queue]
        Cache[Redis Cache]
        Audit[Audit Service]
        Monitor[Monitoring]
    end
    
    WebApp --> Gateway
    Gateway --> Auth
    Gateway --> Orchestrator
    Orchestrator --> Planner
    Planner --> Research
    Research --> Content
    Content --> Architect
    Architect --> QA
    QA --> Export
```

## Multi-Agent Workflow (Sequence Diagram)

```mermaid
sequenceDiagram
    participant User
    participant WebUI
    participant Orchestrator
    participant Planner
    participant Research
    participant Content
    participant QA
    participant Export
    participant AzureAI
    
    User->>WebUI: Upload document/text
    WebUI->>Orchestrator: Process request
    
    Orchestrator->>Planner: Analyze requirements
    Planner->>AzureAI: Extract structure & intent
    AzureAI-->>Planner: Analysis results
    Planner-->>Orchestrator: Presentation plan
    
    Orchestrator->>Research: Validate & enrich content
    Research->>AzureAI: Fact-check queries
    AzureAI-->>Research: Verification results
    Research-->>Orchestrator: Enriched content
    
    Orchestrator->>Content: Generate slides
    Content->>AzureAI: Create slide content
    AzureAI-->>Content: Generated slides
    Content-->>Orchestrator: Draft presentation
    
    Orchestrator->>QA: Compliance check
    QA->>QA: Accessibility audit
    QA->>QA: Brand compliance
    QA->>QA: PII detection
    QA-->>Orchestrator: Quality report
    
    Orchestrator->>Export: Generate final output
    Export-->>WebUI: PPTX/PDF ready
    WebUI-->>User: Download presentation
```

## Technology Stack Rationale

### Core Framework
- **LangGraph**: Multi-agent orchestration with state management
- **Python 3.11+**: Enterprise-approved runtime
- **FastAPI**: High-performance async API framework
- **Pydantic**: Data validation and serialization

### AI/ML Services
- **Azure OpenAI GPT-4o**: Enterprise LLM with data processing guarantees
- **Azure Cognitive Services**: Document intelligence and PII detection
- **Private endpoint**: VNet isolation, no internet egress

### Security & Compliance
- **Azure AD B2C**: Enterprise SSO integration
- **Azure Key Vault**: Secrets and certificate management
- **Azure Application Gateway**: WAF and SSL termination
- **Presidio**: Advanced PII detection and anonymization

### Data & Storage
- **Azure Blob Storage**: Document and asset storage with encryption
- **Azure Redis Cache**: Session and job state management
- **Azure SQL Database**: Audit logs and metadata

### Presentation Generation
- **python-pptx**: PPTX creation and manipulation
- **Pillow**: Image processing and chart generation
- **matplotlib/plotly**: Enterprise-approved charting
- **WeasyPrint**: PDF generation with accessibility

### Infrastructure
- **Azure Container Apps**: Serverless container hosting
- **Azure Service Bus**: Reliable message queuing
- **Application Insights**: Monitoring and telemetry
- **Bicep**: Infrastructure as Code

## Security Architecture

### Data Flow Security
```mermaid
graph LR
    User --> WAF[Web Application Firewall]
    WAF --> Gateway[API Gateway]
    Gateway --> VNet[Private VNet]
    
    subgraph VNet
        App[Application Services]
        DB[Encrypted Database]
        KeyVault[Key Vault]
        Storage[Encrypted Storage]
    end
    
    App --> Azure[Azure OpenAI Private Endpoint]
    App --> Audit[Audit Logs]
```

### Security Controls
1. **Network Isolation**: Private VNet with no internet egress
2. **Encryption**: TLS 1.3 in transit, AES-256 at rest
3. **Identity**: Azure AD with conditional access
4. **Authorization**: RBAC with fine-grained permissions
5. **Audit**: Immutable logs for all operations
6. **Content Safety**: Built-in content filtering and PII detection

## Decision Log

### Decision 1: Multi-Agent Architecture with LangGraph
**Context**: Need coordinated AI agents for complex presentation generation
**Decision**: Use LangGraph for agent orchestration
**Rationale**: 
- Native state management
- Composable agent workflows
- Enterprise Python ecosystem
- Clear separation of concerns

### Decision 2: Azure OpenAI over Other Providers
**Context**: Bank requires enterprise LLM with data guarantees
**Decision**: Azure OpenAI with private endpoints
**Rationale**:
- Data processing agreements
- Private networking
- EU data residency
- Content safety controls

### Decision 3: Container-based Deployment
**Context**: Need scalable, maintainable deployment
**Decision**: Azure Container Apps with Bicep IaC
**Rationale**:
- Serverless scaling
- Version control infrastructure
- Blue-green deployments
- Cost optimization

## Performance Requirements
- **Generation Time**: <30 seconds for 10-12 slides
- **Concurrent Users**: 100+ simultaneous sessions
- **Availability**: 99.9% uptime SLA
- **Data Residency**: EU-only processing and storage

## Compliance Framework
- **GDPR**: PII detection and right to erasure
- **EBA Guidelines**: Operational resilience
- **WCAG 2.1 AA**: Accessibility compliance
- **ISO 27001**: Information security management
- **SOC 2 Type II**: Service organization controls
