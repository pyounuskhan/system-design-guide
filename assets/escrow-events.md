# Escrow System Event Contracts

## Topic Naming
- `escrow.lifecycle.v1`
- `payment.webhook.v1`
- `payout.result.v1`
- `risk.signal.v1`
- `notification.request.v1`
- `reconciliation.case.v1`

## Event Envelope
```json
{
  "event_id": "evt_01J9Z2DQ3R6M7F2M9APB8G0VYZ",
  "event_type": "escrow.funded",
  "event_version": 1,
  "tenant_id": "tenant_marketplace_india",
  "region_legal_entity": "IN-MUM-01",
  "aggregate_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
  "occurred_at": "2026-03-20T08:12:30Z",
  "trace_id": "9f31a1f6f7e548d5a2f0d4fe11bc9028",
  "payload": {}
}
```

## escrow.created
```json
{
  "event_type": "escrow.created",
  "payload": {
    "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
    "external_order_id": "ord_983741",
    "buyer_party_id": "buyer_001",
    "seller_party_id": "seller_981",
    "currency": "INR",
    "amount_minor": 1250000,
    "release_mode": "buyer_accept_or_timer"
  }
}
```

## escrow.funded
```json
{
  "event_type": "escrow.funded",
  "payload": {
    "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
    "funding_attempt_id": "fund_01J9YJ6F8Q32YV1T7D6Q8K1N6P",
    "provider": "stripe_like_psp",
    "provider_reference": "pi_3Pw....",
    "amount_minor": 1250000,
    "currency": "INR"
  }
}
```

## escrow.release_scheduled
```json
{
  "event_type": "escrow.release_scheduled",
  "payload": {
    "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
    "release_deadline_at": "2026-03-24T08:12:30Z",
    "reason": "buyer_review_window_started"
  }
}
```

## escrow.disputed
```json
{
  "event_type": "escrow.disputed",
  "payload": {
    "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
    "dispute_id": "disp_01J9YJN2R2N9T3J6V4J1E8F1FJ",
    "reason_code": "ITEM_NOT_AS_DESCRIBED",
    "opened_by": "buyer_001"
  }
}
```

## escrow.released
```json
{
  "event_type": "escrow.released",
  "payload": {
    "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
    "payout_attempt_id": "payout_01J9YJJ5D9Q94SWQG9F0V2A0PW",
    "seller_party_id": "seller_981",
    "released_amount_minor": 1235000,
    "platform_fee_minor": 15000,
    "currency": "INR"
  }
}
```

## escrow.refunded
```json
{
  "event_type": "escrow.refunded",
  "payload": {
    "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
    "funding_attempt_id": "fund_01J9YJ6F8Q32YV1T7D6Q8K1N6P",
    "refunded_amount_minor": 1250000,
    "currency": "INR",
    "reason": "seller_failed_to_fulfill"
  }
}
```

## payment.webhook.normalized
```json
{
  "event_type": "payment.webhook.normalized",
  "payload": {
    "provider": "stripe_like_psp",
    "provider_event_id": "evt_1Q0....",
    "normalized_status": "captured",
    "provider_reference": "pi_3Pw....",
    "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK"
  }
}
```

## reconciliation.case.opened
```json
{
  "event_type": "reconciliation.case.opened",
  "payload": {
    "reconciliation_case_id": "recon_01J9Z3RBNF1M3V2YAW6J0Z8A7Q",
    "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
    "mismatch_type": "payout_missing_provider_settlement",
    "severity": "high"
  }
}
```
