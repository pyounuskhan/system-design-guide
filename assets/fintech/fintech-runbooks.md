# Fintech & Payments — Operational Runbooks

## Runbook 001: Ledger Imbalance Detected

### Severity: P0 (Critical — Money Integrity)
### Detection
- Alert: `ledger.balance_invariant.violated`
- Query: `SUM(debits) != SUM(credits)` for any currency

### Investigation
1. Identify the time window when imbalance appeared
2. Find the last balanced checkpoint
3. Query journal entries in the window:
   ```sql
   SELECT entry_id, description, reference_type, reference_id,
          SUM(CASE WHEN direction='debit' THEN amount ELSE 0 END) as debits,
          SUM(CASE WHEN direction='credit' THEN amount ELSE 0 END) as credits
   FROM ledger_postings lp
   JOIN journal_entries je ON lp.entry_id = je.entry_id
   WHERE je.created_at BETWEEN $start AND $end
   GROUP BY entry_id, description, reference_type, reference_id
   HAVING SUM(CASE WHEN direction='debit' THEN amount ELSE 0 END) !=
          SUM(CASE WHEN direction='credit' THEN amount ELSE 0 END);
   ```
4. Common causes:
   - Application bug: one side of a journal entry failed but other side committed
   - DB failover: transaction partially committed during synchronous replica failure
   - Manual adjustment without balancing entry

### Resolution
1. **Halt new transactions on affected accounts** until root cause identified
2. Create correcting journal entry to restore balance
3. Root cause fix deployed and verified
4. File incident report for audit trail

---

## Runbook 002: PSP Authorization Rate Drop

### Severity: P1 (Critical)
### Detection
- Alert: `payment.auth.success_rate < 90%` for any PSP
- Dashboard: Payment Health → Auth Rate by PSP

### Investigation
1. Check if the drop is across all card types or specific BINs
2. Check PSP status page
3. Check decline reasons:
   ```sql
   SELECT decline_reason, count(*) FROM payments
   WHERE psp_id = 'stripe' AND status = 'declined'
     AND created_at > now() - interval '1 hour'
   GROUP BY decline_reason ORDER BY count DESC;
   ```
4. If decline reasons are "do_not_honor" or generic: likely PSP or issuer issue
5. If decline reasons are "insufficient_funds": normal buyer behavior, not a system issue

### Resolution
1. If PSP is degraded: verify circuit breaker has opened and traffic is routing to secondary PSP
2. If specific BIN range: add routing rule to bypass degraded PSP for affected BINs
3. If our error: check request formatting, API version, credentials

---

## Runbook 003: Payment Stuck in "Processing" Status

### Severity: P2 (High)
### Detection
- Alert: `payments.processing.age > 10_minutes` count increasing
- Cron job: scan payments in `processing` status older than 10 minutes

### Investigation
1. Check if PSP webhook was received:
   ```sql
   SELECT * FROM payment_events
   WHERE payment_id = $payment_id AND event_type LIKE 'psp_webhook%';
   ```
2. If no webhook: PSP webhook delivery failed. Poll PSP for status.
3. If webhook received but not processed: check consumer logs for errors.

### Resolution
1. Poll PSP for transaction status
2. If PSP says authorized: update our status to `authorized`, post ledger entry
3. If PSP says declined: update status to `declined`, notify merchant
4. If PSP says unknown: escalate; do NOT auto-retry (risk of double charge)

---

## Runbook 004: Reconciliation Exceptions Above Threshold

### Severity: P2 (High)
### Detection
- Alert: `reconciliation.exceptions > 50` in daily batch

### Investigation
1. Categorize exceptions:
   ```sql
   SELECT exception_type, count(*) FROM recon_exceptions
   WHERE batch_date = CURRENT_DATE
   GROUP BY exception_type;
   ```
2. Common categories:
   - **Missing in PSP report**: our transaction not in PSP's settlement file
   - **Missing in our system**: PSP transaction we don't have
   - **Amount mismatch**: FX rounding, fee calculation difference
   - **Duplicate**: same transaction in PSP report twice

### Resolution
1. **Missing in PSP**: wait 24h (PSP processing delay). If still missing after 48h, open PSP support ticket.
2. **Missing in our system**: replay from PSP report; investigate missed webhook.
3. **Amount mismatch**: if < $1, auto-adjust with correction entry. If > $1, investigate.
4. **Duplicate**: verify idempotency; if true duplicate, flag for PSP.

---

## Runbook 005: Wallet Negative Balance Detected

### Severity: P1 (Critical)
### Detection
- Alert: `wallet.balance < 0` for any account
- This should never happen — indicates a bug in concurrency control

### Investigation
1. Find the transaction that caused negative balance:
   ```sql
   SELECT * FROM wallet_transactions
   WHERE wallet_id = $wallet_id
   ORDER BY created_at DESC LIMIT 20;
   ```
2. Check for race condition: two concurrent debits that both passed the balance check
3. Check for chargeback reversal on a topped-up wallet that was subsequently spent

### Resolution
1. If race condition bug: freeze wallet, fix concurrency control, deploy fix
2. If chargeback reversal: set balance to 0, create debt record for collections
3. Alert compliance team (negative balance may indicate fraud or system exploitation)

---

## Runbook 006: Fraud Model Scoring Latency Spike

### Severity: P2 (High)
### Detection
- Alert: `fraud.scoring.latency_p99 > 150ms`
- Impact: Adds latency to every payment authorization

### Investigation
1. Check ML model serving infrastructure:
   - CPU/memory utilization of inference servers
   - Model loading time (cold start after deploy?)
   - Feature store (Redis) latency
2. Check if feature assembly is slow:
   - Redis velocity counter reads
   - User history lookups
3. Check for traffic spike (legitimate or DDoS)

### Resolution
1. **Feature store slow**: scale Redis; optimize feature queries
2. **Model serving overloaded**: scale inference instances; enable GPU if not already
3. **Cold start**: pre-warm models on deployment
4. **Emergency bypass**: if scoring is critically slow, temporarily skip ML scoring and rely on rules engine only (higher false negative risk but maintains payment throughput)

---

## Runbook 007: Chargeback Rate Approaching Card Network Threshold

### Severity: P2 (High) — escalates to P1 if threshold crossed
### Detection
- Alert: `merchant.chargeback_rate > 0.65%` (Visa threshold: 0.9%, MC: 1.0%)
- Dashboard: Fraud Health → Chargeback Rate by Merchant

### Investigation
1. Identify merchants with highest chargeback rates
2. Categorize chargebacks: fraud vs. friendly fraud vs. service disputes
3. Check if specific campaigns or products are driving chargebacks

### Resolution
1. **Individual merchant over threshold**: Contact merchant; require remediation plan within 7 days
2. **Platform-wide increase**: Review fraud model; check for new attack pattern
3. **If threshold exceeded**: Card networks impose fines ($5K-$100K/month). Escalate to executive team.
4. **Prevention**: Enable 3DS for merchants with > 0.5% chargeback rate; require fraud insurance for high-risk merchants

---

## Runbook 008: AML Suspicious Activity Alert

### Severity: P2 (High — Regulatory)
### Detection
- Alert: `aml.suspicious_activity.detected`
- Compliance dashboard flags transaction pattern

### Response
1. **Do NOT alert the customer** — tipping off is a criminal offense in most jurisdictions
2. Compliance officer reviews the case within 24 hours
3. If SAR is warranted: file within 30 days (US FinCEN) or 48 hours (UK NCA)
4. Document investigation and decision, whether SAR is filed or not
5. Consider account restrictions if risk is high (freeze, limit withdrawals)

### Documentation Required
- Transaction details and pattern analysis
- Customer KYC information
- Previous activity history
- Decision rationale (file SAR / no SAR)
- Reviewer name and timestamp

---

## Runbook 009: HSM Key Rotation

### Severity: Planned Maintenance
### Frequency: Quarterly

### Pre-Rotation Checklist
- [ ] Generate new key pair in HSM
- [ ] Test new key with tokenization service in staging
- [ ] Schedule rotation window (low-traffic period)
- [ ] Notify on-call team

### Rotation Steps
1. Load new key into HSM production slot (dual-key mode)
2. Update tokenization service to use new key for new tokens
3. Old key remains active for decrypting existing tokens
4. Monitor error rates during transition
5. After 7 days: verify all active tokens re-encrypted with new key
6. After 30 days: decommission old key

### Rollback
If error rate spikes during rotation: revert tokenization service to old key. Investigate before retrying.
