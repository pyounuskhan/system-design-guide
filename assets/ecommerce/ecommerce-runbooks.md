# E-Commerce Core Commerce — Operational Runbooks

## Runbook 001: Inventory Oversell Detected

### Severity: P1 (Critical)
### Detection
- Alert: `inventory.oversell.detected` from reconciliation job
- Symptom: Order confirmed for an item with zero physical stock

### Investigation
1. Query the inventory ledger for the affected SKU:
   ```sql
   SELECT * FROM inventory_ledger
   WHERE sku_id = '<sku_id>' AND warehouse_id = '<wh_id>'
   ORDER BY created_at DESC LIMIT 50;
   ```
2. Check if the oversell was caused by:
   - Race condition (two concurrent reservations)
   - Reservation expiry + re-reservation by another buyer
   - Manual stock adjustment error
   - CDC lag causing stale availability display

### Resolution
1. **Immediate**: Contact the buyer proactively. Offer alternatives:
   - Fulfillment from another warehouse (if available)
   - Backorder with ETA
   - Full refund + discount coupon for inconvenience
2. **Cancel the unfulfillable order items** via OMS admin API
3. **Issue refund** for cancelled items
4. **Root cause fix**: If race condition, review inventory locking logic. If manual error, add validation.

### Prevention
- Ensure `SELECT FOR UPDATE` is used on all reservation paths
- Add oversell detection to the checkout saga (post-commit verification)
- Monitor `inventory.available` going negative

---

## Runbook 002: Checkout Error Rate Spike

### Severity: P1 (Critical)
### Detection
- Alert: `checkout.error_rate > 5%` sustained for 5 minutes
- Dashboard: Checkout Health dashboard in Grafana

### Investigation
1. Check which step is failing:
   ```
   checkout_error_by_step: inventory_reserve | tax_calculate | payment_authorize | order_create
   ```
2. If **inventory_reserve** failures:
   - Check PostgreSQL inventory DB CPU and connection count
   - Check for lock contention on hot SKUs (flash sale?)
   - Check reservation timeout (expired before commit?)
3. If **payment_authorize** failures:
   - Check PSP status page (Stripe status, Adyen status)
   - Check circuit breaker state for payment gateway
   - Check error codes: decline vs. timeout vs. 5xx
4. If **order_create** failures:
   - Check PostgreSQL order DB health
   - Check disk space and connection limits
   - Check Kafka producer (order events publishing)

### Resolution
1. **PSP failure**: If primary PSP is down, verify circuit breaker has opened and traffic is routing to secondary PSP
2. **DB overload**: Scale up read replicas; kill long-running queries; consider connection pool increase
3. **Flash sale contention**: Enable queue-based checkout; increase inventory bucket shards
4. **Kafka failure**: Checkout should not be blocked by Kafka; verify async publishing is non-blocking

### Escalation
- If unresolved in 15 minutes, escalate to on-call engineering lead
- If revenue impact > $10K/min, escalate to VP Engineering

---

## Runbook 003: Search Index Lag > 60 Seconds

### Severity: P2 (High)
### Detection
- Alert: `kafka.consumer_lag.search_indexer > 10000`
- Symptom: Products updated by sellers not appearing in search results

### Investigation
1. Check Kafka consumer lag for the `catalog-changes` topic:
   ```bash
   kafka-consumer-groups --describe --group search-indexer
   ```
2. Check Elasticsearch cluster health:
   ```bash
   curl -s localhost:9200/_cluster/health | jq .
   ```
3. Check indexer logs for errors:
   ```bash
   kubectl logs -l app=search-indexer --tail=100 | grep ERROR
   ```
4. Common causes:
   - Elasticsearch cluster yellow/red (disk space, node failure)
   - Indexer OOM (bulk index batch too large)
   - Schema mapping conflict (new field type mismatch)

### Resolution
1. **ES cluster unhealthy**: Add data node; increase disk; rebalance shards
2. **Indexer OOM**: Reduce batch size; increase memory limit
3. **Mapping conflict**: Fix mapping; reindex affected documents
4. **Consumer lag growing**: Scale up indexer instances; increase partition count if needed

### Buyer Impact
- Search results may show stale prices or stock status
- New products may not appear for up to 60s (normally < 5s)

---

## Runbook 004: Cart Service (Redis) Unresponsive

### Severity: P1 (Critical)
### Detection
- Alert: `redis.cart.latency_p99 > 50ms` or `redis.cart.connection_errors > 0`
- Symptom: Buyers cannot add items to cart or view cart

### Investigation
1. Check Redis cluster health:
   ```bash
   redis-cli -h cart-redis-001 cluster info
   redis-cli -h cart-redis-001 info memory
   ```
2. Check for:
   - Memory usage > 80% (eviction pressure)
   - Slow queries (`SLOWLOG GET 10`)
   - Network partition between cluster nodes
   - Connection count at limit

### Resolution
1. **Memory pressure**: Increase Redis instance size or add shards
2. **Slow queries**: Identify and optimize (e.g., large HGETALL on huge carts)
3. **Node failure**: Redis Cluster auto-failover should promote replica. Verify failover completed.
4. **Complete Redis failure**:
   - Cart reads fall back to PostgreSQL backup (degraded latency)
   - Cart writes queue in application memory, flush to DB
   - Notify engineering team; Redis recovery is priority

### Buyer Impact
- Cart operations slow (200ms instead of < 10ms) during degraded mode
- Guest carts may be lost if Redis data not recovered (no DB backup for guests)

---

## Runbook 005: Payment Gateway Degraded

### Severity: P1 (Critical)
### Detection
- Alert: `payment.auth.error_rate > 10%` or `payment.auth.latency_p99 > 5s`
- Circuit breaker state: `OPEN` for primary PSP

### Investigation
1. Check PSP status pages:
   - Stripe: https://status.stripe.com
   - Adyen: https://status.adyen.com
2. Check error codes from PSP responses:
   - `card_declined` — buyer's card issue (not a system issue)
   - `rate_limit` — we're sending too many requests
   - `5xx` — PSP internal error
   - `timeout` — network issue between us and PSP
3. Check circuit breaker metrics in Grafana

### Resolution
1. **PSP outage**: Circuit breaker should already be routing to secondary PSP. Verify.
2. **Rate limiting**: Back off; implement request queuing
3. **Network issue**: Check VPN/peering with PSP; try different egress IP
4. **All PSPs down** (rare):
   - Display "Payment temporarily unavailable" to buyers
   - Allow buyers to save checkout session and retry later
   - Do NOT queue blind payment attempts

### Communication
- Update status page if checkout is impacted
- Notify customer support team about expected buyer complaints

---

## Runbook 006: Order Event Processing Backlog

### Severity: P2 (High)
### Detection
- Alert: `kafka.consumer_lag.order_events > 5000`
- Symptom: Delayed notifications, late fulfillment signals

### Investigation
1. Identify which consumer group is lagging:
   ```bash
   kafka-consumer-groups --describe --group fulfillment-service
   kafka-consumer-groups --describe --group notification-service
   kafka-consumer-groups --describe --group analytics-pipeline
   ```
2. Check consumer logs for errors or slow processing
3. Check if a specific partition is hot (one order generating many events)

### Resolution
1. **Slow consumer**: Scale up consumer instances (up to partition count)
2. **Poison message**: If one message repeatedly fails, send to dead-letter queue and skip
3. **Hot partition**: Rebalance Kafka partitions; review partition key strategy
4. **Consumer bug**: Roll back consumer deployment if recently changed

### Impact
- Fulfillment delayed (buyer doesn't receive shipping notification promptly)
- Analytics dashboard shows stale data
- Seller dashboard may show outdated order status

---

## Runbook 007: Flash Sale Preparation Checklist

### Severity: Proactive (run 24h before sale)

### Pre-Sale Checklist

1. **Capacity verification**:
   - [ ] Scale checkout service to 10x normal pod count
   - [ ] Scale API gateway to handle 500K RPS
   - [ ] Verify Redis has 50% headroom on memory
   - [ ] Verify PostgreSQL connection pool can handle surge

2. **Inventory preparation**:
   - [ ] Pre-allocate inventory buckets for flash sale SKUs
   - [ ] Set up queue-based checkout for limited-quantity items
   - [ ] Configure rate limits: 1 unit per buyer per flash SKU

3. **Caching**:
   - [ ] Pre-warm CDN cache for sale landing pages
   - [ ] Pre-warm Redis cache for sale product data
   - [ ] Extend CDN TTL for static assets to 1 hour

4. **Monitoring**:
   - [ ] Set up dedicated flash sale dashboard
   - [ ] Lower alert thresholds for checkout error rate (> 2% instead of 5%)
   - [ ] Assign dedicated on-call engineer for sale duration

5. **Communication**:
   - [ ] Notify PSP about expected traffic spike with time and volume estimate
   - [ ] Notify CDN provider about expected bandwidth spike
   - [ ] Prepare customer support team with FAQ for sale issues

### During Sale
- Monitor: checkout success rate, inventory consumption rate, queue depth
- Be ready to: increase queue capacity, fail over PSP, scale pods

### Post-Sale
- [ ] Scale down services to normal levels
- [ ] Review metrics: peak RPS, error rate, oversell incidents, revenue
- [ ] Run inventory reconciliation job immediately
- [ ] Archive flash sale event data for future capacity planning

---

## Runbook 008: Database Failover (PostgreSQL)

### Severity: P1 (Critical)
### Detection
- Alert: `postgresql.primary.unreachable`
- RDS: Multi-AZ automatic failover triggered

### Investigation
1. Check AWS RDS events console for failover notification
2. Verify new primary is promoted:
   ```sql
   SELECT pg_is_in_recovery();  -- should return false on new primary
   ```
3. Check application connection pool reconnection

### Resolution
1. **Automatic failover (RDS Multi-AZ)**: Usually completes in 60-120 seconds. Applications reconnect automatically if using connection pooling with retry.
2. **Manual failover needed**: Promote read replica to primary:
   ```bash
   aws rds promote-read-replica --db-instance-identifier orders-replica-1
   ```
3. **Update DNS/connection strings** if not using RDS proxy or automatic endpoint switching
4. **Verify data consistency**: Run quick count checks on critical tables (orders, inventory)

### Post-Incident
- [ ] Investigate root cause of primary failure
- [ ] Ensure new replica is created for the new primary
- [ ] Run reconciliation job to verify no data loss during failover window
- [ ] Update incident report

---

## Runbook 009: Refund Processing Failure

### Severity: P2 (High)
### Detection
- Alert: `refunds.failed.count > 10` in 1 hour
- Queue: Dead-letter queue for refund events growing

### Investigation
1. Check refund failure reasons in DB:
   ```sql
   SELECT failure_reason, count(*) FROM refunds
   WHERE status = 'failed' AND created_at > now() - interval '1 hour'
   GROUP BY failure_reason;
   ```
2. Common failure reasons:
   - PSP refund API returning errors
   - Original payment method expired/closed
   - Insufficient platform balance for refunds
   - Idempotency conflict (duplicate refund attempt)

### Resolution
1. **PSP API errors**: Check PSP status; retry failed refunds after PSP recovery
2. **Expired payment method**: Automatically fall back to store credit; notify buyer
3. **Insufficient balance**: Escalate to finance team; process refunds in batches
4. **Duplicate attempts**: Verify idempotency keys; skip duplicates

### Buyer Impact
- Buyers expecting refunds will see "processing" status longer than expected
- Proactive communication: send email explaining delay with updated ETA

---

## Runbook 010: Nightly Reconciliation Drift

### Severity: P3 (Medium) — unless drift is large
### Detection
- Alert: `reconciliation.drift > threshold` from nightly job
- Report: Daily reconciliation report emailed to finance team

### Types of Drift

1. **Inventory drift** (logical stock != physical stock):
   - Small drift (< 1%): Normal. Caused by timing of warehouse scans.
   - Large drift (> 5%): Investigate. Possible causes: unreported damage, theft, system bug.

2. **Payment drift** (authorized amount != captured amount):
   - Common cause: Partial fulfillment (only some items shipped)
   - Also: Currency conversion rounding, tax adjustment

3. **Order-inventory drift** (committed orders != inventory decrements):
   - Cause: Saga compensation didn't complete (inventory not released after cancelled order)
   - Fix: Run compensation retry job

### Resolution
1. Review reconciliation report for anomalies
2. For inventory drift: Schedule physical count for affected SKUs
3. For payment drift: Generate adjustment entries; reconcile with PSP statement
4. For order-inventory drift: Run `inventory.reconcile` job with `--fix` flag (with approval)

### Frequency
- Run nightly at 2 AM (low traffic window)
- Full reconciliation: Weekly (comprehensive, all SKUs)
- Spot reconciliation: Daily (high-value items, recently problematic SKUs)
