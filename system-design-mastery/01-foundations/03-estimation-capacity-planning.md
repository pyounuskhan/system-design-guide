# 3. Estimation & Capacity Planning

## Part Context
**Part:** Part 1 - Foundations of System Design  
**Position:** Chapter 3 of 60
**Why this part exists:** This opening section gives the reader the language, framing, and mental models needed to reason about systems before choosing technologies.  
**This chapter builds toward:** credible high-level design, bottleneck identification, and interview-ready back-of-the-envelope reasoning

## Overview
System design becomes real when numbers enter the conversation. Capacity planning is the process of translating user behavior and product requirements into rough but useful estimates for throughput, storage, bandwidth, and compute. The goal is not mathematical perfection. The goal is architectural realism.

When an architect says “this will probably need caching” or “this database will become the bottleneck first,” that judgment is usually backed by quick mental math. These estimates help decide whether a single database is enough, whether background processing is necessary, and which parts of the design deserve optimization first.

## Why This Matters in Real Systems
- Estimation prevents both under-design and expensive over-design.
- It helps you identify the likely bottleneck before you spend time optimizing the wrong layer.
- It provides the numbers needed to justify architectural choices in design reviews and interviews.
- It trains the habit of reasoning from user behavior rather than from technology marketing.

## Core Concepts
### Back-of-the-envelope estimation
Quick calculations based on simple assumptions are often enough to size the first version of a system and understand pressure points.

### Traffic estimation
Average load is useful, but peak load is usually what breaks systems. Estimation therefore needs both daily volume and concentration behavior.

### Storage estimation
Raw object size is only the beginning. Replication, indexes, metadata, backups, thumbnails, logs, and retention all expand the real number.

### Read-write ratio and bottlenecks
Architectures are shaped differently by read-heavy, write-heavy, and compute-heavy workloads. Estimation tells you which shape you are dealing with.

## Key Terminology
| Term | Definition |
| --- | --- |
| QPS | Queries or requests per second; a common throughput estimate for API traffic. |
| Peak Traffic | The highest expected concentration of load in a short time window. |
| Replication Factor | The number of data copies maintained for availability or durability. |
| Headroom | Extra reserved capacity to handle bursts, incidents, or forecast error. |
| Bandwidth | The rate at which data can be transferred across a network path. |
| Retention | How long data must be stored before deletion or archival. |
| Read-Write Ratio | The relative number of reads versus writes in the workload. |
| Hotspot | A concentrated source of traffic or data access that overloads one part of the system. |

## Detailed Explanation
### Start from product behavior, not server counts
A strong estimate begins with users and actions: daily active users, requests per session, uploads per day, average object size, and expected peak concentration. Hardware sizing comes later. This keeps the reasoning grounded in product behavior rather than vague infrastructure intuition.

### Always estimate peaks, not just averages
If a system receives 100 million reads per day, the average might look manageable, but traffic is never evenly distributed. Peak hours, market events, product launches, and regional traffic patterns create concentrated spikes. Systems usually fail at the peak, not at the average.

### Storage numbers grow through multipliers
Suppose each object is 1 MB. That is not the final storage estimate. You may also store thumbnails, metadata, indexes, logs, backups, or multiple encoded versions. Replication multiplies the result again. Good capacity planning therefore uses expansion factors instead of raw object size alone.

### Estimation should change the design
If the result of your estimate does not influence your architecture, the exercise is incomplete. A very high read volume may justify caches and CDN layers. A high write stream may require partitioning or queues. A modest internal workload may prove that a simple monolith is still the right answer.

### Sanity checks matter
Estimates do not need to be exact, but they should be internally consistent. If your numbers imply an impossibly large cluster for a tiny product, check your assumptions. If your storage number looks too small to account for replication and retention, check again. Architects use estimates to reason, not to impress.

## Diagram / Flow Representation
### Estimation Workflow
```mermaid
flowchart LR
    U[Users and behavior] --> A[Assumptions]
    A --> T[Traffic estimates]
    A --> S[Storage estimates]
    T --> B[Bottleneck analysis]
    S --> B
    B --> D[Architecture decisions]
```

### From Daily Traffic to Peak QPS
```mermaid
flowchart TD
    Daily[Daily requests] --> Avg[Average requests per second]
    Avg --> Peak[Apply peak multiplier]
    Peak --> Headroom[Add safety headroom]
    Headroom --> Capacity[Required capacity target]
```

## Real-World Examples
- Twitter-like timelines are usually read-heavy, so caches and fan-out strategies are often driven by read-volume estimates rather than write counts alone.
- YouTube-like systems must estimate raw uploads, transcoded renditions, thumbnails, and CDN egress, not just original file storage.
- Amazon-style sale events force teams to design for short intense spikes, not for average daily traffic.
- WhatsApp-like chat systems may have moderate message sizes but extremely high message frequency, making throughput and queue sizing central.

## Case Study
### Estimating a Twitter-like system

A microblogging platform is a good estimation case because it combines write traffic, feed reads, media attachments, and skewed popularity. The numbers do not need to be exact; they need to reveal the right architectural pressure points.

### Requirements
- Users can publish short posts, follow accounts, and read personalized timelines.
- The system should support a very large daily active population with global traffic distribution.
- Timeline reads should feel fast and continuously fresh enough for a consumer social product.
- Posts and metadata should be durable, and popular accounts may generate traffic far above the average user.
- The architecture should remain cost-aware instead of blindly overprovisioned.

### Design Evolution
- Start by estimating posts per user per day and total daily writes.
- Estimate timeline refresh frequency separately because reads usually dominate writes in social products.
- Add storage for post text, metadata, secondary indexes, media references, replication, and long-term retention.
- Use the resulting read-write ratio to decide whether the first bottleneck is likely to be database reads, feed generation, cache pressure, or write ingestion.

### Scaling Challenges
- Celebrity or news-event spikes create extreme skew that invalidates simple average-based models.
- Timeline generation can become more expensive than raw post creation because one write may fan out to many followers.
- Hot content drives cache churn and can overload downstream stores if misses are not controlled.
- Media attachments and analytics expand storage and bandwidth beyond the base text workload.

### Final Architecture
- A write path optimized for ingesting posts durably and asynchronously triggering downstream fan-out or feed updates.
- A read path protected by caches and possibly precomputed or hybrid feed models.
- Storage separated between metadata, media references, and large binary objects.
- Capacity plans that reserve headroom for event spikes and partial-failure scenarios.
- Metrics and observability that track QPS, miss rate, storage growth, and queue lag over time.

## Architect's Mindset
- Make assumptions explicit enough that others can challenge them.
- Estimate for the peak and then add headroom for burstiness, failure, and forecasting error.
- Use numbers to justify complexity; do not add sharding or queues just because they sound advanced.
- Revisit estimates as the product changes because old assumptions quietly become dangerous.
- Ask which number is most likely to break the system first, not just which number is easiest to compute.

## Interview Estimation Cheat Sheet

Memorize these numbers to order-of-magnitude accuracy. They are not precise benchmarks — they are reasoning anchors that let you sanity-check estimates during an interview or design review.

### Latency Numbers Every Engineer Should Know

| Operation | Approximate Latency |
|-----------|-------------------|
| L1 cache reference | 1 ns |
| L2 cache reference | 4 ns |
| Main memory reference | 100 ns |
| SSD random read | 16 μs |
| HDD random read | 4 ms |
| Read 1 MB sequentially from SSD | 50 μs |
| Read 1 MB sequentially from HDD | 2 ms |
| Read 1 MB sequentially from network (1 Gbps) | 10 ms |
| Round trip within same datacenter | 0.5 ms |
| Round trip cross-continent (US-EU) | 70-150 ms |
| Disk seek (HDD) | 4-10 ms |
| TCP handshake (same region) | 1-3 ms |
| TLS handshake (same region) | 5-15 ms |

### Quick Conversion Table

| Input | Formula | Result |
|-------|---------|--------|
| 1 million requests/day | ÷ 86,400 | ~12 QPS |
| 100 million requests/day | ÷ 86,400 | ~1,200 QPS |
| 1 billion requests/day | ÷ 86,400 | ~12,000 QPS |
| Average QPS → Peak QPS | × 2-5 (use 3 as default) | Peak QPS |
| 1 KB × 1 billion | = 1 TB | |
| 1 MB × 1 million | = 1 TB | |
| 1 GB/sec for 1 day | = 86.4 TB/day | |

### Power-of-Two Reference

| Power | Exact | Approximate |
|-------|-------|-------------|
| 2^10 | 1,024 | ~1 thousand |
| 2^20 | 1,048,576 | ~1 million |
| 2^30 | 1,073,741,824 | ~1 billion |
| 2^40 | 1,099,511,627,776 | ~1 trillion |

### Server Capacity Rules of Thumb

| Resource | Typical Limit | Notes |
|----------|--------------|-------|
| Single PostgreSQL instance | 5,000-10,000 QPS (read), 1,000-5,000 QPS (write) | Depends on query complexity and indexing |
| Single Redis instance | 100,000+ QPS | In-memory, single-threaded per core |
| Single Kafka broker | 100,000+ messages/sec | Depends on message size and partition count |
| WebSocket connections per server | 50,000-100,000 | Depends on message frequency and memory |
| Single Nginx/ALB | 10,000+ concurrent connections | With proper tuning |

---

## Cost-per-Request Modeling

Estimation is incomplete without cost awareness. Knowing that your system handles 10,000 QPS is useful. Knowing that each request costs $0.0003 and your monthly bill is $78K is actionable.

### The Cost Estimation Formula

```
Monthly cost = Compute + Storage + Bandwidth + Managed Services + Observability

Where:
  Compute   = (instances × hourly_rate × 730 hours)
  Storage   = (total_GB × $/GB/month) + (IOPS × $/IOPS if applicable)
  Bandwidth = (egress_GB × $/GB)   — ingress is usually free
  Managed   = (per-request fees) + (per-host fees) + (per-GB fees)
  Observability = (log_GB × $/GB) + (metric_series × $/series) + (trace_spans × $/span)
```

### Cost Per Request Calculation

```
Cost per request = Monthly infrastructure cost / Monthly request count

Example:
  Monthly cost: $15,000
  Monthly requests: 500 million
  Cost per request: $15,000 / 500,000,000 = $0.00003 (0.003 cents)

  At 10x growth (5B requests): $150,000/month
  At 100x growth (50B requests): $1,500,000/month → cost optimization required
```

### Cloud Cost Quick Reference

| Resource | Approximate Cost (AWS us-east-1, 2025) | Unit |
|----------|---------------------------------------|------|
| EC2 m6i.xlarge (4 vCPU, 16 GB) | ~$140/month on-demand, ~$85/month reserved | Per instance |
| RDS PostgreSQL db.r6g.xlarge | ~$350/month on-demand | Per instance |
| ElastiCache Redis r6g.large | ~$175/month | Per node |
| S3 Standard storage | $0.023/GB/month | Per GB |
| S3 Glacier | $0.004/GB/month | Per GB |
| CloudFront egress | $0.085/GB (first 10 TB) | Per GB |
| NAT Gateway processing | $0.045/GB | Per GB |
| Kafka (MSK) m5.large | ~$200/month | Per broker |
| Lambda | $0.20 per 1M invocations + duration | Per request |
| API Gateway | $3.50 per 1M requests | Per request |

### Storage Lifecycle Tiers

Not all data deserves the same storage class. Tiering data by access frequency reduces costs dramatically at scale.

| Tier | Access Pattern | Storage Class | Cost ($/GB/month) | Retrieval Latency | Use Case |
|------|---------------|--------------|-------------------|-------------------|----------|
| Hot | Frequent (multiple times/day) | SSD, in-memory, S3 Standard | $0.02-0.10 | < 10ms | Active user data, current sessions, cache |
| Warm | Occasional (weekly) | HDD, S3 Infrequent Access | $0.01-0.03 | 10ms-1s | Recent logs, 30-day analytics, older user data |
| Cold | Rare (monthly or less) | S3 Glacier Instant | $0.004 | 50ms-5min | 90-day compliance data, archived media |
| Archive | Regulatory / disaster only | S3 Glacier Deep Archive | $0.001 | 12-48 hours | 7-year audit logs, legal hold data |

**Cost impact example:**
```
100 TB stored entirely in S3 Standard = $2,300/month
100 TB with lifecycle tiers:
  10 TB hot  (S3 Standard)   = $230/month
  20 TB warm (S3 IA)         = $250/month
  30 TB cold (Glacier Inst)  = $120/month
  40 TB archive (Glacier DA) = $40/month
  Total                      = $640/month (72% savings)
```

---

## Multi-Region Traffic Assumptions

For systems serving a global user base, estimation must account for geographic distribution. Multi-region deployment changes traffic patterns, latency budgets, and cost structure.

### Traffic Distribution Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| Single-region dominant | 80%+ traffic from one region | US-only SaaS product |
| Dual-region | Two primary regions, active-active or active-passive | US + EU for GDPR compliance |
| Global | Traffic distributed across 3+ regions | Consumer social media, global e-commerce |

### Multi-Region Estimation Adjustments

| Factor | Single Region | Multi-Region | Impact |
|--------|--------------|-------------|--------|
| Total QPS | Sum of all traffic | Split by region (e.g., 40% US, 30% EU, 20% APAC, 10% other) | Each region sized for its peak, not global peak |
| Database | Single primary | Primary per region OR global primary + read replicas | Cross-region replication lag (100-300ms) affects consistency model |
| Latency budget | ~50ms for DB + ~20ms for cache | Add 70-150ms cross-continent if reads hit remote region | Forces data locality or edge caching strategy |
| Storage | 1x (plus replication factor) | N× regions × replication factor | Costs multiply; use CDN for static assets |
| Bandwidth | Internal only | + cross-region replication traffic ($0.02/GB) | Replication egress adds significant cost at scale |
| Cost multiplier | 1x | 1.5-2.5x (depends on active-active vs active-passive) | Factor into cost estimation from the start |

**Rule of thumb:** Multi-region deployment roughly doubles infrastructure cost. Only deploy multi-region when the business requires it (latency SLO, data residency, disaster recovery).

---

## Scenario Exercises with Latency Targets

These exercises combine estimation with latency budgeting (p95/p99 targets). Practice them to build interview fluency.

### Exercise 1: Photo-Sharing App (Instagram-like)

```
Given:
  500M MAU, 300M DAU
  Each user views 20 photos/day, uploads 0.5 photos/day
  Average photo: 2 MB (original), 200 KB (compressed/thumbnail)

Estimate:
  Upload QPS: 300M × 0.5 / 86,400 = ~1,700 QPS (peak 3x = 5,100 QPS)
  View QPS: 300M × 20 / 86,400 = ~69,000 QPS (peak 3x = 207,000 QPS)
  Read:Write ratio = 40:1 → heavily read-optimized design

  Daily storage (originals): 300M × 0.5 × 2 MB = 300 TB/day
  Daily storage (compressed): 300M × 0.5 × 200 KB = 30 TB/day
  Annual storage: (300 + 30) TB/day × 365 = ~120 PB/year

  Bandwidth (egress): 207K QPS × 200 KB = 41 GB/sec peak

Latency budget (photo view, p99 < 200ms):
  CDN hit:         0ms   (90% of views)
  CDN miss path:   |
    DNS:           5ms
    TLS:           10ms
    API gateway:   5ms
    Auth check:    10ms (cached)
    S3 fetch:      50ms
    Image resize:  0ms  (pre-computed)
    CDN cache set: 5ms
    Response:      15ms
    Total:         100ms (within budget)

Architecture implication:
  - CDN is critical (must achieve 90%+ cache hit rate)
  - Pre-compute thumbnails at upload time, not at view time
  - 120 PB/year requires lifecycle tiering (hot 7 days, warm 90 days, cold after)
```

### Exercise 2: Real-Time Ride Matching (Uber-like)

```
Given:
  50M MAU, 20M monthly rides
  Average ride: 15 minutes, location update every 4 seconds from driver
  Active drivers at any time: ~500K

Estimate:
  Location update QPS: 500K / 4 = 125,000 QPS
  Ride request QPS: 20M / 30 days / 86,400 = ~8 QPS average (peak 10x = 80 QPS)
  Match request is low QPS but latency-critical

  Location data per update: ~100 bytes (lat, lng, timestamp, driver_id)
  Daily location data: 125K × 86,400 × 100 bytes = ~1 TB/day (hot, ephemeral)

Latency budget (ride match, p95 < 3 seconds):
  User request:       5ms
  Geospatial query:   50ms  (find nearby drivers within radius)
  Driver filtering:   20ms  (availability, rating, vehicle type)
  ETA calculation:    100ms (routing API call)
  Driver notification: 200ms (push notification to driver app)
  Driver response:     2,000ms (human response time, timeout at 15s)
  Total to first offer: ~375ms (system) + driver response

  p95 target: first driver notified within 500ms of request

Architecture implication:
  - Geospatial index (H3, S2, or geohash) for sub-50ms spatial queries
  - Location data is hot but ephemeral — no need for durable storage past 24h
  - 125K QPS location writes → in-memory store (Redis) or time-series DB
  - Match latency is dominated by driver response, not system processing
```

### Exercise 3: Notification Platform (High-Volume Batch)

```
Given:
  200M users, 3 notifications/user/day average
  Peak: marketing blast to all users in 30-minute window
  Channels: push (60%), email (30%), SMS (10%)

Estimate:
  Daily notifications: 200M × 3 = 600M/day
  Average QPS: 600M / 86,400 = ~7,000 QPS
  Marketing blast: 200M notifications in 30 min = 111K/sec (peak)
  With channel fan-out (avg 1.3 channels): 144K deliveries/sec peak

  SMS cost: 200M × 0.10 × $0.0075/SMS = $150K/month
  Email cost: 200M × 0.30 × $0.10/1000 = $6K/month
  Push cost: 200M × 0.60 × ~free (APNS/FCM) = ~$0

Latency budget (transactional notification, p99 < 30 seconds):
  API ingestion:    5ms
  Preference check: 10ms (Redis lookup)
  Template render:  5ms
  Queue publish:    10ms (Kafka)
  Queue → worker:   variable (depends on queue depth)
  Provider API:     100-2000ms (push: 100ms, email: 500ms, SMS: 2000ms)
  Total:            target < 5 seconds for transactional, < 30 min for batch

Architecture implication:
  - Priority queues: transactional (OTP, alerts) must skip the marketing queue
  - SMS is the cost bottleneck (not compute) → requires budget governance
  - Marketing blast: staged rollout over 30 min to avoid provider rate limits
  - Cost per notification varies 1000x between push ($0) and SMS ($0.0075)
```

## Common Mistakes
- Planning with average QPS and ignoring peak concentration.
- Estimating raw object size but forgetting replication, backups, derived data, and indexes.
- Producing numbers that never influence the actual architecture decision.
- Assuming traffic is evenly distributed across users, keys, or regions.
- Treating capacity planning as a one-time spreadsheet instead of an evolving part of system ownership.

## Interview Angle
- Estimation is a standard part of system design interviews because it reveals whether you can reason from first principles.
- Interviewers do not usually expect precise real-world numbers. They expect a clear method, explicit assumptions, and a sanity-checked conclusion.
- Strong candidates explain how the estimates change the architecture: for example, whether caching, partitioning, or async processing becomes justified.
- A good interview answer shows formulas, assumptions, peak multipliers, and the likely bottleneck.

## Quick Recap
- Capacity planning translates user behavior into traffic, storage, and bandwidth expectations.
- Average traffic is useful, but peak traffic usually determines design pressure.
- Replication, indexes, and derived artifacts expand storage beyond raw object size.
- Read-write ratio helps reveal the likely bottleneck and the right architecture shape.
- Estimation is valuable only when it changes design decisions.

## Practice Questions
1. Why is peak QPS more useful than average QPS for system design?
2. How would you estimate storage for a photo-sharing product?
3. What hidden multipliers should you add to a raw object-size estimate?
4. How does read-write ratio influence whether caching is important?
5. How would you estimate headroom for a major product launch?
6. What is a sign that your estimate is internally inconsistent?
7. How might celebrity skew affect a social media capacity plan?
8. When is a simple single-database design still the correct result of estimation?
9. How would you explain capacity planning to a non-technical stakeholder?
10. What metrics would you monitor after launch to validate your assumptions?

## Further Exploration
- Carry these estimation habits into the networking and database chapters that follow.
- Practice quick calculations for chat, ride-sharing, and streaming systems.
- As you study real-world systems, ask which estimate is secretly shaping the architecture the most.





## Navigation
- Previous: [Types of Requirements](02-types-of-requirements.md)
- Next: [Networking Fundamentals](../02-building-blocks/04-networking-fundamentals.md)
