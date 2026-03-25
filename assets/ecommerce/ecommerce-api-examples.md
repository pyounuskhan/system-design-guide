# E-Commerce & Marketplaces — API Reference

## Product Catalog Service

### Create Product
```http
POST /api/v1/catalog/products
Authorization: Bearer {seller_token}
Content-Type: application/json
Idempotency-Key: {uuid}

{
  "title": "SoundMax Pro Wireless Headphones",
  "description": "Premium noise-cancelling wireless headphones with 40h battery",
  "brand": "SoundMax",
  "category_id": "cat_headphones_001",
  "attributes": {
    "connectivity": "Bluetooth 5.3",
    "noise_cancelling": true,
    "battery_hours": 40
  },
  "skus": [
    {
      "sku_code": "SM-PRO-BLK",
      "attributes": {"color": "Midnight Black"},
      "base_price": 199.99,
      "currency": "USD",
      "weight_grams": 250,
      "dimensions_cm": {"l": 20, "w": 18, "h": 8},
      "barcode": "0123456789012"
    },
    {
      "sku_code": "SM-PRO-WHT",
      "attributes": {"color": "Pearl White"},
      "base_price": 199.99,
      "currency": "USD",
      "weight_grams": 250
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "product_id": "prod_abc123",
  "slug": "soundmax-pro-wireless-headphones",
  "status": "pending_review",
  "skus": [
    {"sku_id": "sku_001", "sku_code": "SM-PRO-BLK"},
    {"sku_id": "sku_002", "sku_code": "SM-PRO-WHT"}
  ],
  "created_at": "2026-03-22T10:00:00Z"
}
```

### Search Products
```http
GET /api/v1/catalog/search?q=wireless+headphones&category=audio&minPrice=50&maxPrice=200&brand=SoundMax&sort=relevance&page=1&pageSize=20
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "product_id": "prod_abc123",
      "title": "SoundMax Pro Wireless Headphones",
      "brand": "SoundMax",
      "thumbnail_url": "https://cdn.example.com/img/prod_abc123_thumb.jpg",
      "base_price": 199.99,
      "sale_price": 149.99,
      "currency": "USD",
      "rating": 4.5,
      "review_count": 2341,
      "in_stock": true
    }
  ],
  "facets": {
    "brand": [{"value": "SoundMax", "count": 45}],
    "price_range": [{"min": 100, "max": 200, "count": 85}],
    "rating": [{"value": "4+", "count": 200}]
  },
  "total": 892,
  "page": 1,
  "page_size": 20,
  "has_next": true
}
```

### Update Product
```http
PUT /api/v1/catalog/products/prod_abc123
Authorization: Bearer {seller_token}

{
  "title": "SoundMax Pro Wireless Headphones (2026 Edition)",
  "description": "Updated premium noise-cancelling wireless headphones"
}
```

---

## Product Detail Page (PDP)

### Get PDP
```http
GET /api/v1/pdp/prod_abc123?locale=en-US&userId=usr_xyz
```

**Response (200 OK):**
```json
{
  "product": {
    "product_id": "prod_abc123",
    "title": "SoundMax Pro Wireless Headphones",
    "description": "Premium noise-cancelling...",
    "brand": "SoundMax",
    "images": [
      {"url": "https://cdn.example.com/img/prod_abc123_1.jpg", "alt": "Front view"},
      {"url": "https://cdn.example.com/img/prod_abc123_2.jpg", "alt": "Side view"}
    ],
    "variants": [
      {"sku_id": "sku_001", "color": "Midnight Black", "in_stock": true},
      {"sku_id": "sku_002", "color": "Pearl White", "in_stock": false}
    ],
    "attributes": {"connectivity": "Bluetooth 5.3", "noise_cancelling": true},
    "category_breadcrumb": ["Electronics", "Audio", "Headphones"]
  },
  "pricing": {
    "list_price": 199.99,
    "sale_price": 149.99,
    "discount_percent": 25,
    "currency": "USD",
    "promotion_label": "Summer Sale"
  },
  "availability": {
    "in_stock": true,
    "quantity_display": "In Stock",
    "low_stock": false,
    "fulfillment_type": "shipped"
  },
  "delivery": {
    "estimated_date": "2026-03-25",
    "options": [
      {"method": "Standard", "price": 0, "days_range": "3-5"},
      {"method": "Express", "price": 9.99, "days_range": "1-2"}
    ]
  },
  "reviews_summary": {
    "average_rating": 4.5,
    "total_reviews": 2341,
    "distribution": {"5": 1200, "4": 700, "3": 250, "2": 120, "1": 71}
  },
  "seller": {
    "seller_id": "sel_sm001",
    "name": "SoundMax Official",
    "rating": 4.8
  },
  "recommendations": [
    {"product_id": "prod_def456", "title": "SoundMax Pro Case", "price": 29.99, "thumbnail": "..."}
  ]
}
```

---

## Pricing Engine

### Evaluate Price
```http
POST /api/v1/pricing/evaluate
Authorization: Bearer {internal_service_token}

{
  "items": [
    {"sku_id": "sku_001", "quantity": 2},
    {"sku_id": "sku_003", "quantity": 1}
  ],
  "buyer_id": "usr_xyz",
  "coupon_code": "SUMMER25",
  "locale": "en-US",
  "channel": "web"
}
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "sku_id": "sku_001",
      "quantity": 2,
      "unit_base_price": 199.99,
      "unit_final_price": 149.99,
      "line_total": 299.98,
      "applied_discounts": [
        {"type": "platform_promotion", "id": "promo_summer", "name": "Summer Sale 25%", "amount": -50.00}
      ]
    },
    {
      "sku_id": "sku_003",
      "quantity": 1,
      "unit_base_price": 29.99,
      "unit_final_price": 29.99,
      "line_total": 29.99,
      "applied_discounts": []
    }
  ],
  "subtotal": 329.97,
  "coupon_discount": -25.00,
  "coupon_applied": {"code": "SUMMER25", "name": "$25 off orders over $100"},
  "total_before_tax": 304.97,
  "calculation_id": "calc_789xyz"
}
```

---

## Inventory Service

### Check Availability
```http
GET /internal/inventory/availability/sku_001?warehouse_ids=wh_east,wh_west
Authorization: Bearer {internal_service_token}
```

**Response (200 OK):**
```json
{
  "sku_id": "sku_001",
  "warehouses": [
    {"warehouse_id": "wh_east", "available": 342, "reserved": 28},
    {"warehouse_id": "wh_west", "available": 156, "reserved": 12}
  ],
  "total_available": 498,
  "checked_at": "2026-03-22T10:30:00Z"
}
```

### Reserve Inventory
```http
POST /internal/inventory/reserve
Authorization: Bearer {internal_service_token}
Idempotency-Key: checkout_sess_abc123_sku_001

{
  "sku_id": "sku_001",
  "warehouse_id": "wh_east",
  "quantity": 2,
  "ttl_minutes": 15,
  "reference": "checkout_sess_abc123"
}
```

**Response (200 OK):**
```json
{
  "reservation_id": "rsv_xyz789",
  "sku_id": "sku_001",
  "warehouse_id": "wh_east",
  "quantity": 2,
  "expires_at": "2026-03-22T10:45:00Z",
  "status": "active"
}
```

**Response (409 Conflict — Insufficient Stock):**
```json
{
  "error": "INSUFFICIENT_STOCK",
  "message": "Only 1 unit available",
  "available_quantity": 1,
  "sku_id": "sku_001",
  "warehouse_id": "wh_east"
}
```

### Commit Reservation
```http
POST /internal/inventory/commit
Authorization: Bearer {internal_service_token}

{
  "reservation_id": "rsv_xyz789",
  "order_id": "ord_abc123"
}
```

### Release Reservation
```http
POST /internal/inventory/release
Authorization: Bearer {internal_service_token}

{
  "reservation_id": "rsv_xyz789",
  "reason": "payment_failed"
}
```

---

## Cart Service

### Add Item to Cart
```http
POST /api/v1/cart/items
Authorization: Bearer {buyer_token}
Idempotency-Key: {uuid}

{
  "sku_id": "sku_001",
  "quantity": 2
}
```

**Response (200 OK):**
```json
{
  "cart": {
    "items": [
      {
        "sku_id": "sku_001",
        "product_id": "prod_abc123",
        "title": "SoundMax Pro Wireless Headphones (Black)",
        "quantity": 2,
        "unit_price": 149.99,
        "line_total": 299.98,
        "in_stock": true,
        "image_url": "https://cdn.example.com/img/prod_abc123_thumb.jpg"
      }
    ],
    "item_count": 2,
    "subtotal": 299.98,
    "updated_at": "2026-03-22T10:30:00Z"
  }
}
```

### Get Cart
```http
GET /api/v1/cart
Authorization: Bearer {buyer_token}
```

### Update Item Quantity
```http
PUT /api/v1/cart/items/sku_001
Authorization: Bearer {buyer_token}

{
  "quantity": 3
}
```

### Remove Item
```http
DELETE /api/v1/cart/items/sku_001
Authorization: Bearer {buyer_token}
```

### Merge Guest Cart
```http
POST /api/v1/cart/merge
Authorization: Bearer {buyer_token}

{
  "guest_cart_id": "guest_cart_anon_12345"
}
```

---

## Checkout Service

### Create Checkout Session
```http
POST /api/v1/checkout/sessions
Authorization: Bearer {buyer_token}

{
  "shipping_address": {
    "line1": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94102",
    "country": "US"
  },
  "shipping_method": "standard"
}
```

**Response (200 OK):**
```json
{
  "checkout_session_id": "cs_abc123",
  "items": [...],
  "subtotal": 299.98,
  "shipping": 0.00,
  "tax": 24.75,
  "total": 324.73,
  "currency": "USD",
  "shipping_estimate": "March 25-27, 2026",
  "payment_methods_available": ["card", "paypal", "apple_pay"],
  "expires_at": "2026-03-22T11:00:00Z"
}
```

### Confirm Checkout (Place Order)
```http
POST /api/v1/checkout/confirm
Authorization: Bearer {buyer_token}
Idempotency-Key: {uuid}

{
  "checkout_session_id": "cs_abc123",
  "payment_method": {
    "type": "card",
    "token": "pm_card_visa_4242"
  }
}
```

**Response (201 Created):**
```json
{
  "order_id": "ord_xyz789",
  "status": "confirmed",
  "total": 324.73,
  "currency": "USD",
  "estimated_delivery": "March 25-27, 2026",
  "confirmation_email_sent": true
}
```

**Response (402 Payment Required):**
```json
{
  "error": "PAYMENT_DECLINED",
  "message": "Your card was declined. Please try a different payment method.",
  "checkout_session_id": "cs_abc123"
}
```

---

## Order Management

### List Orders
```http
GET /api/v1/orders?page=1&pageSize=10&status=shipped
Authorization: Bearer {buyer_token}
```

### Get Order Detail
```http
GET /api/v1/orders/ord_xyz789
Authorization: Bearer {buyer_token}
```

**Response (200 OK):**
```json
{
  "order_id": "ord_xyz789",
  "status": "shipped",
  "items": [
    {
      "item_id": "oi_001",
      "sku_id": "sku_001",
      "title": "SoundMax Pro Wireless Headphones (Black)",
      "quantity": 2,
      "unit_price": 149.99,
      "line_total": 299.98,
      "status": "shipped",
      "tracking_number": "1Z999AA10123456784",
      "carrier": "UPS",
      "shipped_at": "2026-03-23T14:00:00Z"
    }
  ],
  "subtotal": 299.98,
  "tax": 24.75,
  "shipping": 0.00,
  "total": 324.73,
  "shipping_address": {...},
  "created_at": "2026-03-22T10:30:00Z",
  "timeline": [
    {"event": "order_placed", "at": "2026-03-22T10:30:00Z"},
    {"event": "payment_confirmed", "at": "2026-03-22T10:30:05Z"},
    {"event": "shipped", "at": "2026-03-23T14:00:00Z"}
  ]
}
```

### Cancel Order
```http
POST /api/v1/orders/ord_xyz789/cancel
Authorization: Bearer {buyer_token}

{
  "reason": "changed_mind"
}
```

---

## Returns Service

### Create Return Request
```http
POST /api/v1/returns
Authorization: Bearer {buyer_token}
Idempotency-Key: {uuid}

{
  "order_id": "ord_xyz789",
  "items": [
    {
      "order_item_id": "oi_001",
      "quantity": 1,
      "reason_code": "defective",
      "reason_detail": "Left earpiece stopped working after 2 days"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "return_id": "ret_abc123",
  "status": "approved",
  "return_label_url": "https://returns.example.com/label/ret_abc123.pdf",
  "estimated_refund": 149.99,
  "instructions": "Pack the item securely and drop off at any UPS location within 14 days."
}
```

### Get Return Status
```http
GET /api/v1/returns/ret_abc123
Authorization: Bearer {buyer_token}
```

**Response (200 OK):**
```json
{
  "return_id": "ret_abc123",
  "order_id": "ord_xyz789",
  "status": "received",
  "items": [
    {
      "sku_id": "sku_001",
      "quantity": 1,
      "reason_code": "defective",
      "condition": "defective_confirmed",
      "refund_amount": 149.99
    }
  ],
  "refund": {
    "amount": 149.99,
    "method": "original_payment",
    "status": "processing",
    "estimated_completion": "2026-04-01"
  },
  "timeline": [
    {"event": "return_requested", "at": "2026-03-25T10:00:00Z"},
    {"event": "return_approved", "at": "2026-03-25T10:00:05Z"},
    {"event": "item_received", "at": "2026-03-28T09:00:00Z"},
    {"event": "refund_initiated", "at": "2026-03-28T09:15:00Z"}
  ]
}
```

---

## Error Response Format (Standard)

All API errors follow this format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error description",
  "details": {
    "field": "additional_context"
  },
  "request_id": "req_abc123",
  "timestamp": "2026-03-22T10:30:00Z"
}
```

| HTTP Status | Error Code | Meaning |
|-------------|-----------|---------|
| 400 | `INVALID_REQUEST` | Malformed request body |
| 401 | `UNAUTHORIZED` | Missing or invalid auth token |
| 403 | `FORBIDDEN` | Valid token but insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | State conflict (e.g., insufficient stock, duplicate) |
| 422 | `VALIDATION_ERROR` | Business logic validation failure |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Downstream dependency failure |

---

## Marketplace APIs

### Seller Onboarding

#### Apply as Seller
```http
POST /api/v1/sellers/apply
Content-Type: application/json

{
  "legal_name": "SoundMax Electronics LLC",
  "display_name": "SoundMax Official",
  "email": "seller@soundmax.com",
  "phone": "+1-415-555-0123",
  "country": "US",
  "business_type": "company",
  "tax_id": "12-3456789",
  "category_preferences": ["electronics", "audio"]
}
```

**Response (201 Created):**
```json
{
  "seller_id": "sel_sm001",
  "status": "application_submitted",
  "next_step": "Upload KYC documents",
  "documents_required": ["business_license", "tax_certificate", "identity_proof"],
  "onboarding_url": "https://seller.example.com/onboarding/sel_sm001"
}
```

#### Upload KYC Document
```http
POST /api/v1/sellers/sel_sm001/documents
Content-Type: multipart/form-data

doc_type: business_license
file: [binary]
```

### Settlement

#### Get Settlement Summary
```http
GET /api/v1/sellers/sel_sm001/settlements?cycle=2026-03
Authorization: Bearer {seller_token}
```

**Response (200 OK):**
```json
{
  "cycle": "2026-03-01 to 2026-03-07",
  "total_sales": 12450.00,
  "total_commission": -1867.50,
  "total_psp_fees": -361.05,
  "total_returns": -450.00,
  "net_payout": 9771.45,
  "currency": "USD",
  "payout_status": "completed",
  "paid_at": "2026-03-10T06:00:00Z",
  "ledger_entries": 245
}
```

### Seller Dashboard Analytics
```http
GET /api/v1/sellers/sel_sm001/analytics/daily?from=2026-03-01&to=2026-03-22
Authorization: Bearer {seller_token}
```

**Response (200 OK):**
```json
{
  "daily_metrics": [
    {
      "date": "2026-03-22",
      "orders": 45,
      "items_sold": 127,
      "gmv": 8500.00,
      "returns": 3,
      "avg_rating": 4.6,
      "cancellation_rate": 0.02
    }
  ]
}
```

### Vendor Rating
```http
GET /api/v1/sellers/sel_sm001/rating
```

**Response (200 OK):**
```json
{
  "seller_id": "sel_sm001",
  "composite_score": 4.6,
  "tier": "premium",
  "breakdown": {
    "buyer_rating_avg": 4.7,
    "on_time_delivery_rate": 0.96,
    "cancellation_rate": 0.02,
    "return_rate": 0.05,
    "response_time_hours": 2.3
  },
  "total_reviews": 3421,
  "review_period": "last_90_days"
}
```

---

## Growth & Engagement APIs

### Recommendations
```http
GET /api/v1/recommendations/home?user_id=usr_xyz&limit=20
Authorization: Bearer {buyer_token}
```

**Response (200 OK):**
```json
{
  "sections": [
    {
      "title": "Recommended for You",
      "algorithm": "collaborative_filtering",
      "products": [
        {"product_id": "prod_abc", "title": "SoundMax Pro Case", "price": 29.99, "score": 0.92}
      ]
    },
    {
      "title": "Based on Your Recent Views",
      "algorithm": "session_based",
      "products": [...]
    },
    {
      "title": "Trending in Electronics",
      "algorithm": "popularity",
      "products": [...]
    }
  ],
  "request_id": "reco_req_123"
}
```

### Wishlist
```http
POST /api/v1/wishlists/default/items
Authorization: Bearer {buyer_token}

{
  "product_id": "prod_abc123",
  "sku_id": "sku_001",
  "notify_price_drop": true
}
```

**Response (201 Created):**
```json
{
  "item_id": "wl_item_789",
  "product_id": "prod_abc123",
  "current_price": 149.99,
  "added_at": "2026-03-22T10:00:00Z"
}
```

### Loyalty Account
```http
GET /api/v1/loyalty/account
Authorization: Bearer {buyer_token}
```

**Response (200 OK):**
```json
{
  "account_id": "loy_abc",
  "points_balance": 4520,
  "lifetime_points": 12350,
  "tier": "gold",
  "tier_expires_at": "2027-01-01",
  "points_expiring_soon": {
    "amount": 500,
    "expires_at": "2026-04-22"
  },
  "earning_rate": "1.5x (Gold bonus)",
  "recent_transactions": [
    {"type": "earn", "points": 150, "description": "Order #ord_xyz", "date": "2026-03-20"},
    {"type": "redeem", "points": -500, "description": "Discount on Order #ord_abc", "date": "2026-03-15"}
  ]
}
```

### Redeem Points
```http
POST /api/v1/loyalty/redeem
Authorization: Bearer {buyer_token}

{
  "points": 1000,
  "checkout_session_id": "cs_abc123"
}
```

**Response (200 OK):**
```json
{
  "redemption_id": "red_xyz",
  "points_redeemed": 1000,
  "discount_amount": 10.00,
  "remaining_balance": 3520
}
```

### Coupon Validation
```http
POST /api/v1/coupons/validate
Authorization: Bearer {buyer_token}

{
  "code": "SUMMER25",
  "cart_total": 299.98,
  "items": [{"sku_id": "sku_001", "category": "electronics", "quantity": 2}]
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "discount_amount": 25.00,
  "discount_type": "fixed",
  "promotion_name": "$25 off orders over $100",
  "remaining_uses": 450,
  "expires_at": "2026-04-01T00:00:00Z"
}
```

---

## Logistics APIs

### Fulfillment Allocation
```http
POST /internal/fulfillment/allocate
Authorization: Bearer {internal_token}

{
  "order_id": "ord_abc123",
  "items": [
    {"sku_id": "sku_001", "quantity": 2},
    {"sku_id": "sku_003", "quantity": 1}
  ],
  "shipping_address": {"country": "US", "state": "CA", "zip": "94102"},
  "delivery_sla": "standard"
}
```

**Response (200 OK):**
```json
{
  "allocation_id": "alloc_xyz",
  "shipment_groups": [
    {
      "warehouse_id": "wh_east",
      "items": [{"sku_id": "sku_001", "quantity": 2}],
      "carrier": "UPS",
      "estimated_ship_date": "2026-03-23"
    },
    {
      "warehouse_id": "wh_west",
      "items": [{"sku_id": "sku_003", "quantity": 1}],
      "carrier": "FedEx",
      "estimated_ship_date": "2026-03-23"
    }
  ],
  "split_reason": "multi_warehouse_availability"
}
```

### Delivery Tracking
```http
GET /api/v1/tracking/ord_abc123
Authorization: Bearer {buyer_token}
```

**Response (200 OK):**
```json
{
  "order_id": "ord_abc123",
  "shipments": [
    {
      "tracking_number": "1Z999AA10123456784",
      "carrier": "UPS",
      "status": "in_transit",
      "estimated_delivery": "2026-03-25",
      "events": [
        {"status": "label_created", "timestamp": "2026-03-23T08:00:00Z", "location": "New York, NY"},
        {"status": "picked_up", "timestamp": "2026-03-23T14:00:00Z", "location": "New York, NY"},
        {"status": "in_transit", "timestamp": "2026-03-24T02:00:00Z", "location": "Memphis, TN"}
      ]
    }
  ]
}
```

### WMS Pick Task Update
```http
PATCH /internal/wms/pick-tasks/{taskId}
Authorization: Bearer {warehouse_worker_token}

{
  "status": "picked",
  "picked_quantity": 2,
  "bin_id": "bin_A12_03"
}
```

### Route Optimization Request
```http
POST /internal/routing/optimize
Authorization: Bearer {internal_token}

{
  "depot_id": "wh_east",
  "deliveries": [
    {"order_id": "ord_001", "address": {"lat": 37.78, "lng": -122.41}, "time_window": {"start": "14:00", "end": "16:00"}, "weight_kg": 2.5},
    {"order_id": "ord_002", "address": {"lat": 37.76, "lng": -122.43}, "time_window": null, "weight_kg": 1.0}
  ],
  "vehicles": [
    {"id": "van_01", "capacity_kg": 500, "max_stops": 50}
  ],
  "optimize_for": "minimize_distance"
}
```

**Response (200 OK):**
```json
{
  "routes": [
    {
      "vehicle_id": "van_01",
      "stops": [
        {"order_id": "ord_002", "sequence": 1, "eta": "13:45"},
        {"order_id": "ord_001", "sequence": 2, "eta": "14:15"}
      ],
      "total_distance_km": 12.4,
      "total_time_minutes": 45
    }
  ],
  "computation_time_ms": 2340,
  "unassigned": []
}
```
