# Fintech & Payments — Event Catalog

## Event Bus: Apache Kafka

Topic naming: `{domain}.{entity}.{action}`
Key: Entity ID (for partition ordering)
Format: JSON with standard envelope
Retention: 30 days (financial events require longer retention)

---

## Payment Events

### Topic: `payment.created`
```json
{
  "event_type": "payment.created",
  "data": {
    "payment_id": "pay_abc123",
    "merchant_id": "mer_xyz",
    "amount": 149.99,
    "currency": "USD",
    "payment_method": "card",
    "idempotency_key": "idem_123"
  }
}
```
**Consumers**: Fraud Engine, Analytics

### Topic: `payment.authorized`
```json
{
  "event_type": "payment.authorized",
  "data": {
    "payment_id": "pay_abc123",
    "psp_id": "stripe",
    "psp_reference": "pi_abc",
    "auth_code": "A12345",
    "fraud_score": 0.12
  }
}
```
**Consumers**: Ledger (post auth hold), Notification, Analytics

### Topic: `payment.captured`
```json
{
  "event_type": "payment.captured",
  "data": {
    "payment_id": "pay_abc123",
    "capture_amount": 149.99,
    "captured_at": "2026-03-22T10:30:00Z"
  }
}
```
**Consumers**: Ledger (post capture), Settlement Queue, Notification

### Topic: `payment.refunded`
```json
{
  "event_type": "payment.refunded",
  "data": {
    "payment_id": "pay_abc123",
    "refund_amount": 149.99,
    "refund_type": "full",
    "reason": "customer_request",
    "psp_refund_id": "re_xyz"
  }
}
```
**Consumers**: Ledger (post reversal), Notification, Analytics

### Topic: `payment.disputed`
```json
{
  "event_type": "payment.disputed",
  "data": {
    "payment_id": "pay_abc123",
    "dispute_id": "dp_123",
    "reason": "fraudulent",
    "amount": 149.99,
    "respond_by": "2026-04-05T00:00:00Z"
  }
}
```
**Consumers**: Merchant Notification, Chargeback Team, Ledger (hold funds)

---

## Wallet Events

### Topic: `wallet.transfer.completed`
```json
{
  "event_type": "wallet.transfer.completed",
  "data": {
    "sender_wallet_id": "wal_sender",
    "receiver_wallet_id": "wal_receiver",
    "amount": 50.00,
    "currency": "USD"
  }
}
```
**Consumers**: Ledger, AML Monitoring, Notification, Analytics

### Topic: `wallet.topup.completed`
```json
{
  "event_type": "wallet.topup.completed",
  "data": {
    "wallet_id": "wal_xyz",
    "amount": 100.00,
    "source": "card",
    "payment_id": "pay_topup_123"
  }
}
```
**Consumers**: Ledger, Notification

### Topic: `wallet.withdrawal.completed`
```json
{
  "event_type": "wallet.withdrawal.completed",
  "data": {
    "wallet_id": "wal_xyz",
    "amount": 200.00,
    "destination": "bank_account",
    "bank_transfer_id": "bt_abc"
  }
}
```
**Consumers**: Ledger, Notification, AML Monitoring

---

## Settlement Events

### Topic: `settlement.batch.completed`
```json
{
  "event_type": "settlement.batch.completed",
  "data": {
    "batch_id": "batch_20260322",
    "psp_id": "stripe",
    "total_amount": 1250000.00,
    "currency": "USD",
    "transaction_count": 25000,
    "exceptions": 12
  }
}
```
**Consumers**: Ledger (post settlement entries), Finance Dashboard, Alert (if exceptions > threshold)

### Topic: `reconciliation.exception.found`
```json
{
  "event_type": "reconciliation.exception.found",
  "data": {
    "exception_id": "exc_789",
    "type": "amount_mismatch",
    "payment_id": "pay_abc123",
    "our_amount": 149.99,
    "psp_amount": 150.00,
    "difference": 0.01
  }
}
```
**Consumers**: Exception Queue, Finance Alert

---

## Fraud Events

### Topic: `fraud.score.computed`
```json
{
  "event_type": "fraud.score.computed",
  "data": {
    "payment_id": "pay_abc123",
    "score": 0.85,
    "decision": "block",
    "top_features": ["ip_country_mismatch", "high_velocity", "new_device"],
    "model_version": "v3.2.1"
  }
}
```
**Consumers**: Analytics, Model Retraining Pipeline

### Topic: `fraud.chargeback.received`
```json
{
  "event_type": "fraud.chargeback.received",
  "data": {
    "payment_id": "pay_abc123",
    "original_fraud_score": 0.12,
    "fraud_confirmed": true
  }
}
```
**Consumers**: Model Retraining Pipeline (label correction), Analytics

---

## KYC Events

### Topic: `kyc.verification.completed`
```json
{
  "event_type": "kyc.verification.completed",
  "data": {
    "user_id": "usr_xyz",
    "kyc_level": "standard",
    "result": "approved",
    "provider": "jumio",
    "verified_at": "2026-03-22T10:00:00Z"
  }
}
```
**Consumers**: Wallet Service (unlock higher limits), Notification, Compliance Log

### Topic: `aml.suspicious_activity.detected`
```json
{
  "event_type": "aml.suspicious_activity.detected",
  "data": {
    "user_id": "usr_xyz",
    "pattern": "structuring",
    "details": "15 transactions of $9,900 in 7 days",
    "risk_level": "high",
    "action": "file_sar"
  }
}
```
**Consumers**: Compliance Team Alert, Regulatory Reporting Service, Account Freeze Service

---

## Consumer Group Configuration

| Topic | Consumer Group | Parallelism | Processing Guarantee |
|-------|---------------|-------------|---------------------|
| `payment.*` | `ledger-service` | 6 consumers | Exactly-once (idempotent) |
| `payment.*` | `notification-service` | 6 consumers | At-least-once |
| `payment.*` | `analytics-pipeline` | 12 consumers | At-least-once |
| `payment.*` | `settlement-service` | 3 consumers | Exactly-once (idempotent) |
| `wallet.*` | `ledger-service` | 6 consumers | Exactly-once (idempotent) |
| `wallet.*` | `aml-monitor` | 3 consumers | At-least-once |
| `fraud.*` | `model-training-pipeline` | 3 consumers | At-least-once |
| `kyc.*` | `wallet-service` | 3 consumers | At-least-once |
| `settlement.*` | `finance-dashboard` | 1 consumer | At-least-once |
| `aml.*` | `regulatory-reporting` | 1 consumer | Exactly-once |
