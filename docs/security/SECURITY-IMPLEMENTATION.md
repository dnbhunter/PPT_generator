# Security Implementation Guide

## Overview

This document provides comprehensive security implementation guidelines for the DNB Presentation Generator, ensuring compliance with banking regulations and enterprise security standards.

## Security Architecture

### Defense in Depth

Our security implementation follows a layered defense strategy:

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│                     API Gateway                             │
├─────────────────────────────────────────────────────────────┤
│                    Network Layer                            │
├─────────────────────────────────────────────────────────────┤
│                Infrastructure Layer                         │
└─────────────────────────────────────────────────────────────┘
```

### 1. Authentication & Authorization

#### Azure AD Integration

```python
# Implementation in src/core/auth.py
from azure.identity import DefaultAzureCredential
from msal import ConfidentialClientApplication

class AzureADAuth:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}"
        )
    
    async def validate_token(self, token: str) -> Optional[User]:
        """Validate Azure AD token and return user info"""
        try:
            # Validate token against Azure AD
            result = await self.app.acquire_token_silent(
                scopes=["https://graph.microsoft.com/.default"],
                account=token
            )
            return self._extract_user_info(result)
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return None
```

#### Role-Based Access Control (RBAC)

```python
from enum import Enum
from functools import wraps

class Permission(str, Enum):
    READ_PRESENTATIONS = "presentations:read"
    CREATE_PRESENTATIONS = "presentations:create"
    DELETE_PRESENTATIONS = "presentations:delete"
    ADMIN_ACCESS = "admin:access"
    EXPORT_PRESENTATIONS = "presentations:export"

class Role(str, Enum):
    VIEWER = "viewer"
    CREATOR = "creator"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"

ROLE_PERMISSIONS = {
    Role.VIEWER: [Permission.READ_PRESENTATIONS],
    Role.CREATOR: [
        Permission.READ_PRESENTATIONS,
        Permission.CREATE_PRESENTATIONS,
        Permission.EXPORT_PRESENTATIONS
    ],
    Role.ADMIN: [*Permission],
    Role.COMPLIANCE_OFFICER: [
        Permission.READ_PRESENTATIONS,
        Permission.ADMIN_ACCESS
    ]
}

def requires_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = get_current_user()
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 2. Input Validation & Sanitization

#### Request Validation

```python
from pydantic import BaseModel, validator, Field
import bleach
import re

class DocumentUploadRequest(BaseModel):
    filename: str = Field(..., max_length=255)
    file_size: int = Field(..., gt=0, le=50_000_000)  # 50MB max
    content_type: str
    
    @validator('filename')
    def validate_filename(cls, v):
        # Remove any path traversal attempts
        v = os.path.basename(v)
        # Only allow safe characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Invalid filename characters')
        return v
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/markdown'
        ]
        if v not in allowed_types:
            raise ValueError('Unsupported file type')
        return v

class PresentationRequest(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    
    @validator('title', 'description')
    def sanitize_html(cls, v):
        if v:
            return bleach.clean(v, tags=[], strip=True)
        return v
```

#### SQL Injection Prevention

```python
from sqlalchemy import text
from sqlalchemy.orm import Session

class SecureRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_presentations(self, user_id: UUID) -> List[Presentation]:
        # Use parameterized queries to prevent SQL injection
        query = text("""
            SELECT * FROM presentations 
            WHERE user_id = :user_id 
            AND deleted_at IS NULL
            ORDER BY created_at DESC
        """)
        result = await self.db.execute(query, {"user_id": str(user_id)})
        return [Presentation.from_orm(row) for row in result.fetchall()]
```

### 3. Data Protection

#### Encryption at Rest

```python
from cryptography.fernet import Fernet
from azure.keyvault.secrets import SecretClient

class EncryptionService:
    def __init__(self, key_vault_url: str):
        self.key_vault_client = SecretClient(
            vault_url=key_vault_url,
            credential=DefaultAzureCredential()
        )
        self._encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self._encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """Retrieve encryption key from Azure Key Vault"""
        secret = self.key_vault_client.get_secret("data-encryption-key")
        return secret.value.encode()
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storing"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data after retrieval"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

#### PII Detection & Redaction

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PIIProtectionService:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Configure for Norwegian/European PII patterns
        self.pii_entities = [
            "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", 
            "CREDIT_CARD", "IBAN_CODE", "NO_SSN",  # Norwegian SSN
            "LOCATION", "DATE_TIME", "ORGANIZATION"
        ]
    
    async def detect_pii(self, text: str) -> List[Dict]:
        """Detect PII in text content"""
        results = self.analyzer.analyze(
            text=text,
            entities=self.pii_entities,
            language='no'  # Norwegian
        )
        return [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score
            }
            for result in results
        ]
    
    async def redact_pii(self, text: str, redaction_type: str = "replace") -> str:
        """Redact PII from text"""
        analyzer_results = self.analyzer.analyze(
            text=text,
            entities=self.pii_entities,
            language='no'
        )
        
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={"DEFAULT": OperatorConfig(redaction_type)}
        )
        
        return anonymized_result.text
```

### 4. Content Safety & Compliance

#### Content Filtering

```python
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential

class ContentSafetyService:
    def __init__(self, endpoint: str, key: str):
        self.client = ContentSafetyClient(
            endpoint, 
            AzureKeyCredential(key)
        )
        
        # Define safety thresholds for banking content
        self.safety_thresholds = {
            "hate": 2,      # Low tolerance
            "self_harm": 0, # Zero tolerance
            "sexual": 2,    # Low tolerance
            "violence": 2,  # Low tolerance
            "harassment": 1 # Very low tolerance
        }
    
    async def analyze_content(self, text: str) -> Dict[str, Any]:
        """Analyze content for safety violations"""
        try:
            response = self.client.analyze_text(
                text=text,
                categories=list(self.safety_thresholds.keys())
            )
            
            violations = []
            for category, threshold in self.safety_thresholds.items():
                severity = getattr(response, category, 0)
                if severity > threshold:
                    violations.append({
                        "category": category,
                        "severity": severity,
                        "threshold": threshold
                    })
            
            return {
                "safe": len(violations) == 0,
                "violations": violations,
                "analysis": response
            }
        except Exception as e:
            logger.error(f"Content safety analysis failed: {e}")
            # Fail closed - assume unsafe
            return {"safe": False, "error": str(e)}
```

#### Compliance Validation

```python
class ComplianceValidator:
    def __init__(self):
        self.forbidden_terms = self._load_forbidden_terms()
        self.required_disclaimers = self._load_disclaimers()
    
    def _load_forbidden_terms(self) -> List[str]:
        """Load terms forbidden in banking presentations"""
        return [
            "guaranteed returns", "risk-free", "insider information",
            "market manipulation", "tax evasion", "money laundering"
        ]
    
    async def validate_presentation_content(
        self, 
        presentation: PresentationData
    ) -> ComplianceResult:
        """Validate presentation for compliance violations"""
        violations = []
        
        # Check for forbidden terms
        content = self._extract_all_text(presentation)
        for term in self.forbidden_terms:
            if term.lower() in content.lower():
                violations.append(
                    ComplianceViolation(
                        type="forbidden_term",
                        description=f"Contains forbidden term: {term}",
                        severity="high"
                    )
                )
        
        # Check for required disclaimers
        if not self._has_required_disclaimers(presentation):
            violations.append(
                ComplianceViolation(
                    type="missing_disclaimer",
                    description="Required disclaimers not found",
                    severity="medium"
                )
            )
        
        # Check for proper risk disclosures
        if self._contains_financial_advice(content):
            if not self._has_risk_disclosure(content):
                violations.append(
                    ComplianceViolation(
                        type="missing_risk_disclosure",
                        description="Financial advice without risk disclosure",
                        severity="high"
                    )
                )
        
        return ComplianceResult(
            compliant=len(violations) == 0,
            violations=violations
        )
```

### 5. Secure Communication

#### TLS Configuration

```python
# In production deployment
import ssl
from fastapi import FastAPI
import uvicorn

def create_ssl_context() -> ssl.SSLContext:
    """Create secure SSL context"""
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(
        certfile="/path/to/cert.pem",
        keyfile="/path/to/key.pem"
    )
    
    # Strong security settings
    context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS")
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_TLSv1
    context.options |= ssl.OP_NO_TLSv1_1
    
    return context

if __name__ == "__main__":
    ssl_context = create_ssl_context()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=443,
        ssl_context=ssl_context
    )
```

#### Request Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/generate/presentation")
@limiter.limit("10/minute")  # Limit to 10 generations per minute
async def generate_presentation(
    request: Request,
    data: PresentationRequest,
    current_user: User = Depends(get_current_user)
):
    # Implementation
    pass
```

### 6. Logging & Monitoring

#### Security Event Logging

```python
import structlog
from typing import Optional

logger = structlog.get_logger()

class SecurityLogger:
    @staticmethod
    def log_authentication_event(
        user_id: Optional[str],
        event_type: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        additional_context: Dict = None
    ):
        logger.info(
            "authentication_event",
            user_id=user_id,
            event_type=event_type,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            **additional_context or {}
        )
    
    @staticmethod
    def log_authorization_event(
        user_id: str,
        resource: str,
        action: str,
        granted: bool,
        required_permission: str
    ):
        logger.info(
            "authorization_event",
            user_id=user_id,
            resource=resource,
            action=action,
            granted=granted,
            required_permission=required_permission
        )
    
    @staticmethod
    def log_data_access(
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        sensitive_data: bool = False
    ):
        logger.info(
            "data_access_event",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            sensitive_data=sensitive_data
        )

    @staticmethod
    def log_security_violation(
        user_id: Optional[str],
        violation_type: str,
        description: str,
        severity: str,
        ip_address: str,
        additional_context: Dict = None
    ):
        logger.warning(
            "security_violation",
            user_id=user_id,
            violation_type=violation_type,
            description=description,
            severity=severity,
            ip_address=ip_address,
            **additional_context or {}
        )
```

#### Anomaly Detection

```python
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class AnomalyDetector:
    def __init__(self):
        self.user_activity = defaultdict(list)
        self.thresholds = {
            "requests_per_minute": 100,
            "failed_auth_attempts": 5,
            "large_file_uploads": 5,  # per hour
            "rapid_generation_requests": 10  # per minute
        }
    
    async def detect_anomalies(
        self, 
        user_id: str, 
        event_type: str,
        metadata: Dict = None
    ) -> Optional[SecurityAlert]:
        """Detect anomalous user behavior"""
        now = datetime.utcnow()
        
        # Track user activity
        self.user_activity[user_id].append({
            "timestamp": now,
            "event_type": event_type,
            "metadata": metadata or {}
        })
        
        # Clean old activity (older than 1 hour)
        cutoff = now - timedelta(hours=1)
        self.user_activity[user_id] = [
            activity for activity in self.user_activity[user_id]
            if activity["timestamp"] > cutoff
        ]
        
        # Check for anomalies
        recent_activity = [
            a for a in self.user_activity[user_id]
            if a["timestamp"] > now - timedelta(minutes=1)
        ]
        
        if len(recent_activity) > self.thresholds["requests_per_minute"]:
            return SecurityAlert(
                type="high_request_rate",
                user_id=user_id,
                description=f"User making {len(recent_activity)} requests per minute",
                severity="high"
            )
        
        # Check for failed authentication attempts
        failed_auths = [
            a for a in recent_activity
            if a["event_type"] == "authentication_failed"
        ]
        
        if len(failed_auths) > self.thresholds["failed_auth_attempts"]:
            return SecurityAlert(
                type="brute_force_attempt",
                user_id=user_id,
                description=f"Multiple failed authentication attempts",
                severity="critical"
            )
        
        return None
```

### 7. Incident Response

#### Automated Response System

```python
class SecurityIncidentResponse:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
        self.response_actions = {
            "brute_force_attempt": self._handle_brute_force,
            "content_safety_violation": self._handle_content_violation,
            "pii_exposure": self._handle_pii_exposure,
            "privilege_escalation": self._handle_privilege_escalation
        }
    
    async def handle_security_alert(self, alert: SecurityAlert):
        """Handle security alerts with appropriate response"""
        handler = self.response_actions.get(alert.type)
        if handler:
            await handler(alert)
        
        # Always log the incident
        await self._log_incident(alert)
        
        # Notify security team for high/critical severity
        if alert.severity in ["high", "critical"]:
            await self._notify_security_team(alert)
    
    async def _handle_brute_force(self, alert: SecurityAlert):
        """Handle brute force attack attempts"""
        # Temporarily block the user/IP
        await self._temporary_block_user(alert.user_id, duration_minutes=30)
        
        # Require additional authentication
        await self._require_mfa(alert.user_id)
    
    async def _handle_content_violation(self, alert: SecurityAlert):
        """Handle content safety violations"""
        # Block the content
        if alert.resource_id:
            await self._quarantine_content(alert.resource_id)
        
        # Flag for manual review
        await self._flag_for_review(alert)
    
    async def _handle_pii_exposure(self, alert: SecurityAlert):
        """Handle PII exposure incidents"""
        # Immediately quarantine the content
        if alert.resource_id:
            await self._quarantine_content(alert.resource_id)
        
        # Notify compliance team
        await self._notify_compliance_team(alert)
        
        # Create audit trail
        await self._create_audit_record(alert)
```

## Security Testing

### Penetration Testing Checklist

```python
class SecurityTestSuite:
    """Automated security testing suite"""
    
    async def test_authentication_bypass(self):
        """Test for authentication bypass vulnerabilities"""
        test_cases = [
            {"token": None, "expected": 401},
            {"token": "invalid", "expected": 401},
            {"token": "expired", "expected": 401},
            {"token": "malformed", "expected": 401}
        ]
        
        for case in test_cases:
            response = await self.client.get(
                "/api/v1/presentations",
                headers={"Authorization": f"Bearer {case['token']}"}
            )
            assert response.status_code == case["expected"]
    
    async def test_sql_injection(self):
        """Test for SQL injection vulnerabilities"""
        injection_payloads = [
            "'; DROP TABLE presentations; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in injection_payloads:
            response = await self.client.get(
                f"/api/v1/presentations?search={payload}"
            )
            # Should not return sensitive data or error
            assert response.status_code in [400, 404]
            assert "error" not in response.json().get("data", {})
    
    async def test_file_upload_security(self):
        """Test file upload security measures"""
        malicious_files = [
            ("malware.exe", b"MZ\x90\x00", "application/octet-stream"),
            ("script.js", b"<script>alert('xss')</script>", "text/javascript"),
            ("../../etc/passwd", b"root:x:0:0", "text/plain")
        ]
        
        for filename, content, content_type in malicious_files:
            response = await self.client.post(
                "/api/v1/documents/upload",
                files={"file": (filename, content, content_type)}
            )
            # Should reject malicious files
            assert response.status_code in [400, 415]
```

## Deployment Security

### Infrastructure Security

```yaml
# infrastructure/bicep/security.bicep
resource networkSecurityGroup 'Microsoft.Network/networkSecurityGroups@2021-02-01' = {
  name: 'nsg-presentation-generator'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowHTTPSInbound'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 1000
          direction: 'Inbound'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Deny'
          priority: 4096
          direction: 'Inbound'
        }
      }
    ]
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: 'kv-presentation-generator'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'premium'  // Hardware Security Module
    }
    tenantId: tenant().tenantId
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    networkAcls: {
      defaultAction: 'Deny'
      virtualNetworkRules: [
        {
          id: subnet.id
          ignoreMissingVnetServiceEndpoint: false
        }
      ]
    }
  }
}
```

### Container Security

```dockerfile
# Use minimal, security-hardened base image
FROM mcr.microsoft.com/cbl-mariner/python:3.11-core

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install security updates
RUN tdnf update -y && tdnf clean all

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ /app/src/
WORKDIR /app

# Set secure file permissions
RUN chown -R appuser:appuser /app
RUN chmod -R 755 /app

# Switch to non-root user
USER appuser

# Security labels
LABEL security.scan=required
LABEL security.updates=automatic

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose only necessary port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Security Checklist

### Pre-Deployment

- [ ] All secrets stored in Azure Key Vault
- [ ] TLS 1.3 configured with strong cipher suites
- [ ] Rate limiting implemented for all endpoints
- [ ] Input validation and sanitization in place
- [ ] SQL injection prevention measures active
- [ ] PII detection and redaction enabled
- [ ] Content safety filters configured
- [ ] RBAC permissions properly defined
- [ ] Security headers configured
- [ ] Audit logging enabled
- [ ] Anomaly detection rules active
- [ ] Incident response procedures tested

### Post-Deployment

- [ ] Penetration testing completed
- [ ] Vulnerability scans passed
- [ ] Security monitoring alerts configured
- [ ] Backup and recovery procedures tested
- [ ] Compliance validation completed
- [ ] Security incident response plan activated
- [ ] Regular security reviews scheduled
- [ ] Security awareness training completed

## Compliance Framework

### Regulatory Requirements

1. **GDPR Compliance**
   - Data minimization
   - Consent management
   - Right to erasure
   - Data portability
   - Privacy by design

2. **PCI DSS** (if handling payment data)
   - Secure cardholder data environment
   - Strong access controls
   - Regular security testing
   - Information security policy

3. **SOX Compliance**
   - Financial data integrity
   - Audit trails
   - Segregation of duties
   - Change management controls

4. **Norwegian Banking Regulations**
   - Data residency requirements
   - Risk management
   - Operational resilience
   - Customer protection

### Audit Trail Requirements

```python
class AuditLogger:
    """Comprehensive audit logging for compliance"""
    
    def __init__(self):
        self.audit_logger = structlog.get_logger("audit")
    
    async def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        ip_address: str,
        user_agent: str
    ):
        """Log all data access for audit purposes"""
        self.audit_logger.info(
            "data_access",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_configuration_change(
        self,
        user_id: str,
        component: str,
        old_value: str,
        new_value: str,
        change_reason: str
    ):
        """Log configuration changes for compliance"""
        self.audit_logger.info(
            "configuration_change",
            user_id=user_id,
            component=component,
            old_value=old_value,
            new_value=new_value,
            change_reason=change_reason,
            timestamp=datetime.utcnow().isoformat()
        )
```

This security implementation provides comprehensive protection while maintaining compliance with banking regulations and enterprise security standards.
