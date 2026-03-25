# Escrow System API Examples

## Authentication Model
- Tenant backends use OAuth2 client credentials or mTLS.
- Operator tools use SSO plus scoped JWTs.
- Every mutating request requires an `Idempotency-Key`.

## Create Escrow
```http
POST /v1/escrows
Authorization: Bearer <token>
Idempotency-Key: 6d3d4f2a-create-0001
Content-Type: application/json
```

```json
{
  "tenant_id": "tenant_marketplace_india",
  "external_order_id": "ord_983741",
  "region_legal_entity": "IN-MUM-01",
  "currency": "INR",
  "amount_minor": 1250000,
  "buyer": {
    "party_id": "buyer_001",
    "display_name": "Aarav Kumar"
  },
  "seller": {
    "party_id": "seller_981",
    "display_name": "Prime Gadgets"
  },
  "release_policy": {
    "mode": "buyer_accept_or_timer",
    "inspection_window_hours": 72
  },
  "metadata": {
    "category": "used-electronics",
    "shipment_required": true
  }
}
```

```json
{
  "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
  "state": "CREATED",
  "amount_minor": 1250000,
  "currency": "INR",
  "timeline": {
    "next_expected_action": "buyer_funding"
  }
}
```

## Fund Escrow
```http
POST /v1/escrows/esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK/fund
Authorization: Bearer <token>
Idempotency-Key: 6d3d4f2a-fund-0001
Content-Type: application/json
```

```json
{
  "payment_method": {
    "type": "card_token",
    "token": "pm_tok_abc123"
  },
  "capture_mode": "immediate"
}
```

```json
{
  "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
  "funding_attempt_id": "fund_01J9YJ6F8Q32YV1T7D6Q8K1N6P",
  "state": "FUNDING_PENDING",
  "provider_reference": "pi_3Pw....",
  "next_expected_action": "provider_confirmation"
}
```

## Approve Release
```http
POST /v1/escrows/esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK/approve
Authorization: Bearer <token>
Idempotency-Key: 6d3d4f2a-approve-0001
Content-Type: application/json
```

```json
{
  "approved_by": "buyer_001",
  "note": "Item received and verified."
}
```

```json
{
  "escrow_id": "esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK",
  "state": "RELEASE_PENDING",
  "payout_attempt_id": "payout_01J9YJJ5D9Q94SWQG9F0V2A0PW",
  "next_expected_action": "seller_payout_settlement"
}
```

## Open Dispute
```http
POST /v1/escrows/esc_01J9YJ4Q7P7W3T6Y6Y4V9R1MFK/disputes
Authorization: Bearer <token>
Idempotency-Key: 6d3d4f2a-dispute-0001
Content-Type: application/json
```

```json
{
  "opened_by": "buyer_001",
  "reason_code": "ITEM_NOT_AS_DESCRIBED",
  "description": "Serial number does not match listing.",
  "evidence_refs": [
    "evi_01J9YJMP0G9A2C5D6X8W9F1QRS"
  ]
}
```

```json
{
  "dispute_id": "disp_01J9YJN2R2N9T3J6V4J1E8F1FJ",
  "state": "DISPUTED",
  "review_queue": "electronics-quality"
}
```

## Provider Webhook Example
```json
{
  "provider_event_id": "evt_1Q0....",
  "type": "payment.captured",
  "occurred_at": "2026-03-20T08:11:30Z",
  "data": {
    "payment_intent_id": "pi_3Pw....",
    "amount_minor": 1250000,
    "currency": "INR",
    "status": "captured"
  }
}
```

## Error Codes

| Code | Meaning |
| --- | --- |
| `ESCROW_INVALID_STATE_TRANSITION` | Requested action is not legal for the current escrow state |
| `ESCROW_DUPLICATE_IDEMPOTENCY_KEY` | Request was already processed with the same idempotency scope |
| `ESCROW_PROVIDER_PENDING` | External provider response is pending or ambiguous |
| `ESCROW_DISPUTE_ACTIVE` | Escrow is frozen because a dispute is open |
| `ESCROW_POLICY_BLOCKED` | Tenant policy or compliance rule blocked the transition |
| `ESCROW_PAYOUT_ACCOUNT_INVALID` | Seller payout destination failed validation |
