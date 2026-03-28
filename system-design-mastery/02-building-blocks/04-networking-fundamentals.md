# 4. Networking Fundamentals

## Part Context
**Part:** Part 2 - Core System Building Blocks  
**Position:** Chapter 4 of 60
**Why this part exists:** This section moves from framing to mechanics by explaining the infrastructure components that repeatedly appear in real-world systems.  
**This chapter builds toward:** understanding request paths, latency sources, encryption overhead, and protocol-level trade-offs in distributed systems

## Overview
Every distributed system is ultimately a networking problem disguised as an application problem. A request does not teleport from a user to a server. It moves through DNS, TCP or QUIC handshakes, TLS negotiation, proxies, routers, load balancers, and service-to-service calls. Each step adds latency, creates failure modes, and influences architecture decisions.

Networking fundamentals matter because performance complaints are often blamed on application code even when the real issue is connection setup, cross-region distance, packet loss, or inefficient protocols. Architects who understand the network path make better decisions about caching, service boundaries, regional placement, and API design.

## Why This Matters in Real Systems
- Network behavior often dominates end-user latency before business logic even begins.
- Protocol choices affect reliability, ordering, security, and resource consumption.
- System diagrams become much more realistic when request paths are understood in physical and logical terms.
- Many scaling and resilience problems are actually networking problems: timeouts, retries, handshake cost, and cross-region placement.

## Core Concepts
### HTTP and HTTPS
HTTP defines request-response semantics at the application layer. HTTPS adds TLS so requests are encrypted, authenticated, and harder to tamper with in transit.

### TCP vs UDP
TCP prioritizes reliable ordered delivery. UDP prioritizes low overhead and leaves ordering, retransmission, and congestion behavior more open to the application or higher-level protocol.

### DNS resolution
DNS translates domain names into addresses and can also steer traffic geographically or operationally.

### TLS handshake and session reuse
Secure communication requires key negotiation and certificate validation. Reused connections and session resumption reduce repeated overhead.

## Key Terminology
| Term | Definition |
| --- | --- |
| DNS | The distributed naming system that resolves human-readable domains into IP addresses or service endpoints. |
| TCP | A connection-oriented transport protocol offering reliable ordered delivery. |
| UDP | A connectionless transport protocol with low overhead and no built-in delivery guarantees. |
| TLS | The protocol used to secure communication in HTTPS and many service-to-service connections. |
| Round Trip Time | The time for a packet to travel to a destination and back. |
| Handshake | The setup exchange used to establish a connection or negotiate encryption. |
| CDN | A distributed network of edge servers used to cache and deliver content close to users. |
| Packet Loss | A condition where transmitted network packets do not successfully reach the destination. |

## Detailed Explanation
### What happens before your code runs
When a user opens a URL, the system may perform DNS resolution, establish or reuse a transport connection, negotiate TLS, pass through edge proxies or CDNs, and only then invoke application logic. If an architect ignores this path, latency targets become unrealistic and debugging becomes shallow.

### Why TCP is the default for most APIs
Most APIs and databases want reliable ordered delivery because application correctness is usually more valuable than raw packet speed. TCP handles retransmission, ordering, and congestion control, which simplifies application development. The cost is handshake overhead and some latency under loss or congestion.

### Where UDP fits
UDP is common in DNS, media transport, gaming, and protocols that need lower overhead or can tolerate occasional loss. Modern protocols such as QUIC build richer behavior on top of UDP to combine low-latency setup with features like encryption and stream control.

### TLS is a performance and security topic
TLS is often described only as a security feature, but it also affects architecture. Handshake cost, certificate management, termination points, session reuse, and internal service encryption all affect latency, CPU use, and trust boundaries.

### Network distance is architecture
A service split across regions may be elegant in a diagram and slow in reality. The speed of light, inter-region routing, and cross-zone chatter matter. Architects should place services and data according to the latency budget of the workflow, not according to neat organizational diagrams.

## Diagram / Flow Representation
### Browser Request Path
```mermaid
sequenceDiagram
    participant U as User Browser
    participant D as DNS Resolver
    participant E as Edge / CDN
    participant L as Load Balancer
    participant A as App Server
    participant DB as Database
    U->>D: Resolve domain
    D-->>U: IP / endpoint
    U->>E: HTTPS request
    E->>L: Forward cache miss or dynamic request
    L->>A: Route request
    A->>DB: Query data
    DB-->>A: Response
    A-->>U: HTML / JSON response
```

### Transport Decision Lens
```mermaid
flowchart TD
    Need[Need network communication] --> Reliable{Need reliable ordered delivery?}
    Reliable -->|Yes| TCP[TCP-based protocol]
    Reliable -->|No or custom| UDP[UDP-based protocol]
    TCP --> TLS[TLS / HTTPS / DB protocol]
    UDP --> QUIC[QUIC / streaming / custom realtime]
```

## Real-World Examples
- Google Search benefits from globally distributed edge points so the network path before search serving is as short as possible.
- Netflix relies on CDNs because moving content closer to users reduces both latency and origin bandwidth cost.
- Amazon mobile clients often benefit from request aggregation because every extra network round trip hurts performance on real mobile networks.
- Uber-like systems separate real-time location updates from strongly consistent payment paths because networking and latency requirements differ.

## Case Study
### What happens when you open Google?

Opening a familiar website is one of the best ways to understand networking fundamentals because it exposes the hidden layers that sit between a user action and an application response.

### Requirements
- A user should be routed to a nearby healthy edge point quickly.
- Communication should be encrypted and the server identity should be verified.
- Static and cacheable assets should be served efficiently without overloading origin systems.
- Dynamic requests should be forwarded to healthy application infrastructure with low latency.
- The system should degrade gracefully when some edges, routes, or backends are unhealthy.

### Design Evolution
- A small site may begin with a direct request to one server and simple DNS.
- As traffic grows, CDNs, TLS termination, and load balancers are introduced to shorten paths and distribute load.
- As traffic becomes global, regional routing, edge caching, and session reuse become more important.
- As security expectations rise, certificate automation, internal encryption, and service identity become part of the core design.

### Scaling Challenges
- DNS caching and TTL behavior can delay failover or misroute traffic if poorly configured.
- TLS handshakes add CPU and latency overhead if connection reuse is weak.
- Cross-region traffic can quietly dominate latency if services are deployed without thinking about data placement.
- Packet loss or partial network failures can create retry storms that look like application outages.

### Final Architecture
- Geo-aware DNS and edge routing to steer users to nearby healthy entry points.
- HTTPS with efficient connection reuse and TLS termination strategy.
- CDN layers for cacheable content and edge protection.
- Load-balanced application servers with health checks and regional failover behavior.
- Observability that measures DNS resolution time, handshake time, backend latency, and end-to-end response time separately.

## Architect's Mindset
- Treat network hops as part of the latency budget, not as invisible plumbing.
- Choose transport and protocol behavior according to the workflow, not by habit alone.
- Remember that secure-by-default networking changes cost and performance and must still be designed carefully.
- Place services according to data gravity and latency sensitivity.
- Model failures such as packet loss, slow links, and partial regional isolation explicitly.

## TLS 1.3 and Connection Reuse Patterns

TLS is not just a security checkbox — it is a latency tax on every new connection. Understanding the difference between TLS 1.2 and 1.3, and how connection reuse eliminates repeated overhead, is essential for performance-aware architecture.

### TLS Handshake Comparison

| Aspect | TLS 1.2 | TLS 1.3 |
|--------|---------|---------|
| Handshake round trips | 2 RTT | 1 RTT (0-RTT for resumption) |
| Cipher negotiation | Client offers many, server picks | Client predicts, server confirms |
| Forward secrecy | Optional (depends on cipher) | Mandatory (all ciphers use ephemeral keys) |
| 0-RTT resumption | Not supported | Supported (pre-shared key from previous session) |
| Latency for new connection | ~30-50ms (same region) | ~15-25ms (same region) |
| Latency for resumed connection | ~15-25ms | ~0ms (0-RTT sends data with first packet) |

**0-RTT caveat:** 0-RTT data is replayable — an attacker can capture and re-send the first flight. Only use 0-RTT for idempotent requests (GETs, not POSTs with side effects).

### Connection Reuse Strategies

Every new TCP+TLS connection costs 2-4 round trips before a single byte of application data flows. At scale, these costs dominate. Connection reuse amortizes the setup cost across many requests.

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **HTTP/1.1 Keep-Alive** | Reuse TCP connection for sequential requests | Simple APIs, low concurrency |
| **HTTP/2 Multiplexing** | Multiple concurrent streams over one TCP connection | High-concurrency APIs, browser-to-server |
| **HTTP/3 (QUIC)** | Multiple streams over UDP; no head-of-line blocking | Mobile clients, lossy networks, global users |
| **Connection pooling** | Application maintains pool of pre-established connections | Service-to-service, database connections |
| **TLS session resumption** | Cache session keys to skip full handshake on reconnect | Clients that reconnect frequently (mobile, IoT) |

**Impact example:**
```
Without connection reuse (new connection per request):
  DNS: 5ms + TCP: 15ms + TLS: 25ms + Request: 10ms = 55ms per request
  100 requests = 5,500ms total

With HTTP/2 multiplexing (one connection, 100 parallel streams):
  DNS: 5ms + TCP: 15ms + TLS: 25ms + 100 requests: 50ms = 95ms total
  → 58x faster for 100 requests
```

---

## The Edge Stack — Security and Performance at the Perimeter

Modern production systems place a stack of infrastructure at the network edge — between the user and the application. This edge stack handles security, performance, and traffic management before any request reaches business logic.

### Edge Stack Reference Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  USER (Browser / Mobile / API Client)                        │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼───────────────────────────────────────┐
│  DNS (Route 53 / Cloudflare)                                  │
│  • Geo-routing: steer to nearest region                       │
│  • Health-check routing: avoid unhealthy endpoints            │
│  • Failover: automatic region failover on health check fail   │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│  CDN / Edge (CloudFront / Cloudflare / Fastly)                │
│  • Static asset caching (CSS, JS, images)                     │
│  • TLS termination (reduces origin TLS overhead)              │
│  • Edge compute (Cloudflare Workers, Lambda@Edge)             │
│  • DDoS absorption (volumetric attack mitigation)             │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│  WAF (Web Application Firewall)                               │
│  • OWASP Top 10 protection (SQLi, XSS, SSRF)                │
│  • Rate limiting per IP / per user / per endpoint             │
│  • Bot detection and challenge (CAPTCHA, JS challenge)        │
│  • Geo-blocking (block traffic from restricted countries)     │
│  • Custom rules (block specific request patterns)             │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│  API Gateway (Kong / AWS API GW / Envoy)                      │
│  • Authentication (JWT validation, API key check)             │
│  • Rate limiting (per-tenant, per-plan quotas)                │
│  • Request routing (path-based, header-based)                 │
│  • Request/response transformation                            │
│  • Observability (access logs, metrics, trace ID injection)   │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│  Load Balancer (ALB / Nginx / Envoy)                          │
│  • Health checking (remove unhealthy backends)                │
│  • Connection draining (graceful shutdown)                     │
│  • TLS re-encryption (if end-to-end encryption required)      │
└──────────────────────┬───────────────────────────────────────┘
                       │
                  APPLICATION SERVERS
```

### Edge Component Decision Guide

| Component | When to Add | Skip If |
|-----------|-------------|---------|
| CDN | Any user-facing system with static assets or cacheable API responses | Internal-only service, all content is dynamic and personalized |
| WAF | Public-facing APIs, compliance requirements (PCI-DSS), any system exposed to the internet | Internal services behind VPN/private network |
| API Gateway | Multi-tenant APIs, external developer APIs, microservices needing centralized auth/rate-limiting | Single monolith with built-in auth and rate limiting |
| DDoS protection | Any system with public endpoints | Internal-only services |

---

## Network Retry and Timeout Policies

Network failures are inevitable. The difference between a resilient system and a fragile one is how it handles timeouts, retries, and partial failures. These policies should be designed alongside the architecture, not bolted on after the first outage.

### Timeout Strategy

| Timeout Type | Where to Set | Recommended Value | Why |
|-------------|-------------|-------------------|-----|
| Connection timeout | Client → Server | 1-3 seconds | Detect unreachable hosts fast; don't wait for TCP default (often 30-120s) |
| Request timeout | Client → Server | 5-30 seconds (depends on operation) | Prevent requests from hanging indefinitely; set per-endpoint based on expected latency |
| Idle timeout | Connection pool | 60-300 seconds | Reclaim connections that are no longer active |
| Downstream timeout | Service → Dependency | Shorter than caller's timeout | Prevent cascading timeouts (if caller times out at 10s, dependency must respond in < 8s) |

**The cascading timeout rule:** Each layer's timeout must be shorter than its caller's timeout, with room for retries:

```
User → API Gateway (30s) → Service A (10s) → Service B (3s) → Database (1s)

If Service B is slow:
  Database times out at 1s → Service B retries once → responds at 2s
  Service A receives response at 2s → well within 10s budget
  API Gateway receives at 2.5s → well within 30s budget
  User sees response at ~3s → acceptable
```

### Retry Strategy

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **No retry** | Fail immediately | Writes that are not idempotent; user can retry manually |
| **Fixed retry** | Wait N seconds, retry up to M times | Simple cases; adequate for most internal calls |
| **Exponential backoff** | Wait 1s, 2s, 4s, 8s... with jitter | External APIs, shared resources, distributed systems |
| **Retry with circuit breaker** | Stop retrying when failure rate exceeds threshold | Preventing retry storms from overloading a failing dependency |

**Retry safety rules:**
1. **Only retry idempotent operations** — retrying a non-idempotent POST can create duplicate orders, payments, or messages
2. **Add jitter** — without jitter, all clients retry at the same time and create thundering herds
3. **Set a retry budget** — limit total retries per second across all clients, not just per-client
4. **Propagate deadlines** — if the caller's deadline has passed, do not retry (the response is already too late)

### Cross-Reference: Resilience Patterns

These network policies connect directly to broader resilience patterns covered in other chapters:

| Pattern | Chapter | Connection |
|---------|---------|------------|
| Circuit breaker | F3: Distributed Systems Patterns | Stops calling a failing dependency after threshold failures |
| Bulkhead | F3: Distributed Systems Patterns | Isolates connection pools per dependency to prevent cascading exhaustion |
| Retry with backoff | F10: Observability & Operations | Must be observable — track retry rate as a signal of dependency health |
| Timeout tuning | F10: Observability & Operations | Monitor p99 latency per dependency to set informed timeout values |
| Load shedding | F1: Scalability Fundamentals | Reject excess requests at the edge rather than overloading backends |

---

## Multi-Region Routing Policies

DNS and edge routing determine which region serves each user request. The routing policy directly affects latency, availability, and disaster recovery.

### Routing Policy Comparison

| Policy | How It Works | Use Case | Limitation |
|--------|-------------|----------|-----------|
| **Latency-based** | Route to the region with lowest measured latency to the user | Global consumer apps | Requires health checks; latency measurement has some lag |
| **Geo-proximity** | Route to the geographically nearest region | Data residency compliance (EU users → EU region) | Nearest region may not be healthiest or fastest |
| **Weighted** | Distribute traffic by percentage (e.g., 90% primary, 10% secondary) | Canary deployments, gradual region migration | Manual weight management |
| **Failover** | Active-primary with standby; switch on health check failure | Disaster recovery (active-passive) | Recovery time depends on DNS TTL and health check interval |
| **Multivalue answer** | Return multiple healthy IPs; client picks one | Simple load distribution without a load balancer | No intelligence in routing; client picks randomly |

### Example: Global E-Commerce Routing

```
User in Frankfurt → DNS latency-based routing
  → EU region (eu-west-1): primary for EU users
  → Serves: product catalog (local replica), checkout (local primary)
  → Cross-region only for: global inventory sync (eventual consistency)

User in Tokyo → DNS latency-based routing
  → APAC region (ap-northeast-1): primary for APAC users
  → Serves: product catalog (local replica), checkout (local primary)

Failover scenario: EU region unhealthy
  → DNS health check detects failure (30s interval)
  → TTL expires (60s)
  → EU users routed to US region (us-east-1)
  → Failover latency: 90s-180s (health check + TTL propagation)
  → Trade-off: 70-150ms additional latency for EU users during failover
```

## Common Mistakes
- Blaming the application for latency without measuring DNS, TLS, or routing overhead.
- Using chatty APIs that require many sequential round trips over real mobile or cross-region networks.
- Ignoring connection reuse and paying handshake cost repeatedly.
- Treating internal traffic as trusted and skipping encryption or identity planning.
- Designing multi-region systems without considering cross-region latency and bandwidth.

## Interview Angle
- Interviewers often use this topic to test whether you understand what actually happens when a request travels across the internet.
- Strong answers explain DNS, TCP or QUIC setup, TLS, load balancing, and how these layers affect latency and reliability.
- Candidates stand out when they connect protocol behavior to higher-level architecture choices such as caching or regional deployment.
- A good answer stays practical: what is happening, where time is spent, and what design choices can improve the path.

## Quick Recap
- Networking is part of system design because request paths create latency and failure modes.
- HTTP/HTTPS define application communication; TCP and UDP define transport behavior.
- DNS and TLS are core parts of the user experience, not background trivia.
- Connection reuse, CDN placement, and cross-region distance materially change performance.
- Architects should reason about the full network path before optimizing application code.

## Practice Questions
1. What steps occur before a browser request reaches application code?
2. Why is TCP the default for most APIs and databases?
3. Where is UDP or QUIC a better fit than TCP?
4. How does TLS affect both performance and security design?
5. Why can a multi-region design become slower even if it looks more scalable?
6. How would you explain DNS caching to a junior engineer?
7. What metrics would you collect to separate network latency from application latency?
8. How do CDNs improve both performance and origin protection?
9. Why is connection reuse so important for mobile clients?
10. What kinds of failures are easy to miss if you think only at the application layer?

## Further Exploration
- Study HTTP/2, HTTP/3, and QUIC for deeper modern transport knowledge.
- Carry these ideas into the load balancing and caching chapters where request-path optimization becomes more concrete.
- Practice tracing the full request path of a real product you use every day.





## Navigation
- Previous: [Estimation & Capacity Planning](../01-foundations/03-estimation-capacity-planning.md)
- Next: [Databases Deep Dive](05-databases-deep-dive.md)
