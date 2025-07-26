# STPA-Sec+ Standalone App Architecture

## Overview

This document outlines the architecture for spinning off STPA-Sec+ as a standalone enterprise security analysis platform while maximizing code reuse from the existing prototype.

## Architecture Principles

1. **Modular Design**: Separate STPA-Sec+ specific features from general analysis
2. **Shared Component Library**: Reuse UI components, utilities, and base services
3. **API-First**: All functionality exposed through well-defined APIs
4. **Plugin Architecture**: Extensible framework for adding new analysis methods
5. **Enterprise-Ready**: Multi-tenancy, RBAC, audit logging from day one

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        STPA-Sec+ Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                          Frontend Layer                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    React Application                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │   │
│  │  │  Analysis   │  │ Compliance  │  │   Executive    │  │   │
│  │  │  Workbench  │  │  Dashboard  │  │   Dashboard    │  │   │
│  │  └─────────────┘  └─────────────┘  └────────────────┘  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │   │
│  │  │     CVE     │  │  Wargaming  │  │     Admin      │  │   │
│  │  │  Explorer   │  │   Studio    │  │    Console     │  │   │
│  │  └─────────────┘  └─────────────┘  └────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                      Shared Components                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ @security-platform/ui-components                          │  │
│  │ ├── AnalysisTable    ├── HeatMap      ├── FlowDiagram   │  │
│  │ ├── RiskMatrix       ├── ChatPanel    ├── VersionControl │  │
│  │ └── Common UI elements...                                │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                         API Gateway                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Kong / AWS API Gateway                                    │  │
│  │ ├── Authentication  ├── Rate Limiting  ├── API Versioning│  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      Backend Services                            │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐     │
│  │  Analysis   │  │ Compliance  │  │    Intelligence    │     │
│  │  Engine     │  │   Engine    │  │      Service       │     │
│  │ ├─STPA-Sec  │  │ ├─PCI-DSS   │  │ ├─CVE Feed        │     │
│  │ ├─MAESTRO   │  │ ├─FedRAMP   │  │ ├─Threat Intel    │     │
│  │ ├─LINDDUN   │  │ ├─HIPAA     │  │ ├─MITRE ATT&CK    │     │
│  │ └─HAZOP     │  │ └─GDPR      │  │ └─Exploit DB      │     │
│  └─────────────┘  └─────────────┘  └────────────────────┘     │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐     │
│  │  Wargaming  │  │   Report    │  │   Notification     │     │
│  │   Engine    │  │  Generator  │  │     Service        │     │
│  └─────────────┘  └─────────────┘  └────────────────────┘     │
├─────────────────────────────────────────────────────────────────┤
│                      Data Layer                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL (Primary Database)                │  │
│  │  ├── Core Schema    ├── Compliance    ├── CVE Database   │  │
│  │  ├── Audit Logs     ├── Versions      └── Analytics      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Redis (Cache & Queue)                        │  │
│  │  ├── Session Cache  ├── Analysis Queue ├── Results Cache │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              S3 / Object Storage                          │  │
│  │  ├── Reports       ├── Evidence       ├── Backups        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Reuse Strategy

### Shared UI Components Package

Create a separate package `@security-platform/ui-components`:

```typescript
// packages/ui-components/src/index.ts
export { AnalysisTable } from './components/AnalysisTable';
export { AnalysisHeatMap } from './components/AnalysisHeatMap';
export { FlowDiagram } from './components/FlowDiagram';
export { RiskMatrix } from './components/RiskMatrix';
export { VersionSelector } from './components/VersionSelector';
export { ChatPanel } from './components/ChatPanel';

// Hooks
export { useAnalysisWebSocket } from './hooks/useAnalysisWebSocket';
export { useVersionControl } from './hooks/useVersionControl';

// Types
export type { Analysis, Entity, Relationship, Scenario } from './types';
```

### Shared Backend Services

Create a shared services package `@security-platform/core-services`:

```python
# packages/core-services/src/analysis_base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AnalysisFramework(ABC):
    """Base class for all analysis frameworks"""
    
    @abstractmethod
    async def analyze(self, system_model: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analysis on system model"""
        pass
    
    @abstractmethod
    def get_requirements(self) -> List[str]:
        """Get required inputs for this analysis"""
        pass

class STAPSecAnalysis(AnalysisFramework):
    """STPA-Sec implementation"""
    
    async def analyze(self, system_model: Dict[str, Any]) -> Dict[str, Any]:
        # Reuse existing STPA-Sec logic
        pass

# packages/core-services/src/compliance_base.py
class ComplianceFramework(ABC):
    """Base class for compliance frameworks"""
    
    @abstractmethod
    async def assess(self, evidence: Dict[str, Any]) -> ComplianceReport:
        pass
    
    @abstractmethod
    def get_requirements(self) -> List[ComplianceRequirement]:
        pass
```

## STPA-Sec+ Specific Features

### 1. Analysis Workbench

Enhanced UI specifically for STPA-Sec+ methodology:

```typescript
// apps/stpa-sec-plus/src/features/workbench/AnalysisWorkbench.tsx
import { 
  AnalysisTable, 
  FlowDiagram, 
  useAnalysisWebSocket 
} from '@security-platform/ui-components';

export function AnalysisWorkbench() {
  // STPA-Sec+ specific workflow
  const [currentStep, setCurrentStep] = useState<STAPSecStep>('system-definition');
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>('guided');
  
  return (
    <div className="stpa-workbench">
      <WorkflowStepper 
        steps={STPA_SEC_PLUS_STEPS}
        current={currentStep}
        onStepChange={setCurrentStep}
      />
      
      {/* Reuse components with STPA-Sec+ specific props */}
      <FlowDiagram 
        mode="control-structure"
        showAdversaries={true}
        showPrivacyFlows={true}
        onNodeClick={handleEntityAnalysis}
      />
      
      <AnalysisPanel 
        frameworks={['stpa-sec', 'maestro', 'linddun', 'hazop']}
        integratedMode={true}
      />
    </div>
  );
}
```

### 2. CVE Intelligence Dashboard

```typescript
// apps/stpa-sec-plus/src/features/cve/CVEDashboard.tsx
export function CVEDashboard() {
  const { vulnerabilities, loading } = useCVEIntelligence();
  const { missionContext } = useMissionContext();
  
  return (
    <Dashboard>
      <MetricCard 
        title="Mission-Critical CVEs"
        value={vulnerabilities.filter(v => v.missionImpact === 'CRITICAL').length}
        trend={calculateTrend()}
      />
      
      <CVEExplorer 
        vulnerabilities={vulnerabilities}
        contextualScoring={true}
        groupBy="mission-impact"
      />
      
      <ExploitPrediction 
        timeHorizon="30-days"
        showMitigationROI={true}
      />
    </Dashboard>
  );
}
```

### 3. Compliance Command Center

```typescript
// apps/stpa-sec-plus/src/features/compliance/ComplianceCenter.tsx
export function ComplianceCommandCenter() {
  const frameworks = useComplianceFrameworks();
  const gaps = useComplianceGaps();
  
  return (
    <div className="compliance-center">
      <FrameworkSelector 
        frameworks={['PCI-DSS', 'FedRAMP', 'HIPAA', 'GDPR']}
        multi={true}
      />
      
      <ComplianceHeatMap 
        frameworks={frameworks}
        showFinancialImpact={true}
        drillDown="requirement-level"
      />
      
      <GapAnalysis 
        gaps={gaps}
        showRemediationCost={true}
        priorityMode="roi"
      />
      
      <EvidenceCollector 
        automated={true}
        continuous={true}
      />
    </div>
  );
}
```

### 4. Executive Dashboard

```typescript
// apps/stpa-sec-plus/src/features/executive/ExecutiveDashboard.tsx
export function ExecutiveDashboard() {
  return (
    <Dashboard variant="executive">
      <RiskPosture 
        showTrends={true}
        compareToIndustry={true}
      />
      
      <ComplianceStatus 
        showCertificationReadiness={true}
        financialExposure={true}
      />
      
      <InvestmentROI 
        mitigations={topMitigations}
        showPaybackPeriod={true}
      />
      
      <ThreatLandscape 
        relevant={true}
        emerging={true}
        showBusinessImpact={true}
      />
    </Dashboard>
  );
}
```

## Database Architecture

### Multi-tenancy Support

```sql
-- Tenant isolation
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR NOT NULL,
  subscription_tier VARCHAR CHECK (subscription_tier IN ('starter', 'professional', 'enterprise')),
  settings JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Row-level security
ALTER TABLE system_definition ADD COLUMN tenant_id UUID REFERENCES tenants(id);
CREATE POLICY tenant_isolation ON system_definition
  FOR ALL USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

### Performance Optimization

```sql
-- Materialized views for dashboards
CREATE MATERIALIZED VIEW executive_risk_summary AS
WITH risk_metrics AS (
  -- Complex aggregation query
)
SELECT * FROM risk_metrics;

-- Refresh strategy
CREATE OR REPLACE FUNCTION refresh_executive_views() RETURNS VOID AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY executive_risk_summary;
  REFRESH MATERIALIZED VIEW CONCURRENTLY compliance_posture;
  REFRESH MATERIALIZED VIEW CONCURRENTLY cve_mission_impact;
END;
$$ LANGUAGE plpgsql;
```

## API Design

### RESTful API Structure

```yaml
/api/v1/stpa-sec-plus:
  /projects:
    GET: List projects
    POST: Create project
    /{id}:
      GET: Get project details
      PUT: Update project
      DELETE: Delete project
      
  /analyses:
    POST: Start new analysis
    /{id}:
      GET: Get analysis results
      /ucas: GET unsafe control actions
      /scenarios: GET/POST scenarios
      /mitigations: GET/POST mitigations
      
  /compliance:
    /frameworks:
      GET: List available frameworks
    /assessments:
      POST: Run assessment
      /{id}:
        GET: Get assessment results
        /evidence: GET/POST evidence
        /gaps: GET compliance gaps
        
  /cve:
    /search: GET search CVEs
    /contextual-risk: POST calculate risk
    /affected-entities: GET affected entities
    
  /intelligence:
    /threats: GET threat landscape
    /advisories: GET security advisories
    /trends: GET threat trends
```

### GraphQL Alternative

```graphql
type Query {
  project(id: ID!): Project
  analysis(id: ID!): Analysis
  compliancePosture(frameworkId: ID!): ComplianceAssessment
  missionCriticalCVEs(limit: Int): [CVE!]!
  executiveDashboard(timeRange: TimeRange!): ExecutiveMetrics
}

type Mutation {
  createProject(input: ProjectInput!): Project!
  startAnalysis(projectId: ID!, frameworks: [Framework!]!): Analysis!
  assessCompliance(frameworkId: ID!): ComplianceAssessment!
  createMitigation(scenarioId: ID!, input: MitigationInput!): Mitigation!
}

type Subscription {
  analysisProgress(analysisId: ID!): AnalysisProgress!
  complianceAlerts(severity: Severity): ComplianceAlert!
  cveAlerts(missionCritical: Boolean): CVEAlert!
}
```

## Deployment Architecture

### Kubernetes Deployment

```yaml
# k8s/stpa-sec-plus/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stpa-sec-plus-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: stpa-sec-plus-api
  template:
    metadata:
      labels:
        app: stpa-sec-plus-api
    spec:
      containers:
      - name: api
        image: stpa-sec-plus/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: stpa-db-secret
              key: url
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: stpa-sec-plus-api
spec:
  selector:
    app: stpa-sec-plus-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Auto-scaling Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: stpa-sec-plus-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: stpa-sec-plus-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Security Architecture

### Authentication & Authorization

```python
# Backend RBAC implementation
from enum import Enum
from typing import List

class Permission(Enum):
    # Analysis permissions
    ANALYSIS_READ = "analysis:read"
    ANALYSIS_WRITE = "analysis:write"
    ANALYSIS_DELETE = "analysis:delete"
    
    # Compliance permissions
    COMPLIANCE_READ = "compliance:read"
    COMPLIANCE_ASSESS = "compliance:assess"
    COMPLIANCE_CERTIFY = "compliance:certify"
    
    # Executive permissions
    EXECUTIVE_DASHBOARD = "executive:dashboard"
    EXECUTIVE_REPORTS = "executive:reports"

class Role:
    ANALYST = [
        Permission.ANALYSIS_READ,
        Permission.ANALYSIS_WRITE,
        Permission.COMPLIANCE_READ
    ]
    
    COMPLIANCE_OFFICER = [
        Permission.COMPLIANCE_READ,
        Permission.COMPLIANCE_ASSESS,
        Permission.ANALYSIS_READ
    ]
    
    EXECUTIVE = [
        Permission.EXECUTIVE_DASHBOARD,
        Permission.EXECUTIVE_REPORTS,
        Permission.ANALYSIS_READ,
        Permission.COMPLIANCE_READ
    ]
    
    ADMIN = Permission  # All permissions
```

### Data Encryption

```python
# Field-level encryption for sensitive data
from cryptography.fernet import Fernet

class EncryptedField:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, value: str) -> str:
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()

# Usage in models
class SensitiveEntity(Base):
    __tablename__ = 'sensitive_entities'
    
    id = Column(String, primary_key=True)
    name = Column(String)  # Not encrypted
    critical_data = Column(EncryptedType(String, secret_key))  # Encrypted
```

## Migration Strategy

### Phase 1: Core Extraction (Week 1)
1. Extract shared components to packages
2. Set up monorepo with Turborepo/Nx
3. Create STPA-Sec+ app scaffold
4. Configure shared dependencies

### Phase 2: Feature Implementation (Weeks 2-3)
1. Implement enhanced analysis workbench
2. Add CVE integration
3. Build compliance center
4. Create executive dashboard

### Phase 3: Enterprise Features (Weeks 4-5)
1. Add multi-tenancy
2. Implement RBAC
3. Set up audit logging
4. Add API versioning

### Phase 4: Production Readiness (Week 6)
1. Performance optimization
2. Security hardening
3. Deployment automation
4. Documentation

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **State**: Zustand + React Query
- **UI**: Tailwind CSS + Radix UI
- **Charts**: Recharts + D3.js
- **Build**: Vite + Turborepo

### Backend
- **API**: FastAPI (Python)
- **Database**: PostgreSQL 15 + TimescaleDB
- **Cache**: Redis
- **Queue**: Celery + Redis
- **Search**: Elasticsearch (for CVE search)

### Infrastructure
- **Container**: Docker + Kubernetes
- **CI/CD**: GitHub Actions + ArgoCD
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack
- **Security**: Vault + OWASP ZAP

## Success Metrics

### Technical KPIs
- API response time: < 200ms (p95)
- Analysis completion: < 5 minutes (medium system)
- Uptime: 99.9% SLA
- Concurrent users: 1000+

### Business KPIs
- Time to compliance: 50% reduction
- CVE prioritization accuracy: 85%+
- Customer onboarding: < 1 day
- ROI demonstration: < 30 days

## Summary

The STPA-Sec+ standalone architecture provides:

1. **Maximum code reuse** through shared component libraries
2. **Enterprise-grade features** from day one
3. **Scalable architecture** supporting 1000+ concurrent users
4. **Extensible framework** for adding new analysis methods
5. **Clear migration path** from prototype to production

This architecture positions STPA-Sec+ as a best-in-class enterprise security analysis platform while maintaining development velocity through strategic code reuse.