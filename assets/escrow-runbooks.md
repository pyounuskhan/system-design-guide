# Escrow System Runbooks

## SLO Snapshot

| SLI | Target |
| --- | --- |
| Escrow status read availability | 99.95% |
| Valid write acceptance | 99.9% |
| Provider webhook processing within 2 minutes | 99% |
| Scheduled auto-release execution within 5 minutes | 99% |

## Runbook: Funding Provider Timeout Storm
### Symptoms
- Spike in `ESCROW_PROVIDER_PENDING`
- Increased webhook backlog
- Funding success rate drops while provider latency rises

### Actions
1. Confirm whether the provider is partially degraded or fully down.
2. Freeze aggressive client retries if they risk duplicate funding attempts.
3. Shift new escrows to degraded mode if policy allows, for example pause high-risk funding methods.
4. Increase operator visibility for pending escrows older than SLA.
5. Run targeted reconciliation once provider stabilizes.

## Runbook: Duplicate Webhook Flood
### Symptoms
- Sharp increase in duplicate webhook dedupe hits
- Elevated provider callback volume without corresponding real transaction growth

### Actions
1. Confirm dedupe table health and uniqueness enforcement.
2. Verify webhook receipt writes are succeeding.
3. Rate-limit provider ingress if absolutely necessary, while preserving audit logs.
4. Replay only unprocessed unique events after stabilization.

## Runbook: Auto-Release Jobs Delayed
### Symptoms
- Scheduled releases not firing on time
- Backlog in workflow or timer queue

### Actions
1. Inspect workflow-engine queue depth and worker saturation.
2. Scale workers if compute-starved.
3. Prioritize release and refund timers above lower-priority notifications.
4. If SLA breach continues, hand off affected escrows to operator queue.

## Runbook: Payout Failure After Release Decision
### Symptoms
- Escrow state moved to `RELEASE_PENDING`
- Payout provider returns invalid account, bank reject, or delayed failure

### Actions
1. Keep funds in seller-payable internal state; do not mark final settlement complete.
2. Notify seller and tenant if required.
3. Retry with configured policy or request payout-account correction.
4. Escalate to finance if settlement remains blocked beyond SLA.

## Runbook: Reconciliation Mismatch
### Symptoms
- Internal ledger and provider report disagree
- Missing payout settlement or unexpected refund

### Actions
1. Open reconciliation case automatically.
2. Freeze further irreversible actions on the affected escrow if needed.
3. Inspect provider references, webhook history, and ledger postings.
4. Apply operator-reviewed adjustment only through explicit compensating entries.
5. Capture root cause for provider, parser, or workflow defects.
