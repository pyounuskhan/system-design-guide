# E-Commerce Core Commerce — Event Catalog

## Event Bus: Apache Kafka

All domain events are published to Kafka topics with the following conventions:
- **Topic naming**: `{domain}.{entity}.{action}` (e.g., `catalog.product.updated`)
- **Key**: Entity ID (for partition ordering)
- **Format**: JSON with envelope
- **Retention**: 7 days default; 30 days for order events

## Event Envelope

Every event follows this envelope structure:

```json
{
  "event_id": "evt_abc123",
  "event_type": "order.created",
  "version": "1.0",
  "source": "checkout-service",
  "timestamp": "2026-03-22T10:30:00.000Z",
  "correlation_id": "req_xyz789",
  "partition_key": "ord_abc123",
  "data": { ... }
}
```

---

## Catalog Events

### Topic: `catalog.product.created`
```json
{
  "event_type": "catalog.product.created",
  "data": {
    "product_id": "prod_abc123",
    "seller_id": "sel_sm001",
    "title": "SoundMax Pro Wireless Headphones",
    "brand": "SoundMax",
    "category_id": "cat_headphones_001",
    "status": "pending_review",
    "skus": [
      {"sku_id": "sku_001", "sku_code": "SM-PRO-BLK", "base_price": 199.99}
    ]
  }
}
```
**Consumers**: Search Indexer, Analytics Pipeline, Content Moderation

### Topic: `catalog.product.updated`
```json
{
  "event_type": "catalog.product.updated",
  "data": {
    "product_id": "prod_abc123",
    "changed_fields": ["title", "description"],
    "previous_version": 2,
    "new_version": 3
  }
}
```
**Consumers**: Search Indexer, PDP Cache Invalidator

### Topic: `catalog.product.status_changed`
```json
{
  "event_type": "catalog.product.status_changed",
  "data": {
    "product_id": "prod_abc123",
    "previous_status": "pending_review",
    "new_status": "active",
    "reason": "auto_approved",
    "changed_by": "system"
  }
}
```
**Consumers**: Search Indexer (add/remove from index), Seller Notification

### Topic: `catalog.sku.price_changed`
```json
{
  "event_type": "catalog.sku.price_changed",
  "data": {
    "sku_id": "sku_001",
    "product_id": "prod_abc123",
    "previous_price": 199.99,
    "new_price": 179.99,
    "currency": "USD",
    "changed_by": "sel_sm001"
  }
}
```
**Consumers**: Pricing Engine Cache Invalidator, Price Tracking Analytics, Wishlist Price Alert

---

## Inventory Events

### Topic: `inventory.stock.reserved`
```json
{
  "event_type": "inventory.stock.reserved",
  "data": {
    "reservation_id": "rsv_xyz789",
    "sku_id": "sku_001",
    "warehouse_id": "wh_east",
    "quantity": 2,
    "available_after": 340,
    "checkout_session_id": "cs_abc123",
    "expires_at": "2026-03-22T10:45:00Z"
  }
}
```
**Consumers**: PDP Availability Cache, Analytics

### Topic: `inventory.stock.committed`
```json
{
  "event_type": "inventory.stock.committed",
  "data": {
    "reservation_id": "rsv_xyz789",
    "sku_id": "sku_001",
    "warehouse_id": "wh_east",
    "quantity": 2,
    "order_id": "ord_abc123"
  }
}
```
**Consumers**: Analytics, Warehouse Management

### Topic: `inventory.stock.released`
```json
{
  "event_type": "inventory.stock.released",
  "data": {
    "reservation_id": "rsv_xyz789",
    "sku_id": "sku_001",
    "warehouse_id": "wh_east",
    "quantity": 2,
    "available_after": 342,
    "reason": "payment_failed"
  }
}
```
**Consumers**: PDP Availability Cache, Analytics

### Topic: `inventory.stock.restocked`
```json
{
  "event_type": "inventory.stock.restocked",
  "data": {
    "sku_id": "sku_001",
    "warehouse_id": "wh_east",
    "quantity_added": 500,
    "total_after": 842,
    "purchase_order_id": "po_12345"
  }
}
```
**Consumers**: PDP Availability Cache, Pre-order Notification, Analytics

### Topic: `inventory.stock.low`
```json
{
  "event_type": "inventory.stock.low",
  "data": {
    "sku_id": "sku_001",
    "warehouse_id": "wh_east",
    "available": 8,
    "reorder_point": 10
  }
}
```
**Consumers**: Seller Notification, Procurement Alert, PDP ("Only 8 left!")

---

## Order Events

### Topic: `order.created`
```json
{
  "event_type": "order.created",
  "data": {
    "order_id": "ord_abc123",
    "buyer_id": "usr_xyz",
    "total_amount": 324.73,
    "currency": "USD",
    "item_count": 2,
    "items": [
      {"sku_id": "sku_001", "seller_id": "sel_sm001", "quantity": 2, "unit_price": 149.99}
    ],
    "shipping_address": {"country": "US", "state": "CA", "city": "San Francisco"},
    "channel": "web"
  }
}
```
**Consumers**: Fulfillment, Notification, Analytics, Fraud Detection, Seller Dashboard

### Topic: `order.confirmed`
```json
{
  "event_type": "order.confirmed",
  "data": {
    "order_id": "ord_abc123",
    "payment_auth_id": "pi_auth_xyz",
    "confirmed_at": "2026-03-22T10:30:05Z"
  }
}
```
**Consumers**: Fulfillment (start picking), Seller Notification

### Topic: `order.item.shipped`
```json
{
  "event_type": "order.item.shipped",
  "data": {
    "order_id": "ord_abc123",
    "item_id": "oi_001",
    "sku_id": "sku_001",
    "tracking_number": "1Z999AA10123456784",
    "carrier": "UPS",
    "warehouse_id": "wh_east",
    "shipped_at": "2026-03-23T14:00:00Z",
    "estimated_delivery": "2026-03-25"
  }
}
```
**Consumers**: Notification (shipping email), Payment (trigger capture), Analytics, Buyer Tracking

### Topic: `order.delivered`
```json
{
  "event_type": "order.delivered",
  "data": {
    "order_id": "ord_abc123",
    "item_id": "oi_001",
    "delivered_at": "2026-03-25T10:30:00Z",
    "proof_of_delivery": "POD_123456",
    "signed_by": "J. Doe"
  }
}
```
**Consumers**: Notification, Finance (start settlement timer), Review Request Scheduler

### Topic: `order.cancelled`
```json
{
  "event_type": "order.cancelled",
  "data": {
    "order_id": "ord_abc123",
    "cancelled_by": "buyer",
    "reason": "changed_mind",
    "refund_amount": 324.73,
    "cancelled_at": "2026-03-22T11:00:00Z"
  }
}
```
**Consumers**: Inventory (release), Payment (void auth or refund), Notification, Analytics

---

## Return Events

### Topic: `return.requested`
```json
{
  "event_type": "return.requested",
  "data": {
    "return_id": "ret_abc123",
    "order_id": "ord_abc123",
    "buyer_id": "usr_xyz",
    "items": [
      {"sku_id": "sku_001", "quantity": 1, "reason_code": "defective"}
    ]
  }
}
```
**Consumers**: Return Approval Engine, Seller Notification, Fraud Detection

### Topic: `return.approved`
```json
{
  "event_type": "return.approved",
  "data": {
    "return_id": "ret_abc123",
    "approved_method": "auto",
    "return_label_url": "https://returns.example.com/label/ret_abc123.pdf"
  }
}
```
**Consumers**: Notification (send label to buyer)

### Topic: `return.item.received`
```json
{
  "event_type": "return.item.received",
  "data": {
    "return_id": "ret_abc123",
    "sku_id": "sku_001",
    "quantity": 1,
    "condition": "defective_confirmed",
    "warehouse_id": "wh_east"
  }
}
```
**Consumers**: Refund Processor, Inventory (restock decision)

### Topic: `refund.completed`
```json
{
  "event_type": "refund.completed",
  "data": {
    "refund_id": "ref_xyz789",
    "return_id": "ret_abc123",
    "order_id": "ord_abc123",
    "amount": 149.99,
    "currency": "USD",
    "method": "original_payment",
    "psp_refund_id": "re_stripe_abc"
  }
}
```
**Consumers**: Notification (refund confirmation email), Finance, Analytics

---

## Checkout Events

### Topic: `checkout.session.created`
```json
{
  "event_type": "checkout.session.created",
  "data": {
    "session_id": "cs_abc123",
    "buyer_id": "usr_xyz",
    "item_count": 2,
    "subtotal": 299.98
  }
}
```
**Consumers**: Analytics (funnel tracking)

### Topic: `checkout.session.abandoned`
```json
{
  "event_type": "checkout.session.abandoned",
  "data": {
    "session_id": "cs_abc123",
    "buyer_id": "usr_xyz",
    "last_step": "payment_pending",
    "abandoned_at": "2026-03-22T11:00:00Z",
    "cart_value": 299.98
  }
}
```
**Consumers**: Cart Recovery Notification (delayed), Analytics

---

## Cart Events

### Topic: `cart.item.added`
```json
{
  "event_type": "cart.item.added",
  "data": {
    "buyer_id": "usr_xyz",
    "sku_id": "sku_001",
    "product_id": "prod_abc123",
    "quantity": 2,
    "unit_price": 149.99
  }
}
```
**Consumers**: Analytics (conversion funnel), Recommendation Engine

### Topic: `cart.abandoned`
```json
{
  "event_type": "cart.abandoned",
  "data": {
    "buyer_id": "usr_xyz",
    "item_count": 3,
    "cart_value": 329.97,
    "last_updated": "2026-03-21T10:00:00Z"
  }
}
```
**Consumers**: Notification Service (abandoned cart email after 24h)

---

## Consumer Group Configuration

| Topic | Consumer Group | Parallelism | Processing Guarantee |
|-------|---------------|-------------|---------------------|
| `order.*` | `fulfillment-service` | 12 consumers | At-least-once |
| `order.*` | `notification-service` | 6 consumers | At-least-once |
| `order.*` | `analytics-pipeline` | 12 consumers | At-least-once |
| `order.*` | `finance-service` | 3 consumers | Exactly-once (idempotent) |
| `catalog.*` | `search-indexer` | 12 consumers | At-least-once |
| `inventory.*` | `pdp-cache-updater` | 6 consumers | At-least-once |
| `return.*` | `refund-processor` | 3 consumers | Exactly-once (idempotent) |
| `cart.*` | `analytics-pipeline` | 6 consumers | At-least-once |
| `seller.*` | `settlement-service` | 3 consumers | Exactly-once (idempotent) |
| `seller.*` | `notification-service` | 3 consumers | At-least-once |
| `settlement.*` | `finance-service` | 3 consumers | Exactly-once (idempotent) |
| `loyalty.*` | `notification-service` | 3 consumers | At-least-once |
| `fulfillment.*` | `wms-service` | 6 consumers | At-least-once |
| `fulfillment.*` | `tracking-service` | 6 consumers | At-least-once |
| `tracking.*` | `notification-service` | 6 consumers | At-least-once |

---

## Marketplace Events

### Topic: `seller.onboarded`
```json
{
  "event_type": "seller.onboarded",
  "data": {
    "seller_id": "sel_sm001",
    "display_name": "SoundMax Official",
    "tier": "standard",
    "live_at": "2026-03-22T12:00:00Z"
  }
}
```
**Consumers**: Catalog Service (enable listings), Notification, Analytics

### Topic: `seller.suspended`
```json
{
  "event_type": "seller.suspended",
  "data": {
    "seller_id": "sel_sm001",
    "reason": "policy_violation",
    "violation_type": "counterfeit_claim",
    "suspended_at": "2026-03-22T15:00:00Z"
  }
}
```
**Consumers**: Catalog (delist products), Search Indexer (remove from search), Settlement (hold payouts)

### Topic: `settlement.cycle.completed`
```json
{
  "event_type": "settlement.cycle.completed",
  "data": {
    "cycle_id": "cyc_abc123",
    "seller_id": "sel_sm001",
    "net_payout": 9771.45,
    "currency": "USD",
    "items_settled": 245,
    "cycle_period": "2026-03-01 to 2026-03-07"
  }
}
```
**Consumers**: Notification (payout email to seller), Finance Reconciliation

### Topic: `settlement.payout.failed`
```json
{
  "event_type": "settlement.payout.failed",
  "data": {
    "cycle_id": "cyc_abc123",
    "seller_id": "sel_sm001",
    "amount": 9771.45,
    "failure_reason": "bank_account_invalid",
    "retry_count": 2
  }
}
```
**Consumers**: Notification (alert seller), Finance Team Alert

---

## Growth & Engagement Events

### Topic: `recommendation.impression`
```json
{
  "event_type": "recommendation.impression",
  "data": {
    "user_id": "usr_xyz",
    "surface": "homepage",
    "algorithm": "collaborative_filtering",
    "products_shown": ["prod_abc", "prod_def", "prod_ghi"],
    "request_id": "reco_req_123"
  }
}
```
**Consumers**: Analytics (CTR calculation), Model Training Pipeline

### Topic: `recommendation.click`
```json
{
  "event_type": "recommendation.click",
  "data": {
    "user_id": "usr_xyz",
    "product_id": "prod_abc",
    "surface": "homepage",
    "algorithm": "collaborative_filtering",
    "position": 3,
    "request_id": "reco_req_123"
  }
}
```
**Consumers**: Analytics, Feature Store (update user profile)

### Topic: `loyalty.points.earned`
```json
{
  "event_type": "loyalty.points.earned",
  "data": {
    "account_id": "loy_abc",
    "buyer_id": "usr_xyz",
    "points": 150,
    "reason": "order_purchase",
    "reference_id": "ord_xyz789",
    "balance_after": 4520,
    "tier": "gold"
  }
}
```
**Consumers**: Notification, Analytics

### Topic: `loyalty.tier.changed`
```json
{
  "event_type": "loyalty.tier.changed",
  "data": {
    "account_id": "loy_abc",
    "buyer_id": "usr_xyz",
    "previous_tier": "silver",
    "new_tier": "gold",
    "reason": "threshold_reached"
  }
}
```
**Consumers**: Notification (congratulations email), Personalization Engine (update user segment)

### Topic: `coupon.redeemed`
```json
{
  "event_type": "coupon.redeemed",
  "data": {
    "coupon_id": "cpn_summer25",
    "code": "SUMMER25",
    "buyer_id": "usr_xyz",
    "order_id": "ord_xyz789",
    "discount_amount": 25.00,
    "remaining_budget": 4975.00,
    "remaining_uses": 449
  }
}
```
**Consumers**: Analytics, Budget Monitoring (alert if budget < 10%)

### Topic: `wishlist.price_drop`
```json
{
  "event_type": "wishlist.price_drop",
  "data": {
    "buyer_id": "usr_xyz",
    "product_id": "prod_abc123",
    "old_price": 199.99,
    "new_price": 149.99,
    "drop_percentage": 25
  }
}
```
**Consumers**: Notification Service (price drop alert email/push)

---

## Logistics Events

### Topic: `fulfillment.allocated`
```json
{
  "event_type": "fulfillment.allocated",
  "data": {
    "order_id": "ord_abc123",
    "allocation_id": "alloc_xyz",
    "shipment_groups": [
      {"warehouse_id": "wh_east", "items": ["sku_001"], "carrier": "UPS"}
    ]
  }
}
```
**Consumers**: WMS (generate pick tasks), Tracking Service (create tracking entry)

### Topic: `wms.pick.completed`
```json
{
  "event_type": "wms.pick.completed",
  "data": {
    "order_id": "ord_abc123",
    "warehouse_id": "wh_east",
    "items_picked": [{"sku_id": "sku_001", "quantity": 2, "bin_id": "bin_A12_03"}],
    "worker_id": "wkr_456",
    "picked_at": "2026-03-23T10:30:00Z"
  }
}
```
**Consumers**: OMS (update item status), Analytics

### Topic: `wms.packed`
```json
{
  "event_type": "wms.packed",
  "data": {
    "order_id": "ord_abc123",
    "warehouse_id": "wh_east",
    "package_weight_kg": 0.8,
    "tracking_number": "1Z999AA10123456784",
    "carrier": "UPS",
    "packed_at": "2026-03-23T11:00:00Z"
  }
}
```
**Consumers**: Tracking Service, OMS, Notification

### Topic: `tracking.status.updated`
```json
{
  "event_type": "tracking.status.updated",
  "data": {
    "order_id": "ord_abc123",
    "tracking_number": "1Z999AA10123456784",
    "carrier": "UPS",
    "previous_status": "in_transit",
    "new_status": "out_for_delivery",
    "location": {"city": "San Francisco", "state": "CA"},
    "estimated_delivery": "2026-03-25T15:00:00Z"
  }
}
```
**Consumers**: Notification (push: "Your package is out for delivery!"), OMS, Buyer Tracking API Cache

### Topic: `tracking.delivered`
```json
{
  "event_type": "tracking.delivered",
  "data": {
    "order_id": "ord_abc123",
    "tracking_number": "1Z999AA10123456784",
    "delivered_at": "2026-03-25T14:30:00Z",
    "signed_by": "Front Door",
    "proof_of_delivery": "photo_url"
  }
}
```
**Consumers**: OMS (mark delivered), Payment (trigger capture if not done), Notification, Review Request Scheduler, Settlement (start return window countdown)
