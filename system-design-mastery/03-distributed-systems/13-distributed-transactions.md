# 13. Distributed Transactions

## Part Context
**Part:** Part 3 - Distributed Systems Concepts  
**Position:** Chapter 13 of 60
**Why this part exists:** This section explains the trade-offs that appear once systems scale across machines, replicas, regions, and failure domains.  
**This chapter builds toward:** workflow correctness across services, data stores, and failure-prone business processes

## Overview
A local database transaction is relatively simple: either the grouped operations commit or they do not. Distributed transactions are difficult because the business workflow spans multiple services, databases, or external systems that do not share one atomic commit boundary.

This chapter explains how architects reason about correctness when one user action affects many components. The goal is not perfect magic atomicity everywhere. The goal is safe business behavior under delay, retries, partial failure, and recovery.

## Why This Matters in Real Systems
- Real business workflows such as checkout, booking, and onboarding almost always cross service boundaries.
- If distributed correctness is not designed carefully, systems leak money, inventory, trust, and operator time.
- This topic ties together consistency, resilience, and business-state modeling.
- Interviewers use it to see whether candidates can move beyond happy-path request-response thinking.

## Core Concepts
### Why local ACID is not enough
Once multiple services or datastores are involved, one database transaction no longer protects the full business action.

### Two-phase commit (2PC)
2PC coordinates multiple participants through prepare and commit phases, offering stronger all-or-nothing behavior but at significant operational and availability cost.

### Saga pattern
A Saga breaks a large workflow into smaller local transactions linked by events or orchestration, using compensating actions when later steps fail.

### Workflow state and reconciliation
Distributed correctness depends on explicit state transitions, retry semantics, and the ability to inspect or recover stuck workflows.

## Key Terminology
| Term | Definition |
| --- | --- |
| 2PC | A coordination protocol that asks distributed participants to prepare, then commit or abort together. |
| Saga | A sequence of local transactions with compensating actions for failure recovery. |
| Compensation | A business-level action that semantically undoes or offsets an earlier successful step. |
| Coordinator | The service or component responsible for progressing or directing the distributed workflow. |
| Orchestration | A workflow style where a central coordinator tells each participant what to do next. |
| Choreography | A workflow style where services react to events without one central coordinator. |
| Pending State | A temporary state indicating the workflow is in progress but not yet fully resolved. |
| Reconciliation | The process of detecting and repairing workflows that ended in ambiguous or stuck states. |

## Detailed Explanation
### Business correctness comes first
Architects should begin by asking what a safe business outcome looks like if one step succeeds and a later step fails. “The transaction failed” is not enough. The system must know whether to refund, release inventory, retry, or request human review. Distributed transactions are therefore about business semantics, not only protocol mechanics.

### 2PC gives stronger coordination at a price
Two-phase commit can provide a stronger all-or-nothing outcome across participants, but it introduces blocking behavior, tighter coupling, and vulnerability to coordinator or participant unavailability. It is often reasonable in tightly controlled environments, but many internet-scale service architectures avoid it across autonomous services.

### Sagas trade atomicity for recoverable workflows
A Saga accepts that the overall workflow is not one atomic write. Instead, each step commits locally, and failures later in the process trigger compensating actions. This works well when the business can tolerate and define meaningful undo behavior.

### Ambiguity must be observable
A distributed workflow can end in ambiguous states: payment authorized but inventory not reserved, order created but email not sent, shipment booked but customer cancelation racing in. Good systems model these states clearly and provide tooling to reconcile them.

### Idempotency and retries remain central
The same event or command may be delivered more than once due to retry behavior. Participants therefore need idempotent operations, deterministic state transitions, and enough metadata to detect duplicates safely.

## Diagram / Flow Representation
### 2PC Simplified
```mermaid
sequenceDiagram
    participant C as Coordinator
    participant P1 as Participant 1
    participant P2 as Participant 2
    C->>P1: Prepare
    C->>P2: Prepare
    P1-->>C: Ready
    P2-->>C: Ready
    C->>P1: Commit
    C->>P2: Commit
```

### Saga Workflow Example
```mermaid
flowchart LR
    Order[Create Order] --> Inventory[Reserve Inventory]
    Inventory --> Payment[Authorize Payment]
    Payment --> Ship[Create Shipment]
    Ship --> Success[Order Confirmed]
    Payment -. failure .-> Comp1[Release Inventory]
    Ship -. failure .-> Comp2[Refund / Void Payment]
```

## Real-World Examples
- Amazon-style checkout workflows span orders, payment, inventory, and fulfillment systems, which rarely fit inside one local transaction boundary.
- Travel booking platforms often use saga-like compensations because flight, hotel, and car reservations belong to different providers and timelines.
- Ride-sharing systems may need careful distributed state when trip acceptance, pricing, and payment events race under high concurrency.
- Fintech systems often centralize stronger transactional guarantees around the ledger while using asynchronous workflows elsewhere.

## Case Study
### E-commerce checkout as a distributed transaction

Checkout is a useful case because it combines user expectations of immediacy with business requirements for correctness across several systems that may fail independently.

### Requirements
- An order should not be confirmed without the required business conditions being satisfied.
- Customers should not be charged twice or left in ambiguous states without recovery.
- Inventory should not remain reserved forever if the rest of the workflow fails.
- The system should tolerate retries and partial outages.
- Operators must be able to inspect, replay, and reconcile failed workflows.

### Design Evolution
- A first version may centralize more of the workflow inside one service and one database where possible.
- As separate payment, inventory, and fulfillment services emerge, local transactions plus saga orchestration become more attractive.
- As failure cases accumulate, compensations, audit trails, and reconciliation jobs become formalized.
- As scale and product complexity increase, event-driven state propagation and clearer workflow state machines become necessary.

### Scaling Challenges
- External payment or shipping providers can introduce long delays and ambiguous acknowledgments.
- Retries can create duplicate side effects unless each step is idempotent.
- Partial success across services creates business confusion unless the workflow state is explicit.
- Without reconciliation, rare edge cases accumulate into financial or operational drift.

### Final Architecture
- A durable order intent recorded early with a workflow identifier.
- Local transactions inside each service instead of pretending one ACID boundary covers everything.
- Saga orchestration or carefully designed event choreography for progression and compensation.
- Clear workflow states such as pending, confirmed, failed, compensated, or needs-review.
- Operational tooling for replay, reconciliation, and support visibility.

## Architect's Mindset
- Begin from business safety, not from protocol names.
- Use stronger coordination only where the business cannot tolerate compensation-based recovery.
- Model workflow states explicitly so both machines and humans can reason about them.
- Design compensation paths and reconciliation tooling at the same time as the happy path.
- Assume retries, duplicates, and ambiguous acknowledgments will occur.

## 2PC vs Saga vs Outbox — Comparison

These three approaches solve different problems. Use this table to choose.

| Dimension | 2PC | Saga (Orchestration) | Saga (Choreography) | Transactional Outbox |
|-----------|-----|---------------------|--------------------|--------------------|
| **Atomicity** | Strong (all-or-nothing across participants) | Eventual (local commits + compensation) | Eventual (local commits + compensation) | Atomic within one service (DB + event in same txn) |
| **Coupling** | Tight (all participants must be available) | Medium (orchestrator knows participants) | Loose (services react to events) | Low (producer and consumer decoupled) |
| **Availability during failure** | Low (blocked if any participant is unavailable) | Medium (can pause and retry per step) | High (each service is independent) | High (events queued for later delivery) |
| **Latency** | Higher (synchronous prepare+commit) | Moderate (sequential steps) | Lower (parallel where possible) | Lowest (async, non-blocking) |
| **Compensation logic** | Rollback (automatic) | Required (explicitly coded per step) | Required (each service handles its own) | Not needed (single-service boundary) |
| **When to use** | Tightly coupled DB-to-DB within one org (e.g., ledger entries) | Multi-step business workflows (checkout, booking) | Loosely coupled services, different team ownership | Publishing events reliably from a service |
| **When NOT to use** | Across autonomous internet services | Simple single-service writes | Workflows needing strict ordering or central visibility | Cross-service workflow coordination |

### Saga Decision Rubric

Use this flowchart to choose the right distributed transaction approach:

```
Is the entire workflow within one database?
  → YES: Use local ACID transaction (no distributed pattern needed)
  → NO: Does it cross services?
    → YES: Can you tolerate eventual consistency + compensation?
      → YES: Do you need central visibility and step ordering?
        → YES: Use SAGA with ORCHESTRATION
        → NO:  Use SAGA with CHOREOGRAPHY
      → NO (must be all-or-nothing):
        → Are all participants within your org and available synchronously?
          → YES: Use 2PC (sparingly)
          → NO:  Redesign — 2PC across autonomous services will fail
    → NO: Does one service need to publish events reliably?
      → YES: Use TRANSACTIONAL OUTBOX (+ CDC relay)
```

---

## Orchestration vs Choreography — Deep Comparison

| Aspect | Orchestration | Choreography |
|--------|-------------|-------------|
| **Control flow** | Central orchestrator tells each service what to do next | Each service reacts to events and decides what to do |
| **Visibility** | Orchestrator has full workflow state | No single service knows the full workflow |
| **Debugging** | Query orchestrator for step status | Must correlate events across services |
| **Coupling** | Services coupled to orchestrator | Services coupled to event schema |
| **Adding steps** | Change orchestrator logic | Add new consumer (no change to existing services) |
| **Failure handling** | Orchestrator triggers compensation | Each service compensates itself on failure event |
| **Best for** | Complex multi-step workflows (checkout, onboarding, loan approval) | Loose integrations (analytics, notifications, search indexing) |

### Orchestration Example (Checkout)

```
Orchestrator (Order Service):
  Step 1: Reserve Inventory → await confirmation
  Step 2: Authorize Payment → await confirmation
  Step 3: Create Shipment → await confirmation
  Step 4: Mark Order Confirmed

  On Step 2 failure:
    Compensate Step 1: Release Inventory
    Mark Order: Failed (payment declined)

  On Step 3 failure:
    Compensate Step 2: Void Payment Authorization
    Compensate Step 1: Release Inventory
    Mark Order: Failed (shipment unavailable)
```

### Choreography Example (Post-Order Side Effects)

```
OrderConfirmed event published to Kafka topic

Consumers (independent, no coordinator):
  → Email Service:      Send confirmation email
  → Analytics Service:  Record conversion event
  → Loyalty Service:    Award points
  → Recommendation:     Update purchase history

Each consumer processes independently.
Failure in one does not affect others.
No compensation needed (these are side effects, not core workflow).
```

**Guideline:** Use orchestration for the core business workflow (where ordering and compensation matter). Use choreography for side effects and integrations (where independence matters more than coordination).

---

## Idempotent Participants — Patterns for Saga Steps

Every participant in a distributed transaction must be idempotent because retries and redelivery are inevitable.

### Pattern 1: Idempotency Key Per Saga Step

```python
# Each saga step uses an idempotency key derived from the workflow ID + step
def reserve_inventory(order_id, items):
    idempotency_key = f"reserve:{order_id}"

    # Check if already processed
    existing = db.query(
        "SELECT * FROM inventory_reservations WHERE idempotency_key = %s",
        (idempotency_key,)
    )
    if existing:
        return existing  # Already reserved — return same result

    # Perform reservation
    reservation = create_reservation(items)
    db.execute(
        "INSERT INTO inventory_reservations (idempotency_key, order_id, items, status) "
        "VALUES (%s, %s, %s, 'reserved')",
        (idempotency_key, order_id, json.dumps(items))
    )
    return reservation
```

### Pattern 2: State Machine Guard

```python
# Only process if workflow is in the expected state
def authorize_payment(order_id, amount):
    order = db.query("SELECT status FROM orders WHERE id = %s FOR UPDATE", (order_id,))

    if order.status == 'payment_authorized':
        return  # Already done — idempotent
    if order.status != 'inventory_reserved':
        raise InvalidStateError(f"Cannot authorize from state: {order.status}")

    # Process payment
    result = payment_gateway.authorize(order_id, amount)
    db.execute(
        "UPDATE orders SET status = 'payment_authorized', payment_ref = %s WHERE id = %s",
        (result.ref, order_id)
    )
```

### Pattern 3: Replayable Workflow with Checkpoint

```python
# Orchestrator replays from last successful checkpoint
def execute_saga(order_id):
    workflow = load_workflow(order_id)

    steps = [
        ("inventory_reserved", reserve_inventory),
        ("payment_authorized", authorize_payment),
        ("shipment_created", create_shipment),
        ("order_confirmed", confirm_order),
    ]

    for target_state, step_func in steps:
        if workflow.state >= target_state:
            continue  # Already past this step

        try:
            step_func(order_id)
            workflow.advance_to(target_state)
        except StepFailure as e:
            trigger_compensation(order_id, workflow.state)
            workflow.advance_to("failed")
            raise
```

---

## Compensation Testing Guidance

Compensation paths are the most under-tested code in most systems. If you only test the happy path, you are only testing half the saga.

### What to Test

| Test Category | What to Verify | Example |
|--------------|---------------|---------|
| **Happy-path compensation** | Each step's compensation undoes its effect cleanly | Reserve inventory → Release inventory: count returns to original |
| **Idempotent compensation** | Compensating twice produces same result as compensating once | Releasing already-released inventory does not double-add stock |
| **Partial-failure compensation** | Compensation runs for completed steps only, not for steps that never started | If payment fails, compensate inventory but don't compensate shipment (never created) |
| **Concurrent compensation** | Compensation races with the forward workflow | Cancellation arrives while payment is still processing — system reaches consistent state |
| **Compensation after delay** | Compensation works even if triggered hours after the original step | Refund after 3 hours: payment provider still honors void |
| **Compensation observability** | Compensation events are logged and visible to operators | Support team can see "order-789: inventory released, payment voided" |

### Compensation Test Checklist

- [ ] Every saga step has a corresponding compensation function
- [ ] Compensation functions are idempotent (tested with duplicate invocations)
- [ ] Compensation handles "step never completed" gracefully (no-op, not error)
- [ ] Compensation events are published for audit and observability
- [ ] Integration tests cover at least 3 failure scenarios (step 2 fails, step 3 fails, step N fails)
- [ ] Load tests verify compensation under concurrent traffic
- [ ] Reconciliation job detects orders stuck in intermediate states for > X minutes

---

## Exactly-Once Expectations Management

"Exactly-once" in distributed transactions is a practical engineering outcome, not a protocol guarantee. Here is how to set correct expectations.

| What People Say | What It Actually Means | How to Achieve It |
|----------------|----------------------|-------------------|
| "Exactly-once delivery" | At-least-once delivery + idempotent consumer | Idempotency keys, dedup store, upserts |
| "Exactly-once processing" | Each message's *effect* happens once, even if delivered multiple times | State machine guards, conditional writes |
| "No duplicate charges" | Payment authorization is idempotent; settlement uses idempotency keys | Payment provider idempotency key (e.g., Stripe `idempotency_key`) |
| "No double-booking" | Reservation uses optimistic locking or unique constraint | `INSERT ... ON CONFLICT DO NOTHING` or `version` check |
| "No lost events" | At-least-once delivery with durable queue | Kafka with acks=all, outbox pattern, consumer offset commit after processing |

**The practical rule:** Design every participant as if it will receive every message at least twice. If the system produces the correct business outcome regardless of duplicates, you have "effectively exactly-once."

### Cross-References

| Topic | Chapter |
|-------|---------|
| Outbox pattern and CDC | Ch 5: Databases; Ch 8: Message Queues |
| Idempotent consumption patterns | Ch 8: Message Queues |
| Consistency models (strong vs eventual) | Ch 11: Consistency & CAP |
| Circuit breakers and retries | Ch 12: Fault Tolerance |
| SLO for workflow completion time | F10: Observability & Operations |
| Event-driven architecture (CQRS, event sourcing) | Architectural Patterns chapters |

## Common Mistakes
- Assuming a local database transaction can protect a workflow that spans multiple services.
- Using sagas without real compensating actions.
- Ignoring ambiguous or stuck states because they are “rare.”
- Building non-idempotent steps inside retry-heavy distributed workflows.
- Focusing on coordination mechanics without defining the desired business outcome under failure.

## Interview Angle
- Distributed transaction questions usually appear when a design involves payment, inventory, booking, or any multi-step cross-service workflow.
- Strong answers compare 2PC and saga trade-offs and then choose based on business semantics, coupling, and availability needs.
- Candidates stand out when they discuss compensation, reconciliation, and explicit workflow states rather than only protocol names.
- A weak answer says “use transactions” without explaining where the transaction boundary actually lives.

## Quick Recap
- Distributed transactions are about safe business workflows across multiple boundaries.
- 2PC provides stronger all-or-nothing behavior but adds coupling and blocking cost.
- Sagas use local transactions and compensation to recover from failure.
- Workflow state, idempotency, and reconciliation are central to correctness.
- Architects should optimize for business-safe outcomes, not for mythical global atomicity everywhere.

## Practice Questions
1. Why does a local ACID transaction stop being enough in a service-oriented workflow?
2. What are the main costs of 2PC?
3. When is a saga a better fit than stronger coordination?
4. What makes a compensation valid and useful?
5. How would you represent the lifecycle of a distributed checkout workflow?
6. Why is reconciliation necessary even with good retry logic?
7. How does idempotency support distributed correctness?
8. What kinds of workflows cannot tolerate loose compensation easily?
9. How would you explain distributed transaction design to a product or operations stakeholder?
10. What observability would you add to a distributed workflow engine?

## Further Exploration
- Connect this chapter with the architectural pattern chapters where event-driven and CQRS approaches may support workflow design.
- Study outbox patterns, workflow engines, and saga orchestration implementations in more depth.
- Practice drawing the state machine for a complex multi-step workflow before choosing technologies.





## Navigation
- Previous: [Fault Tolerance & Resilience](12-fault-tolerance-resilience.md)
- Next: [Monolith vs Microservices](../04-architectural-patterns/14-monolith-vs-microservices.md)
