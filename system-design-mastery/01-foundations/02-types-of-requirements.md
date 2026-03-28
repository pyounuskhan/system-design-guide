# 2. Types of Requirements

## Part Context
**Part:** Part 1 - Foundations of System Design  
**Position:** Chapter 2 of 60
**Why this part exists:** This opening section gives the reader the language, framing, and mental models needed to reason about systems before choosing technologies.  
**This chapter builds toward:** capacity planning, component selection, interview framing, and clearer design reviews

## Overview
Requirements are the input to design. Before choosing a database, a queue, or a service boundary, you need to know what the system must do and what qualities it must preserve while doing it. In practice, bad requirements lead to bad architecture faster than bad technology choices do.

The two big categories are functional requirements and non-functional requirements. Functional requirements describe behavior: what features the system must provide. Non-functional requirements describe qualities such as performance, availability, consistency, reliability, security, and cost. A system can satisfy every feature request and still fail because the non-functional requirements were ignored.

## Why This Matters in Real Systems
- Requirements determine which trade-offs matter and which ones are irrelevant noise.
- They prevent architects from solving the wrong problem with the right technology.
- They help teams prioritize what must be correct, what must be fast, what can be delayed, and what can be simplified.
- They are one of the first things interviewers test, because poor requirement framing leads to weak design from the start.

## Core Concepts
### Functional requirements
These describe business behavior, user actions, and visible capabilities such as sending messages, processing orders, or searching products.

### Non-functional requirements
These define quality targets such as latency, throughput, consistency, reliability, privacy, observability, compliance, and total cost of operation.

### Constraints, assumptions, and exclusions
A good design conversation includes limits. Budget, team maturity, release deadline, region restrictions, and existing systems all shape the solution.

### Prioritization and measurable targets
Requirements become architecturally useful when they are ranked and made measurable. “Fast” is vague. “p95 under 200 ms for reads” is actionable.

## Key Terminology
| Term | Definition |
| --- | --- |
| Functional Requirement | A statement of what the system should do from a business or user perspective. |
| Non-Functional Requirement | A statement of how well the system must behave under real operating conditions. |
| Latency | The time required for a request or workflow to complete. |
| Throughput | The volume of work a system can process over time. |
| Availability | The percentage of time the system is operational and reachable. |
| Durability | The confidence that accepted data will not be lost. |
| Consistency | The degree to which different readers see the same view of data. |
| Constraint | A limitation or condition that narrows the valid design space. |

## Detailed Explanation
### Start with the job the system must do
Functional requirements describe the job to be done. They are often the easiest part for teams to talk about because they map directly to features. But good architecture requires digging deeper: who performs the action, how often, under what load, with which failure tolerance, and with what business consequence if it goes wrong?

### Non-functional requirements are often the true architecture drivers
The sentence “users can send messages” is not what decides whether you need WebSockets, durable queues, regional replicas, or strong encryption. The deciding factors are latency tolerance, delivery guarantees, ordering requirements, privacy expectations, and mobile battery constraints. In other words, non-functional requirements often shape the architecture more than the feature sentence does.

### Requirements often conflict
A team may ask for the system to be globally low-latency, strongly consistent, very cheap, and easy to evolve. Those goals do not always align. Architects therefore need to identify which requirements are hard constraints and which are preferences. For example, a banking system may prioritize correctness and auditability above all else, while a social media system may prioritize responsiveness and scale over perfectly synchronized counters.

### Measurable requirements improve design quality
Architecture gets stronger when fuzzy goals are translated into targets. Instead of “the app should be fast,” ask for p95 latency goals, expected peak QPS, recovery-time objectives, acceptable data loss windows, retention requirements, or per-user cost targets. These numbers make trade-offs discussable and make estimates possible in the next chapter.

### Edge cases reveal missing requirements
Some of the most important requirements appear only when you ask uncomfortable questions. Should messages be delivered while the user is offline? What happens when a payment provider times out? Can admins override user data? How long must audit logs be kept? What happens during a regional outage? These are not nice-to-have questions; they define the architecture.

### SLOs and SLAs are requirements, not metrics
Service Level Objectives (SLOs) and Service Level Agreements (SLAs) are often discussed in the observability chapter, but they belong here too — because they are *requirements* that constrain the design. An SLO is a measurable reliability target. An SLA is a contractual promise with financial consequences. Both must be defined during requirements gathering, not after the system is built.

**SLO examples by system type:**

| System | SLI (What You Measure) | SLO (Target) | Why It Shapes Architecture |
|--------|----------------------|-------------|---------------------------|
| E-commerce checkout | % of requests returning 2xx within 500ms | 99.95% availability | Requires multi-AZ deployment, circuit breakers on payment provider, async order confirmation |
| Chat messaging | % of messages delivered within 2 seconds | 99.9% delivery within SLA | Requires persistent queues, retry logic, delivery acknowledgment protocol |
| Search API | p99 latency of search queries | < 200ms at p99 | Requires in-memory index, CDN for static results, pre-computed ranking |
| Batch data pipeline | % of jobs completing before deadline | 99.5% on-time completion | Requires capacity headroom, job-level monitoring, automatic retry |
| File storage | Proportion of objects retrievable after write | 99.999999999% durability (11 nines) | Requires cross-region replication, erasure coding, checksum verification |

**How to derive SLOs during requirements gathering:**

1. Ask: "What happens if this feature is down for 5 minutes? 30 minutes? 4 hours?" — the answer reveals the acceptable downtime.
2. Ask: "Which user action must never lose data?" — the answer reveals durability requirements.
3. Ask: "What response time makes users abandon the workflow?" — the answer reveals latency SLOs.
4. Convert answers to numbers: "99.9% availability = 43 minutes downtime per month."

### Requirements often conflict — resolution patterns

When requirements conflict (and they will), architects must identify which requirement yields and document why. Here are common conflicts with resolution patterns:

| Conflict | Example | Resolution Pattern |
|----------|---------|-------------------|
| **Consistency vs. Latency** | Banking: account balance must be correct, but users expect instant transfers | Use strong consistency for balance reads; use async processing for transfer execution with optimistic UI ("transfer pending") |
| **Cost vs. Availability** | Startup cannot afford multi-region deployment but needs high uptime | Single region with multi-AZ; accept regional outage risk; document as explicit trade-off for investors |
| **Security vs. Usability** | Healthcare portal requires MFA but doctors need instant access during emergencies | Tiered auth: MFA for sensitive data, session-based for read-only views, break-glass override with audit logging |
| **Freshness vs. Performance** | Dashboard needs real-time data but queries are slow on live tables | Pre-aggregate into materialized views with 1-minute refresh; label UI as "data as of 1 min ago" |
| **Privacy vs. Analytics** | Marketing wants user behavior data but GDPR limits data collection | Anonymize/aggregate at collection time; separate PII store from analytics store; consent-gated collection |
| **Simplicity vs. Scalability** | Team of 3 engineers cannot maintain a microservices architecture | Start as a modular monolith; extract services only when a specific module needs independent scaling |

**Resolution principle:** When two requirements conflict, ask "which one has a higher cost of failure?" The requirement whose violation causes greater business damage (revenue loss, legal penalty, user churn) wins.

### Regulatory, compliance, and privacy requirements

In regulated industries (finance, healthcare, government, education), compliance requirements are not optional extras — they are hard constraints that override performance and convenience preferences. Treat them as first-class requirements.

**Regulatory requirements template:**

| Category | Questions to Ask | Example Requirements |
|----------|-----------------|---------------------|
| **Data Residency** | Where must data be stored? Can it cross borders? | "EU user data must remain in EU regions" (GDPR) |
| **Data Retention** | How long must data be kept? When must it be deleted? | "Financial records retained 7 years" (SOX); "User data deleted within 30 days of account closure" (GDPR) |
| **Audit Logging** | What actions must be logged? Who can access logs? | "All admin actions logged with immutable audit trail" (SOC 2) |
| **Access Control** | Who can see what data? How is access authenticated? | "PHI accessible only to treating providers" (HIPAA); "Separation of duties for financial approvals" |
| **Encryption** | Must data be encrypted at rest? In transit? With what standard? | "AES-256 at rest, TLS 1.3 in transit" (PCI-DSS for cardholder data) |
| **Consent** | Is user consent required before data collection? Can users opt out? | "Explicit consent before tracking; honor Do Not Track" (CCPA/GDPR) |
| **Breach Notification** | What happens if data is compromised? | "Notify affected users within 72 hours" (GDPR) |

**Privacy-by-design checklist** — verify during requirements gathering:

- [ ] PII fields identified in the data model (name, email, phone, IP, device ID)
- [ ] Data minimization applied (collect only what is needed)
- [ ] Retention policy defined for each data category
- [ ] Deletion/anonymization mechanism specified for account closure
- [ ] Consent flow designed for data collection
- [ ] Cross-border data transfer reviewed (standard contractual clauses if needed)
- [ ] Encryption requirements specified for PII at rest and in transit

### Anti-requirements: what the system explicitly will NOT do

Anti-requirements (explicit exclusions) are as important as requirements themselves. They prevent scope creep, set clear expectations, and save engineering effort. Every design should include a "Not in Scope" section.

**Why anti-requirements matter:**

| Without Anti-Requirements | With Anti-Requirements |
|--------------------------|----------------------|
| Stakeholders assume every feature is planned | Clear boundaries on what v1 delivers |
| Engineers build for imagined future requirements | Engineers optimize for confirmed requirements |
| Design reviews debate features that were never committed | Reviews focus on committed scope |
| Cost and timeline estimates are unreliable | Estimates are scoped to actual deliverables |

**How to write anti-requirements:**

Use this format: "The system will **not** [capability] in this version because [reason]. This is planned for [never / v2 / if demand warrants]."

**Examples:**

- "The system will **not** support real-time collaborative editing in v1 because the user base is single-editor per document. Planned for v2 if usage patterns confirm demand."
- "The system will **not** handle multi-currency transactions because the product launches in a single market. Will revisit for international expansion."
- "The system will **not** provide sub-second search because the corpus is < 100K documents and a simple database query with index meets latency targets."
- "The system will **not** guarantee exactly-once delivery because the messaging protocol supports at-least-once with idempotent consumers, which is sufficient."

## Diagram / Flow Representation
### Requirement Funnel
```mermaid
flowchart TD
    Business[Business goal] --> Users[User journeys]
    Users --> FR[Functional requirements]
    Users --> NFR[Non-functional requirements]
    NFR --> Constraints[Constraints and trade-offs]
    FR --> Design[Architecture decisions]
    Constraints --> Design
```

### Clarification Flow in a Design Interview
```mermaid
sequenceDiagram
    participant I as Interviewer
    participant C as Candidate
    I->>C: Design a messaging system
    C->>I: Clarify users, scale, delivery guarantees
    I-->>C: Gives functional + non-functional context
    C->>C: Prioritize requirements
    C->>I: Propose architecture based on priorities
```

## Real-World Examples
- WhatsApp requires messaging, group chat, and media sharing as functional needs, but low latency, privacy, and offline delivery are the deeper architecture drivers.
- Amazon checkout requires adding items, placing orders, and processing payments, but consistency, fraud protection, and auditability dominate the system design.
- Netflix home page requirements include listing content and playing video, but personalized recommendations, regional delivery speed, and cost-efficient streaming define the actual architecture.
- Google Drive needs file storage and sharing features, but collaboration latency, version history, permission models, and storage durability shape the system far more deeply.

## Case Study
### WhatsApp requirements breakdown

WhatsApp is a good requirement-analysis exercise because the visible feature set sounds simple, but the real system is driven by latency, reliability, privacy, and mobile constraints.

### Requirements
- Users can send one-to-one messages, group messages, images, videos, and documents.
- Users can see delivery acknowledgments, read receipts, and basic presence information.
- Messages should work across unreliable mobile networks and across temporary disconnects.
- Chat history should remain durable enough that users do not lose accepted messages.
- Security expectations are high: privacy, access control, and encrypted transport are non-negotiable.

### Design Evolution
- An early version may support one-to-one messaging with a simple store-and-forward model and limited presence signaling.
- As group messaging grows, fan-out behavior, ordering, and delivery guarantees become far more important.
- As multiple devices per user are supported, synchronization, read receipts, and conflict handling become more complex.
- As global scale grows, regional routing, queue durability, and the difference between message consistency and presence consistency become design-defining.

### Scaling Challenges
- Presence updates are frequent and ephemeral, so they should not be treated like durable messages.
- Delivery guarantees matter much more for messages than for typing indicators or “last seen” state.
- Mobile battery and bandwidth constraints make chat architecture different from desktop-first systems.
- Security features influence storage, transport, and device synchronization design.

### Final Architecture
- A durable message path backed by persistent storage and per-recipient delivery queues.
- Separate handling for ephemeral signals such as typing and presence.
- Strongly defined delivery lifecycle states such as sent, delivered, and read.
- Security controls that treat message content and metadata carefully across the request path.
- Regional infrastructure and observability tuned for latency, queue health, and message loss prevention.

## Architect's Mindset
- Translate vague business language into measurable design inputs.
- Identify the two or three non-functional requirements that dominate the architecture.
- Separate must-have requirements from preferences so the design space remains realistic.
- Document assumptions explicitly because hidden assumptions become future incidents or interview weak points.
- Use requirements to justify design choices, not to justify a preferred technology.

## Requirements Worksheet — Reusable Template

Use this worksheet at the start of every system design — whether in a design document, an architecture review, or an interview. It ensures no category of requirement is overlooked.

```markdown
# Requirements Worksheet: [System Name]

## 1. Functional Requirements (What the system does)
| # | Requirement | Priority | Notes |
|---|------------|----------|-------|
| FR-1 | | P0 / P1 / P2 | |
| FR-2 | | P0 / P1 / P2 | |
| FR-3 | | P0 / P1 / P2 | |

## 2. Non-Functional Requirements (How well it does it)
| Category | Target | Measurement |
|----------|--------|-------------|
| Availability | 99.X% | Uptime over 30-day rolling window |
| Latency (read) | p99 < Xms | End-to-end API response time |
| Latency (write) | p99 < Xms | Time to durable acknowledgment |
| Throughput | X req/sec (peak) | Sustained peak QPS |
| Durability | 99.X% | Probability of no data loss after write ack |
| Consistency | Strong / Eventual | Per data entity — specify which needs what |
| Freshness | Data visible within X seconds | Time from write to read visibility |

## 3. Constraints
| Type | Constraint | Impact on Design |
|------|-----------|-----------------|
| Budget | $X/month infrastructure | Limits vendor choices, multi-region scope |
| Team | X engineers | Limits operational complexity |
| Timeline | Launch by YYYY-MM-DD | Limits v1 scope |
| Regulatory | GDPR / HIPAA / PCI / SOX | Mandates encryption, retention, audit |
| Existing systems | Must integrate with [system] | Constrains protocol, data format choices |

## 4. Risks and Assumptions
| # | Assumption / Risk | What Happens If Wrong |
|---|-------------------|----------------------|
| A-1 | Traffic will not exceed Xk QPS in year 1 | Need to re-evaluate DB sharding earlier |
| A-2 | Users are in a single geographic region | Multi-region adds latency + cost |
| R-1 | Third-party API may have outages | Need circuit breaker + fallback |

## 5. Anti-Requirements (Explicit Exclusions)
| # | What the System Will NOT Do | Reason | Revisit When |
|---|---------------------------|--------|-------------|
| X-1 | | | Never / v2 / If demand |
| X-2 | | | Never / v2 / If demand |

## 6. SLO Definitions
| SLI | SLO Target | Error Budget (30 days) | Alerting Threshold |
|-----|-----------|----------------------|-------------------|
| Availability | 99.X% | X minutes downtime | Burn rate > 6x |
| Latency (p99) | < Xms | X% of requests over target | Burn rate > 3x |
```

**How to use this worksheet:**
1. Fill sections 1-2 during the first 5-8 minutes of a design interview or the first meeting of a design review.
2. Fill sections 3-4 to constrain the solution space before drawing any architecture.
3. Fill section 5 to prevent scope creep and set clear expectations.
4. Fill section 6 to make reliability a concrete, measurable goal.

## Common Mistakes
- Treating all requirements as equally important instead of ranking them.
- Starting architecture discussion before clarifying scale, consistency, or availability expectations.
- Failing to turn vague statements like “fast” or “secure” into actionable targets or constraints.
- Ignoring operational or legal constraints such as retention, compliance, or regional deployment rules.
- Assuming every workflow in a product needs the same consistency and latency guarantees.

## Interview Angle
- This topic is usually tested at the start of a system design interview when the interviewer gives a broad problem statement.
- Interviewers expect strong candidates to ask clarifying questions about users, usage patterns, scale, latency, consistency, and constraints before presenting a design.
- A high-quality answer explicitly distinguishes functional requirements from non-functional requirements and prioritizes them.
- If requirements conflict, explain the trade-off rather than pretending the system can maximize everything at once.

## Quick Recap
- Functional requirements describe what the system does; non-functional requirements describe how well it must do it.
- Architecture is often driven more by non-functional requirements than by feature lists alone.
- Requirements become useful when they are measurable, ranked, and bounded by constraints.
- Good architects ask clarifying questions until the real problem is clear.
- Requirement quality strongly predicts design quality.

## Practice Questions
1. How would you explain the difference between functional and non-functional requirements to a new engineer?
2. Why do non-functional requirements often influence architecture more than feature descriptions?
3. What follow-up questions would you ask before designing a food delivery platform?
4. How would you convert “the app should be fast” into measurable requirements?
5. Which WhatsApp requirements can tolerate eventual consistency and which cannot?
6. How do regulatory or compliance constraints affect design even when they are not user-facing features?
7. What problems arise when teams do not rank requirements explicitly?
8. How would you capture assumptions in a design document so they can be challenged later?
9. Why is requirement gathering one of the strongest signals in a system design interview?
10. What is an example of a feature that looks simple until non-functional requirements are considered?

## Further Exploration
- Continue to capacity planning so you can convert requirements into estimates and infrastructure choices.
- Practice requirement breakdowns for products such as ride-sharing, streaming, and document collaboration.
- As you study later chapters, trace each architecture pattern back to the requirement it solves.





## Navigation
- Previous: [What is System Design?](01-what-is-system-design.md)
- Next: [Estimation & Capacity Planning](03-estimation-capacity-planning.md)
