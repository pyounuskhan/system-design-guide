# E-Commerce Core Commerce — Database Schema Reference

## PostgreSQL: Catalog Database

```sql
-- ===========================================
-- CATALOG SERVICE SCHEMA
-- ===========================================

-- Sellers
CREATE TABLE sellers (
    seller_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,
    email           TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('pending', 'active', 'suspended', 'deactivated')),
    kyc_verified    BOOLEAN DEFAULT false,
    commission_rate DECIMAL(5,4) DEFAULT 0.15,  -- 15% default
    country         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Hierarchical categories
CREATE TABLE categories (
    category_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id       UUID REFERENCES categories(category_id),
    name            TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,
    level           INT NOT NULL,                 -- 0=root, 1=top, 2=sub, 3=leaf
    path            TEXT NOT NULL,                 -- "electronics.audio.headphones"
    attribute_schema JSONB,                        -- required/optional attributes for this category
    is_active       BOOLEAN DEFAULT true,
    sort_order      INT DEFAULT 0
);
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_path ON categories USING GIN (path gin_trgm_ops);

-- Products
CREATE TABLE products (
    product_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id       UUID NOT NULL REFERENCES sellers(seller_id),
    title           TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,
    description     TEXT,
    brand           TEXT,
    category_id     UUID REFERENCES categories(category_id),
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft', 'pending_review', 'active', 'inactive', 'suspended')),
    tags            TEXT[],
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    version         INT NOT NULL DEFAULT 1
);
CREATE INDEX idx_products_seller ON products(seller_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_status ON products(status) WHERE status = 'active';
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_tags ON products USING GIN (tags);

-- SKU-level variants
CREATE TABLE skus (
    sku_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id      UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    sku_code        TEXT UNIQUE NOT NULL,
    attributes      JSONB NOT NULL DEFAULT '{}',
    base_price      DECIMAL(12,2) NOT NULL CHECK (base_price >= 0),
    currency        TEXT NOT NULL DEFAULT 'USD',
    cost_price      DECIMAL(12,2),                -- COGS for margin calculation
    weight_grams    INT CHECK (weight_grams > 0),
    dimensions_cm   JSONB,
    barcode         TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'inactive', 'discontinued')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_skus_product ON skus(product_id);
CREATE INDEX idx_skus_code ON skus(sku_code);

-- Product media
CREATE TABLE product_media (
    media_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id      UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    media_type      TEXT NOT NULL CHECK (media_type IN ('image', 'video', '360_view', 'size_chart')),
    url             TEXT NOT NULL,
    thumbnail_url   TEXT,
    alt_text        TEXT,
    sort_order      INT NOT NULL DEFAULT 0,
    is_primary      BOOLEAN DEFAULT false,
    width_px        INT,
    height_px       INT,
    file_size_bytes BIGINT
);
CREATE INDEX idx_media_product ON product_media(product_id);
```

## PostgreSQL: Inventory Database

```sql
-- ===========================================
-- INVENTORY SERVICE SCHEMA
-- ===========================================

-- Warehouses
CREATE TABLE warehouses (
    warehouse_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    code            TEXT UNIQUE NOT NULL,
    region          TEXT NOT NULL,
    address         JSONB NOT NULL,
    type            TEXT NOT NULL CHECK (type IN ('fulfillment_center', 'store', 'dropship')),
    is_active       BOOLEAN DEFAULT true,
    capacity        INT
);

-- Inventory per SKU per warehouse
CREATE TABLE inventory (
    inventory_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id          UUID NOT NULL,
    warehouse_id    UUID NOT NULL REFERENCES warehouses(warehouse_id),
    total_quantity  INT NOT NULL DEFAULT 0 CHECK (total_quantity >= 0),
    reserved        INT NOT NULL DEFAULT 0 CHECK (reserved >= 0),
    available       INT GENERATED ALWAYS AS (total_quantity - reserved) STORED,
    reorder_point   INT DEFAULT 10,
    max_quantity    INT DEFAULT 10000,
    version         INT NOT NULL DEFAULT 1,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(sku_id, warehouse_id),
    CHECK (total_quantity >= reserved)
);
CREATE INDEX idx_inventory_sku ON inventory(sku_id);
CREATE INDEX idx_inventory_low_stock ON inventory(sku_id) WHERE (total_quantity - reserved) <= 10;

-- Reservations
CREATE TABLE reservations (
    reservation_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id          UUID NOT NULL,
    warehouse_id    UUID NOT NULL,
    order_id        UUID,
    quantity        INT NOT NULL CHECK (quantity > 0),
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'committed', 'released', 'expired')),
    expires_at      TIMESTAMPTZ NOT NULL,
    idempotency_key TEXT UNIQUE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_reservations_expires ON reservations(expires_at) WHERE status = 'active';
CREATE INDEX idx_reservations_sku ON reservations(sku_id, warehouse_id);
CREATE INDEX idx_reservations_order ON reservations(order_id) WHERE order_id IS NOT NULL;

-- Inventory audit ledger (append-only)
CREATE TABLE inventory_ledger (
    ledger_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id          UUID NOT NULL,
    warehouse_id    UUID NOT NULL,
    operation       TEXT NOT NULL CHECK (operation IN (
        'reserve', 'commit', 'release', 'restock', 'adjustment', 'reconcile', 'write_off'
    )),
    quantity_delta  INT NOT NULL,
    balance_after   INT NOT NULL,
    reference_id    UUID,
    reference_type  TEXT,
    actor           TEXT NOT NULL,
    reason          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_ledger_sku ON inventory_ledger(sku_id, created_at);
CREATE INDEX idx_ledger_reference ON inventory_ledger(reference_id);
```

## PostgreSQL: Order Database

```sql
-- ===========================================
-- ORDER MANAGEMENT SCHEMA
-- ===========================================

-- Orders (partitioned by month)
CREATE TABLE orders (
    order_id        UUID NOT NULL,
    buyer_id        UUID NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'confirmed', 'processing',
                    'partially_shipped', 'shipped', 'delivered', 'completed',
                    'cancelled', 'return_requested')),
    subtotal        DECIMAL(12,2) NOT NULL,
    tax_amount      DECIMAL(12,2) NOT NULL DEFAULT 0,
    shipping_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    total_amount    DECIMAL(12,2) NOT NULL,
    currency        TEXT NOT NULL DEFAULT 'USD',
    shipping_address JSONB NOT NULL,
    billing_address JSONB NOT NULL,
    payment_method  JSONB NOT NULL,
    payment_auth_id TEXT,
    payment_capture_id TEXT,
    coupon_code     TEXT,
    channel         TEXT DEFAULT 'web',
    locale          TEXT DEFAULT 'en-US',
    ip_address      INET,
    idempotency_key TEXT UNIQUE NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    version         INT NOT NULL DEFAULT 1,
    PRIMARY KEY (order_id, created_at)
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE orders_2026_01 PARTITION OF orders FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE orders_2026_02 PARTITION OF orders FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE orders_2026_03 PARTITION OF orders FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

CREATE INDEX idx_orders_buyer ON orders(buyer_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status);

-- Order items
CREATE TABLE order_items (
    item_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID NOT NULL,
    sku_id          UUID NOT NULL,
    product_id      UUID NOT NULL,
    seller_id       UUID NOT NULL,
    title           TEXT NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(12,2) NOT NULL,
    line_total      DECIMAL(12,2) NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'processing', 'shipped', 'delivered',
                    'cancelled', 'return_requested', 'returned')),
    warehouse_id    UUID,
    tracking_number TEXT,
    carrier         TEXT,
    shipped_at      TIMESTAMPTZ,
    delivered_at    TIMESTAMPTZ
);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_seller ON order_items(seller_id, status);
CREATE INDEX idx_order_items_sku ON order_items(sku_id);

-- Order event log (append-only)
CREATE TABLE order_events (
    event_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID NOT NULL,
    event_type      TEXT NOT NULL,
    payload         JSONB NOT NULL DEFAULT '{}',
    actor           TEXT NOT NULL,
    actor_id        UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_order_events_order ON order_events(order_id, created_at);

-- Checkout sessions
CREATE TABLE checkout_sessions (
    session_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_id        UUID NOT NULL,
    cart_snapshot    JSONB NOT NULL,
    shipping_address JSONB,
    shipping_method TEXT,
    subtotal        DECIMAL(12,2),
    tax_amount      DECIMAL(12,2),
    shipping_amount DECIMAL(12,2),
    total_amount    DECIMAL(12,2),
    currency        TEXT DEFAULT 'USD',
    reservation_ids UUID[],
    status          TEXT DEFAULT 'created'
                    CHECK (status IN ('created', 'address_validated', 'shipping_selected',
                    'tax_calculated', 'payment_pending', 'payment_authorized',
                    'order_created', 'confirmed', 'expired', 'abandoned')),
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_checkout_buyer ON checkout_sessions(buyer_id);
CREATE INDEX idx_checkout_expires ON checkout_sessions(expires_at) WHERE status NOT IN ('confirmed', 'expired');

-- Checkout idempotency
CREATE TABLE checkout_idempotency (
    idempotency_key TEXT PRIMARY KEY,
    checkout_id     UUID NOT NULL,
    order_id        UUID,
    result          JSONB NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ NOT NULL
);
```

## PostgreSQL: Returns & Refunds

```sql
-- ===========================================
-- RETURNS & REFUNDS SCHEMA
-- ===========================================

CREATE TABLE returns (
    return_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID NOT NULL,
    buyer_id        UUID NOT NULL,
    status          TEXT NOT NULL DEFAULT 'requested'
                    CHECK (status IN ('requested', 'approved', 'denied',
                    'label_generated', 'in_transit', 'received',
                    'inspected', 'refund_initiated', 'refunded',
                    'partial_refund', 'rejected', 'closed')),
    return_type     TEXT NOT NULL DEFAULT 'return'
                    CHECK (return_type IN ('return', 'exchange', 'warranty')),
    return_label_url TEXT,
    carrier         TEXT,
    tracking_number TEXT,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_returns_order ON returns(order_id);
CREATE INDEX idx_returns_buyer ON returns(buyer_id);
CREATE INDEX idx_returns_status ON returns(status);

CREATE TABLE return_items (
    return_item_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    return_id       UUID NOT NULL REFERENCES returns(return_id),
    order_item_id   UUID NOT NULL,
    sku_id          UUID NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    reason_code     TEXT NOT NULL CHECK (reason_code IN (
        'defective', 'wrong_item', 'changed_mind', 'not_as_described',
        'arrived_late', 'damaged_in_shipping', 'missing_parts', 'other'
    )),
    reason_detail   TEXT,
    condition       TEXT CHECK (condition IN (
        'new', 'like_new', 'good', 'fair', 'defective', 'damaged', 'missing'
    )),
    refund_amount   DECIMAL(12,2),
    restock_action  TEXT CHECK (restock_action IN ('restock', 'write_off', 'vendor_return', 'donate'))
);
CREATE INDEX idx_return_items_return ON return_items(return_id);

CREATE TABLE refunds (
    refund_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    return_id       UUID REFERENCES returns(return_id),
    order_id        UUID NOT NULL,
    buyer_id        UUID NOT NULL,
    amount          DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    currency        TEXT NOT NULL,
    refund_method   TEXT NOT NULL CHECK (refund_method IN (
        'original_payment', 'store_credit', 'bank_transfer', 'gift_card'
    )),
    psp_refund_id   TEXT,
    breakdown       JSONB,  -- {"item_refund": 149.99, "tax_refund": 12.37, "shipping_refund": 0}
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'reversed')),
    idempotency_key TEXT UNIQUE NOT NULL,
    failure_reason  TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_refunds_return ON refunds(return_id);
CREATE INDEX idx_refunds_order ON refunds(order_id);
CREATE INDEX idx_refunds_status ON refunds(status) WHERE status IN ('pending', 'processing');
```

## PostgreSQL: Pricing Engine

```sql
-- ===========================================
-- PRICING ENGINE SCHEMA
-- ===========================================

CREATE TABLE promotions (
    promotion_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    description     TEXT,
    type            TEXT NOT NULL CHECK (type IN (
        'percentage_off', 'fixed_off', 'buy_x_get_y',
        'bundle', 'tiered_quantity', 'free_shipping',
        'spend_threshold', 'category_discount'
    )),
    scope           TEXT NOT NULL DEFAULT 'platform'
                    CHECK (scope IN ('platform', 'seller', 'category', 'product', 'sku')),
    rules           JSONB NOT NULL,
    discount_value  DECIMAL(12,2),
    discount_percent DECIMAL(5,2),
    max_discount    DECIMAL(12,2),
    min_order_value DECIMAL(12,2),
    start_at        TIMESTAMPTZ NOT NULL,
    end_at          TIMESTAMPTZ NOT NULL,
    budget_total    DECIMAL(12,2),
    budget_used     DECIMAL(12,2) DEFAULT 0,
    max_uses        INT,
    current_uses    INT DEFAULT 0,
    priority        INT NOT NULL DEFAULT 0,
    stackable       BOOLEAN DEFAULT false,
    status          TEXT DEFAULT 'active'
                    CHECK (status IN ('draft', 'scheduled', 'active', 'paused', 'expired', 'exhausted')),
    created_by      UUID NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_promotions_active ON promotions(start_at, end_at) WHERE status = 'active';
CREATE INDEX idx_promotions_scope ON promotions(scope, status);

CREATE TABLE coupons (
    coupon_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            TEXT UNIQUE NOT NULL,
    promotion_id    UUID NOT NULL REFERENCES promotions(promotion_id),
    max_uses        INT,
    current_uses    INT DEFAULT 0,
    max_uses_per_user INT DEFAULT 1,
    valid_from      TIMESTAMPTZ,
    valid_until     TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT true
);
CREATE INDEX idx_coupons_code ON coupons(code);

CREATE TABLE coupon_usage (
    usage_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coupon_id       UUID NOT NULL REFERENCES coupons(coupon_id),
    buyer_id        UUID NOT NULL,
    order_id        UUID NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL,
    used_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_coupon_usage_buyer ON coupon_usage(coupon_id, buyer_id);

CREATE TABLE price_calculations (
    calc_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id          UUID NOT NULL,
    buyer_id        UUID,
    base_price      DECIMAL(12,2) NOT NULL,
    final_price     DECIMAL(12,2) NOT NULL,
    applied_rules   JSONB NOT NULL,
    context         JSONB,
    calculated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Partitioned by date; retained for 90 days for analytics
CREATE INDEX idx_price_calc_sku ON price_calculations(sku_id, calculated_at);
```

## Redis: Cart Schema

```
# Cart key pattern: cart:{user_id} or cart:guest:{session_id}
# Type: Hash with JSON value

KEY: cart:usr_xyz123
VALUE: {
  "items": [...],
  "saved_for_later": [...],
  "coupon_code": "SUMMER25",
  "updated_at": "2026-03-22T11:15:00Z",
  "version": 7
}
TTL: 30 days (authenticated), 7 days (guest)

# Cart item count (for badge display)
KEY: cart_count:usr_xyz123
VALUE: 3
TTL: same as cart

# Active promotions cache
KEY: promotions:active
VALUE: [serialized list of active promotion rules]
TTL: 60 seconds

# Price cache per SKU
KEY: price:sku_001:web:en-US
VALUE: {"base": 199.99, "final": 149.99, "promo": "Summer Sale"}
TTL: 30 seconds

# Inventory display cache
KEY: inv:sku_001
VALUE: {"available": 342, "low_stock": false}
TTL: 10 seconds
```

## Elasticsearch: Product Index

```json
{
  "settings": {
    "number_of_shards": 10,
    "number_of_replicas": 2,
    "analysis": {
      "analyzer": {
        "product_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "synonym_filter", "stemmer"]
        }
      },
      "filter": {
        "synonym_filter": {
          "type": "synonym",
          "synonyms": ["headphone, earphone, headset", "phone, mobile, cell"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "product_id": {"type": "keyword"},
      "title": {"type": "text", "analyzer": "product_analyzer", "fields": {"keyword": {"type": "keyword"}}},
      "description": {"type": "text", "analyzer": "product_analyzer"},
      "brand": {"type": "keyword"},
      "seller_id": {"type": "keyword"},
      "category_id": {"type": "keyword"},
      "category_path": {"type": "keyword"},
      "tags": {"type": "keyword"},
      "attributes": {
        "type": "nested",
        "properties": {
          "name": {"type": "keyword"},
          "value": {"type": "keyword"}
        }
      },
      "base_price": {"type": "scaled_float", "scaling_factor": 100},
      "sale_price": {"type": "scaled_float", "scaling_factor": 100},
      "currency": {"type": "keyword"},
      "rating": {"type": "float"},
      "review_count": {"type": "integer"},
      "in_stock": {"type": "boolean"},
      "popularity_score": {"type": "float"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"},
      "status": {"type": "keyword"}
    }
  }
}
```
