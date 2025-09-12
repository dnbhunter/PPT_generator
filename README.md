# DNB Presentation Generator

## Project Structure

```
PPT_generator/
├── README.md                           # Project overview and setup
├── ARCHITECTURE.md                     # Detailed architecture documentation
├── requirements.txt                    # Python dependencies
├── requirements-dev.txt                # Development dependencies
├── pyproject.toml                      # Project configuration
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore rules
├── Dockerfile                          # Container configuration
├── docker-compose.yml                  # Local development setup
├── 
├── src/                                # Source code
│   ├── __init__.py
│   ├── main.py                         # Application entry point
│   │
│   ├── agents/                         # LangGraph multi-agent system
│   │   ├── __init__.py
│   │   ├── orchestrator.py             # Main agent coordinator
│   │   ├── planner_agent.py            # Requirements analysis agent
│   │   ├── research_agent.py           # Content research and validation
│   │   ├── content_agent.py            # Slide content generation
│   │   ├── architect_agent.py          # Technical architecture decisions
│   │   ├── qa_compliance_agent.py      # Quality assurance and compliance
│   │   ├── export_agent.py             # Final export and formatting
│   │   └── base_agent.py               # Base agent class
│   │
│   ├── api/                            # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py                     # API entry point
│   │   ├── routes/                     # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── health.py               # Health check endpoints
│   │   │   ├── auth.py                 # Authentication endpoints
│   │   │   ├── presentations.py        # Presentation CRUD operations
│   │   │   ├── generation.py           # Generation workflow endpoints
│   │   │   ├── assets.py               # Asset management endpoints
│   │   │   └── admin.py                # Administrative endpoints
│   │   ├── middleware/                 # Custom middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # Authentication middleware
│   │   │   ├── cors.py                 # CORS handling
│   │   │   ├── rate_limiting.py        # Rate limiting
│   │   │   ├── audit.py                # Audit logging
│   │   │   └── security.py             # Security headers
│   │   └── dependencies.py             # FastAPI dependencies
│   │
│   ├── core/                           # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py                   # Configuration management
│   │   ├── exceptions.py               # Custom exceptions
│   │   ├── constants.py                # Application constants
│   │   └── logging.py                  # Logging configuration
│   │
│   ├── models/                         # Data models
│   │   ├── __init__.py
│   │   ├── presentation.py             # Presentation data models
│   │   ├── slide.py                    # Slide data models
│   │   ├── user.py                     # User and auth models
│   │   ├── job.py                      # Job queue models
│   │   ├── audit.py                    # Audit log models
│   │   └── schemas.py                  # Pydantic schemas
│   │
│   ├── services/                       # Service layer
│   │   ├── __init__.py
│   │   ├── document_processor.py       # Document parsing and ingestion
│   │   ├── llm_service.py              # Azure OpenAI integration
│   │   ├── presentation_generator.py   # Core presentation logic
│   │   ├── chart_generator.py          # Chart and visualization creation
│   │   ├── theme_engine.py             # Brand and theme management
│   │   ├── asset_manager.py            # Digital asset management
│   │   ├── export_service.py           # PPTX/PDF export functionality
│   │   ├── job_queue.py                # Background job processing
│   │   ├── cache_service.py            # Caching layer
│   │   └── notification_service.py     # User notifications
│   │
│   ├── security/                       # Security and compliance
│   │   ├── __init__.py
│   │   ├── auth.py                     # Authentication logic
│   │   ├── authorization.py            # RBAC implementation
│   │   ├── pii_detection.py            # PII detection and redaction
│   │   ├── content_safety.py           # Content filtering
│   │   ├── encryption.py               # Encryption utilities
│   │   ├── audit_logger.py             # Audit trail logging
│   │   ├── compliance_checker.py       # Regulatory compliance
│   │   └── secrets_manager.py          # Secrets management
│   │
│   └── utils/                          # Utility functions
│       ├── __init__.py
│       ├── file_utils.py               # File operations
│       ├── text_utils.py               # Text processing utilities
│       ├── validation.py               # Input validation
│       ├── accessibility.py            # Accessibility helpers
│       ├── brand_utils.py              # Brand guideline utilities
│       └── monitoring.py               # Telemetry and monitoring
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration
│   ├── unit/                           # Unit tests
│   │   ├── test_agents/
│   │   ├── test_services/
│   │   ├── test_security/
│   │   └── test_utils/
│   ├── integration/                    # Integration tests
│   │   ├── test_api/
│   │   ├── test_workflows/
│   │   └── test_external_services/
│   ├── e2e/                           # End-to-end tests
│   │   ├── test_presentation_generation.py
│   │   ├── test_user_workflows.py
│   │   └── test_compliance.py
│   ├── performance/                    # Performance tests
│   │   ├── test_load.py
│   │   └── test_stress.py
│   ├── security/                       # Security tests
│   │   ├── test_penetration.py
│   │   ├── test_red_team.py
│   │   └── test_vulnerability.py
│   └── fixtures/                       # Test data
│       ├── sample_documents/
│       ├── golden_presentations/
│       └── mock_responses/
│
├── frontend/                           # React frontend application
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── index.html
│   ├── public/
│   │   ├── favicon.ico
│   │   └── robots.txt
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── components/
│       │   ├── common/
│       │   ├── presentation/
│       │   ├── upload/
│       │   ├── preview/
│       │   ├── theme/
│       │   └── admin/
│       ├── pages/
│       ├── hooks/
│       ├── services/
│       ├── store/
│       ├── types/
│       ├── utils/
│       └── styles/
│
├── infrastructure/                     # Infrastructure as Code
│   ├── bicep/                         # Azure Bicep templates
│   │   ├── main.bicep
│   │   ├── modules/
│   │   │   ├── app-service.bicep
│   │   │   ├── container-apps.bicep
│   │   │   ├── key-vault.bicep
│   │   │   ├── storage.bicep
│   │   │   ├── cognitive-services.bicep
│   │   │   └── networking.bicep
│   │   └── parameters/
│   │       ├── dev.bicepparam
│   │       ├── test.bicepparam
│   │       └── prod.bicepparam
│   ├── terraform/                     # Alternative Terraform (if needed)
│   └── k8s/                          # Kubernetes manifests (if needed)
│
├── config/                            # Configuration files
│   ├── logging.yaml                   # Logging configuration
│   ├── brand/                         # Brand configuration
│   │   ├── dnb_theme.json
│   │   ├── slide_templates.json
│   │   └── color_palette.json
│   ├── compliance/                    # Compliance rules
│   │   ├── pii_patterns.json
│   │   ├── content_policies.json
│   │   └── accessibility_rules.json
│   └── deployment/                    # Deployment configurations
│       ├── dev.yaml
│       ├── test.yaml
│       └── prod.yaml
│
├── assets/                            # Static assets
│   ├── templates/                     # Presentation templates
│   │   ├── corporate.pptx
│   │   ├── executive.pptx
│   │   └── research.pptx
│   ├── images/                        # Approved image library
│   │   ├── logos/
│   │   ├── icons/
│   │   └── backgrounds/
│   ├── fonts/                         # Corporate fonts
│   └── schemas/                       # JSON schemas
│       ├── openapi.yaml
│       ├── presentation.schema.json
│       └── slide.schema.json
│
├── docs/                              # Documentation
│   ├── api/                           # API documentation
│   │   ├── openapi.yaml
│   │   └── postman_collection.json
│   ├── user/                          # User documentation
│   │   ├── user_guide.md
│   │   ├── accessibility_guide.md
│   │   └── troubleshooting.md
│   ├── admin/                         # Administrator documentation
│   │   ├── deployment_guide.md
│   │   ├── monitoring_guide.md
│   │   ├── security_guide.md
│   │   └── backup_recovery.md
│   ├── developer/                     # Developer documentation
│   │   ├── contributing.md
│   │   ├── code_standards.md
│   │   ├── testing_guide.md
│   │   └── architecture_decisions/
│   └── compliance/                    # Compliance documentation
│       ├── security_model.md
│       ├── data_flow_analysis.md
│       ├── privacy_impact_assessment.md
│       └── audit_procedures.md
│
├── .github/                           # GitHub workflows
│   └── workflows/
│       ├── ci.yml
│       ├── cd.yml
│       ├── security-scan.yml
│       └── dependency-check.yml
│
└── scripts/                           # Utility scripts
    ├── setup.py                       # Environment setup
    ├── deploy.py                      # Deployment automation
    ├── backup.py                      # Backup utilities
    ├── health_check.py                # Health monitoring
    └── data_migration.py              # Data migration tools
```

## Key Features

### 🔒 Security First
- Enterprise SSO integration
- PII detection and redaction
- Audit logging for all operations
- Content safety filters
- Zero data egress policy

### 🤖 Multi-Agent Architecture
- LangGraph-powered agent coordination
- Specialized agents for each workflow stage
- State management and error recovery
- Parallel processing capabilities

### 🎨 Brand Compliance
- DNB corporate themes and templates
- Automatic brand guideline enforcement
- WCAG 2.1 AA accessibility compliance
- Professional chart generation

### 📊 Enterprise Integration
- Azure OpenAI with private endpoints
- Corporate asset management integration
- Knowledge base connectivity
- Policy engine compliance

### 🚀 Production Ready
- Container-based deployment
- Infrastructure as Code (Bicep)
- Comprehensive monitoring
- Auto-scaling capabilities

## Technology Stack

- **Backend**: Python 3.11, FastAPI, LangGraph
- **AI/ML**: Azure OpenAI GPT-4o, Azure Cognitive Services
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Database**: Azure SQL Database, Redis Cache
- **Infrastructure**: Azure Container Apps, Azure Key Vault
- **Security**: Azure AD, Presidio PII Detection
- **Export**: python-pptx, WeasyPrint, matplotlib

## Quick Start

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd PPT_generator
   ```

2. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

4. **Run Development Server**
   ```bash
   python src/main.py
   ```

5. **Access Application**
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## Security & Compliance

This application is designed for enterprise banking environments with strict security requirements:

- **Data Protection**: All data encrypted at rest and in transit
- **Access Control**: Role-based access with Azure AD integration
- **Audit Trail**: Comprehensive logging of all user actions
- **PII Handling**: Automatic detection and redaction of sensitive data
- **Compliance**: GDPR, EBA guidelines, and WCAG 2.1 AA compliance

## License

Proprietary - DNB Bank ASA. All rights reserved.