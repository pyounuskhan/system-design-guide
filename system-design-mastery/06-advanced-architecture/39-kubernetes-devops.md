# A7. Kubernetes & DevOps

## Part Context
**Part:** Part 6 - Advanced Architecture
**Position:** Chapter A7 (Advanced Architecture — Kubernetes & DevOps Primer)
**Complements:** F11: Deployment & DevOps (deep chapter) covers CI/CD pipelines, supply-chain security, progressive delivery, and release safety in production depth. This chapter provides the conceptual primer for the Advanced Architecture sequence.
**Why this part exists:** This section focuses on how systems are actually deployed, operated, and evolved after the architecture diagram is approved.
**This chapter builds toward:** container orchestration, deployment safety, platform thinking, and operational delivery discipline

## Overview
Kubernetes and modern DevOps practices sit at the boundary between application architecture and platform operations. They determine how services are packaged, deployed, discovered, scaled, configured, rolled back, and observed. For many teams, architecture decisions only become real when they survive these delivery mechanics.

This chapter does not treat Kubernetes as a set of YAML objects to memorize. Instead, it frames Kubernetes as a control plane for running distributed systems and DevOps as the discipline of turning code changes into safe, observable production changes.

## Why This Matters in Real Systems
- A strong design is still fragile if it cannot be deployed and rolled back safely.
- Kubernetes concepts such as pods, services, and autoscaling shape how microservices behave in production.
- DevOps practices determine release safety, operational speed, and incident recoverability.
- Interviewers increasingly expect candidates to understand how application design interacts with platform constraints.

## Core Concepts
### Containers and pods
Containers package application code with runtime dependencies. Kubernetes schedules one or more related containers together in a pod, which becomes the basic deployable unit. Architects need to understand this because resource sizing, failure domains, and sidecar patterns all operate at pod level.

### Services, ingress, and service discovery
Pods are ephemeral, so clients should not address them directly. Kubernetes Services provide stable virtual endpoints, while ingress or gateway layers expose traffic into the cluster. This abstraction changes how internal networking and load balancing are designed.

### Deployment strategies
Rolling updates, blue-green deployments, and canary releases all balance speed and risk differently. Platform choices should reflect the blast radius of failure, database compatibility, and whether traffic can be mirrored or segmented.

### Autoscaling and resource management
Horizontal Pod Autoscalers, cluster autoscaling, and resource requests or limits affect both performance and cost. Under-sizing causes throttling and instability. Over-sizing wastes money and can hide poor application behavior.

### CI/CD and platform workflows
DevOps is broader than deployment. It includes build reproducibility, automated testing, artifact promotion, infrastructure as code, secrets management, and release observability. Kubernetes is only one part of the delivery system.

## Key Terminology
| Term | Definition |
| --- | --- |
| Pod | The smallest deployable unit in Kubernetes, containing one or more containers. |
| Deployment | A controller that manages rolling updates and desired replica counts for pods. |
| Service | A stable network abstraction that routes traffic to matching pods. |
| Ingress | A layer that routes external HTTP(S) traffic into services inside the cluster. |
| HPA | Horizontal Pod Autoscaler, which adjusts replica counts based on metrics. |
| Rolling Update | A deployment approach that gradually replaces old instances with new ones. |
| Blue-Green | A release strategy with two full environments, switching traffic from old to new. |
| GitOps | An operational model where declarative infrastructure and deployment state are managed through version control. |

## Detailed Explanation
### Think in workloads, not just manifests
Kubernetes resources are useful only when tied to workload behavior. A stateless API service, a queue worker, and a stateful database replica have different lifecycle, scaling, and recovery needs. Architects should classify workloads first, then choose the right platform primitives.

### Use deployment strategies to reduce blast radius
A rolling update is often enough for backward-compatible stateless services. High-risk changes may justify canary rollout with real traffic observation. Critical products may prefer blue-green deployments so rollback is mostly a routing decision. The point is not to memorize the names, but to connect release mechanics to business risk.

### Pair autoscaling with good application behavior
Autoscaling works best when applications expose meaningful metrics and tolerate replica churn. If startup is slow, connection pools are fragile, or caches cold-start badly, scaling alone will not save the service. Platform and application design must fit together.

### Platform abstractions should remove repetitive toil
DevOps maturity often shows up as paved roads: standard base images, consistent health probes, shared observability, reusable CI pipelines, secret rotation, and policy enforcement. Architects should value these because they compress delivery risk across many teams.

### Kubernetes is not the architecture by itself
Running a monolith on Kubernetes does not make it cloud-native, and running microservices there does not guarantee resilience. Kubernetes is an execution environment. The underlying service boundaries, data consistency models, and failure-handling logic still matter more than the container platform alone.

## Diagram / Flow Representation
### Cluster-Level Architecture
```mermaid
flowchart LR
    User --> Ingress[Ingress / API Gateway]
    Ingress --> ServiceA[Service A]
    Ingress --> ServiceB[Service B]
    ServiceA --> SvcA[(Kubernetes Service)]
    ServiceB --> SvcB[(Kubernetes Service)]
    SvcA --> PodsA[Pods]
    SvcB --> PodsB[Pods]
    PodsA --> Metrics[Metrics / Logs]
    PodsB --> Metrics
```

### Progressive Delivery Flow
```mermaid
flowchart TD
    Commit[Code Commit] --> CI[Build + Test Pipeline]
    CI --> Registry[Container Registry]
    Registry --> Deploy[Deploy to Cluster]
    Deploy --> Canary[Canary / Rolling Release]
    Canary --> Observe[Observe Metrics + Traces]
    Observe -->|healthy| Promote[Promote Release]
    Observe -->|unhealthy| Rollback[Rollback]
```

## Real-World Examples
- Many cloud-native teams use Kubernetes to standardize service deployment, networking, and scaling across many applications.
- Platform teams often pair Kubernetes with Prometheus, Grafana, ingress controllers, service meshes, and GitOps tooling to build an internal developer platform.
- Netflix-scale organizations use a variety of platform abstractions, but the underlying concerns of safe rollout, autoscaling, and observability are universal even when the tooling differs.
- Smaller teams may use managed Kubernetes or simpler container platforms while still applying the same deployment and reliability principles.

## Case Study
### Deploying an e-commerce service on Kubernetes
Assume a retail platform has a checkout API, an inventory service, a background worker, and a notification service. Traffic spikes sharply during sales events, and releases must be safe because checkout failures are revenue-impacting.

### Requirements
- Package services consistently and deploy them repeatably across environments.
- Scale API and worker components independently based on traffic and backlog.
- Route external traffic safely and expose service-to-service discovery internally.
- Perform low-risk rollouts with monitoring and fast rollback.
- Manage configuration, secrets, and observability in a standardized way.

### Design Evolution
- A first stage may containerize services and deploy them with simple rolling updates.
- A later stage adds health probes, autoscaling, ingress routing, and centralized observability.
- As release risk grows, canary or blue-green workflows and automated analysis become necessary.
- As the platform matures, GitOps, policy enforcement, and reusable templates reduce variance across teams.

### Scaling Challenges
- Pods are ephemeral, so application startup and readiness behavior matter more than in long-lived VM environments.
- Resource requests and limits are difficult to tune and can create both cost waste and instability.
- Database migrations and backward compatibility can become the real deployment bottleneck.
- Without platform standards, teams recreate pipelines, logging, and security controls inconsistently.

### Final Architecture
- Services run as deployments with tuned resource requests, readiness probes, and horizontal scaling policies.
- Ingress or gateway layers route public traffic while internal service discovery uses cluster-native abstractions.
- CI/CD builds signed images, promotes artifacts, and performs progressive deployments with observability checks.
- Configuration and secrets are managed declaratively with clear environment separation.
- The platform exposes metrics, logs, and release markers so operators can judge rollout safety quickly.

## Architect's Mindset
- Connect workload behavior to platform primitives instead of using one deployment pattern for everything.
- Choose rollout strategies according to blast radius, reversibility, and user impact.
- Treat platform standards as leverage: they make many teams safer at once.
- Pair autoscaling with application design that tolerates churn and cold starts.
- Remember that Kubernetes solves deployment mechanics, not poor service boundaries or weak reliability design.

## Reference Platform Blueprint

A Kubernetes-based internal developer platform (IDP) should provide standardized capabilities that remove repeated toil across all teams. Here is the minimum viable platform.

### Platform Component Map

```
┌────────────────────────────────────────────────────────┐
│  Developer Experience Layer                             │
│  • Service templates (cookiecutter / Backstage)         │
│  • Developer portal (Backstage catalog)                 │
│  • Self-service namespace + resource provisioning        │
└──────────────────────┬─────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────┐
│  CI/CD Layer                                            │
│  • Build: GitHub Actions / GitLab CI                    │
│  • Scan: Trivy (images), Semgrep (SAST), Grype (SCA)   │
│  • Sign: cosign (keyless via OIDC)                      │
│  • Deploy: Argo CD (GitOps reconciliation)              │
└──────────────────────┬─────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────┐
│  Runtime Layer (Kubernetes)                              │
│  • Ingress: Nginx / Envoy Gateway                       │
│  • Service mesh: Istio / Linkerd (mTLS, retries)        │
│  • Autoscaling: HPA (CPU/custom metrics), Cluster AS    │
│  • Secrets: External Secrets Operator + Vault            │
│  • Policy: Kyverno / OPA Gatekeeper                     │
└──────────────────────┬─────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────┐
│  Observability Layer                                     │
│  • Metrics: Prometheus + Grafana                         │
│  • Logs: Loki (or ELK)                                   │
│  • Traces: Tempo / Jaeger (via OTel Collector)           │
│  • Alerting: Alertmanager → PagerDuty                    │
└────────────────────────────────────────────────────────┘
```

### Platform Maturity Levels

| Level | What You Have | Impact |
|-------|-------------|--------|
| **L0: Manual** | kubectl apply, manual image builds, no CI | High risk, slow, inconsistent |
| **L1: Automated CI/CD** | Automated build + test + deploy per service | Consistent builds, faster delivery |
| **L2: GitOps + Observability** | Argo CD reconciliation, Prometheus + Grafana, structured logging | Auditable deploys, production visibility |
| **L3: Self-Service Platform** | Service templates, developer portal, policy enforcement, secret rotation | Teams onboard fast, platform absorbs complexity |
| **L4: Full IDP** | Cost attribution, multi-cluster governance, progressive delivery, chaos testing | Engineering efficiency at scale |

---

## Infrastructure as Code (IaC) and GitOps — Concrete Examples

### IaC: Terraform for Cloud Resources

```hcl
# Terraform: provision an RDS database for a service
resource "aws_db_instance" "orders_db" {
  identifier           = "orders-db-prod"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.r6g.xlarge"
  allocated_storage    = 100
  storage_encrypted    = true
  multi_az             = true     # HA across availability zones
  backup_retention_period = 14    # 14-day point-in-time recovery

  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.private.name

  tags = {
    Team        = "orders"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
```

**IaC principles:**
- All infrastructure defined in code, versioned in Git
- Changes go through PR review (same as application code)
- `terraform plan` shows diff before `terraform apply`
- State stored remotely (S3 + DynamoDB lock) — never local

### GitOps: Argo CD Application

```yaml
# Argo CD Application: deploy orders-service from Git
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: orders-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/k8s-config
    path: environments/production/orders-service
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: orders
  syncPolicy:
    automated:
      prune: true        # Remove resources deleted from Git
      selfHeal: true     # Revert manual kubectl changes
    syncOptions:
      - CreateNamespace=true
```

**GitOps principles:**
- Git is the single source of truth for cluster state
- No manual `kubectl apply` in production — ever
- Argo CD continuously reconciles desired (Git) vs actual (cluster)
- Rollback = `git revert` → Argo CD auto-syncs

---

## Supply-Chain Security and Policy-as-Code

### Supply-Chain Security in the Platform

| Control | How It Works | Tool |
|---------|-------------|------|
| **SBOM generation** | Every build produces a Software Bill of Materials | Syft, Trivy |
| **Image signing** | Every image is cryptographically signed | cosign (Sigstore, keyless via OIDC) |
| **Admission enforcement** | Cluster rejects unsigned or unscanned images | Kyverno, OPA Gatekeeper |
| **Vulnerability scanning** | Block images with critical CVEs from deploying | Trivy (in CI) + Kyverno (at admission) |
| **SLSA provenance** | Build metadata proves image was built by trusted CI | SLSA GitHub Actions generator |

### Policy-as-Code Examples

```yaml
# Kyverno: require all pods to have resource limits
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resource-limits
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-limits
      match:
        any:
          - resources:
              kinds: ["Pod"]
      validate:
        message: "All containers must have CPU and memory limits set."
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    memory: "?*"
                    cpu: "?*"
```

```yaml
# Kyverno: only allow images from trusted registry
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-image-registries
spec:
  validationFailureAction: Enforce
  rules:
    - name: validate-registries
      match:
        any:
          - resources:
              kinds: ["Pod"]
      validate:
        message: "Images must come from myregistry.io"
        pattern:
          spec:
            containers:
              - image: "myregistry.io/*"
```

### Multi-Cluster Governance

| Concern | Single Cluster | Multi-Cluster |
|---------|---------------|---------------|
| Policy enforcement | Kyverno/OPA per cluster | Centralized policy repo deployed to all clusters via GitOps |
| Secret management | External Secrets Operator per cluster | Vault with per-cluster auth paths |
| Observability | Local Prometheus + Grafana | Centralized Grafana with remote-write from each cluster (Mimir/Thanos) |
| Cost attribution | Namespace-level labels | Cluster + namespace labels; per-cluster cost reports |
| Deployment | Argo CD per cluster | Argo CD with multi-cluster targeting (ApplicationSet) |

### Cross-References to Deep Content

| Topic | Where to Go |
|-------|-------------|
| Full CI/CD pipeline with supply-chain security | F11: Deployment & DevOps §1.5 (Supply-Chain Security) |
| Progressive delivery (Flagger, Argo Rollouts) | F11: Progressive Delivery |
| Release safety checklists by risk level | F11: Release Safety Checklists |
| Container image best practices (multi-stage, non-root) | F11 §3.1 (Docker Fundamentals) |
| Helm chart management | F11 §3.4 (Helm) |
| Service mesh deep dive (Istio vs Linkerd) | F11 §3.5 (Service Mesh) |

## Common Mistakes
- Treating Kubernetes as a goal instead of an execution environment.
- Using default resource settings without measuring real workload needs.
- Ignoring readiness, liveness, and startup behaviors.
- Rolling out incompatible application and database changes together without a safety plan.
- Building bespoke pipelines for every team instead of reusable platform patterns.

## Interview Angle
- Interviewers may ask how a designed system is deployed, scaled, and rolled back in production.
- Strong answers discuss stateless versus stateful workloads, autoscaling, rollout strategy, and observability.
- Candidates stand out when they connect Kubernetes primitives to system behavior instead of listing objects mechanically.
- Weak answers use Kubernetes buzzwords without explaining how releases remain safe.

## Quick Recap
- Kubernetes provides runtime control over deployment, networking, and scaling, but it does not replace architecture.
- Pods, services, ingress, and autoscaling shape how microservices run in production.
- DevOps practices turn code changes into safe, observable releases.
- Platform standards reduce repeated toil and lower operational variance.
- Release strategy should always reflect business risk and reversibility.

## Practice Questions
1. Why are pods considered the basic scheduling unit in Kubernetes?
2. How does a Service differ from an Ingress?
3. When would you prefer canary deployment over rolling update?
4. Why can autoscaling fail even when the cluster has free capacity?
5. How should a background worker scale differently from a stateless API?
6. What platform capabilities are worth standardizing across teams?
7. How do database migrations complicate containerized deployments?
8. Why do readiness probes matter for release safety?
9. How would you reduce deployment risk for a revenue-critical service?
10. What does GitOps change in a team’s delivery model?

## Further Exploration
- Study service meshes, policy engines, and internal developer platforms for the next layer of platform maturity.
- Connect this chapter with observability and cost optimization, since deployment choices affect both.
- Practice mapping earlier system designs onto concrete runtime and release workflows.





## Navigation
- Previous: [Observability](38-observability.md)
- Next: [Security & Authentication](40-security-authentication.md)
