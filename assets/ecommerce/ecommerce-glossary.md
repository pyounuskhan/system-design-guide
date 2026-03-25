# E-Commerce & Marketplaces — Glossary & Abbreviations

## Domain Terms

| Term | Definition |
|------|-----------|
| **SKU** | Stock Keeping Unit — unique identifier for a product variant (e.g., "Red T-Shirt, Size M"). Every purchasable item has a distinct SKU. |
| **PDP** | Product Detail Page — the page displayed when a buyer clicks on a product. Assembles data from catalog, pricing, inventory, reviews, and media. |
| **OMS** | Order Management System — the service responsible for tracking the order lifecycle from creation to delivery and beyond. |
| **GMV** | Gross Merchandise Value — total value of goods sold through the platform, before deductions for returns, discounts, or fees. |
| **AOV** | Average Order Value — total revenue divided by number of orders. Key metric for growth. |
| **PSP** | Payment Service Provider — third-party service that processes payments (e.g., Stripe, Adyen, Razorpay, PayPal). |
| **RMA** | Return Merchandise Authorization — a formal approval issued to a buyer to return an item. |
| **COGS** | Cost of Goods Sold — the direct cost of producing or acquiring the goods sold. |
| **1P** | First-Party — inventory owned and sold directly by the platform (e.g., Amazon Basics). |
| **3P** | Third-Party — inventory owned and sold by external sellers on the platform marketplace. |
| **FBA** | Fulfillment By Amazon (or platform) — seller ships goods to platform warehouse; platform handles storage, packing, shipping. |
| **FBM** | Fulfilled By Merchant — seller handles storage and shipping directly. |
| **BFF** | Backend for Frontend — a service pattern where a backend service is tailored to the needs of a specific frontend (web, mobile, etc.). |
| **Conversion Rate** | Percentage of visitors who complete a purchase. Typical e-commerce: 1-3%. |
| **Cart Abandonment Rate** | Percentage of users who add items to cart but don't complete checkout. Industry average: ~70%. |
| **Chargeback** | A forced reversal of a payment initiated by the buyer's bank, typically due to fraud or dispute. |
| **Dropship** | Fulfillment model where the platform routes the order to a seller or supplier who ships directly to the buyer. |
| **Flash Sale** | Time-limited, often quantity-limited promotional event. Causes extreme traffic spikes. |
| **Wardrobing** | Fraudulent return behavior where buyer purchases, uses, and returns items (e.g., wearing clothes once and returning). |
| **Oversell** | Confirming an order for an item that is actually out of stock. One of the worst e-commerce failures. |
| **Hot Partition** | A database or cache partition receiving disproportionate traffic (e.g., a viral product's inventory row). |
| **Settlement** | The process of transferring funds from the platform to the seller after order completion. |
| **Fulfillment** | The process of picking, packing, and shipping an order to the buyer. |
| **Catalog Enrichment** | Adding additional data to product listings: enhanced descriptions, images, specifications, SEO metadata. |
| **Price Waterfall** | The sequence of discount evaluations applied to determine the final price (base price -> seller discount -> platform promo -> coupon -> loyalty). |

## Technical Terms

| Term | Definition |
|------|-----------|
| **CQRS** | Command Query Responsibility Segregation — separate models for reading and writing data. The catalog uses PostgreSQL for writes and Elasticsearch for reads. |
| **Saga** | A distributed transaction pattern using a sequence of local transactions with compensating actions for rollback. Used in the checkout flow. |
| **CDC** | Change Data Capture — a technique to capture and stream database changes as events. Used with Debezium to sync PostgreSQL changes to Elasticsearch and Redis. |
| **Idempotency** | The property that performing an operation multiple times has the same effect as performing it once. Critical for payment and order creation. |
| **Idempotency Key** | A client-generated unique identifier sent with a request to enable idempotent processing. |
| **Optimistic Locking** | A concurrency control strategy using a version column. The update fails if the version has changed since the read. |
| **Pessimistic Locking** | A concurrency control strategy that acquires a lock before modifying data (`SELECT ... FOR UPDATE`). Used for inventory reservation. |
| **Circuit Breaker** | A resilience pattern that stops calling a failing downstream service after a threshold of failures. Prevents cascade failures. |
| **Bulkhead** | An isolation pattern that limits the resources (threads, connections) allocated to a single downstream service. |
| **Backpressure** | A flow control mechanism where a consumer signals to a producer to slow down when it cannot keep up with the message rate. |
| **Event Sourcing** | Storing the sequence of state-changing events rather than just the current state. The order events table is an event log. |
| **Materialized View** | A precomputed, denormalized read model derived from source data. The Elasticsearch product index is a materialized view of the catalog. |
| **Stale-While-Revalidate** | A caching strategy that serves stale data while fetching fresh data in the background. Used for PDP caching. |
| **Single-Flight** | A pattern where only one request fetches data on a cache miss; concurrent requests wait for the result. Prevents cache stampede. |
| **Blue-Green Deployment** | Running two identical production environments and switching traffic between them for zero-downtime deploys. |
| **Canary Deployment** | Gradually rolling out a change to a small percentage of traffic before full rollout. |
| **Feature Flag** | A configuration switch that enables or disables a feature without deploying new code. |
| **Fan-out** | The pattern of a single event being consumed by multiple downstream services. Order events fan out to 6+ consumers. |
| **SLI** | Service Level Indicator — a measurable metric (e.g., p99 latency, error rate). |
| **SLO** | Service Level Objective — the target value for an SLI (e.g., "p99 latency < 200ms"). |
| **SLA** | Service Level Agreement — a formal commitment to an SLO, often with financial penalties for violations. |
| **RPO** | Recovery Point Objective — the maximum acceptable amount of data loss measured in time. |
| **RTO** | Recovery Time Objective — the maximum acceptable downtime during a failure. |
| **HPA** | Horizontal Pod Autoscaler — Kubernetes component that scales pod count based on metrics. |
| **WAF** | Web Application Firewall — protects against common web attacks (SQL injection, XSS, DDoS). |

## Abbreviations Quick Reference

| Abbreviation | Full Form |
|-------------|-----------|
| AZ | Availability Zone |
| CDN | Content Delivery Network |
| DB | Database |
| DDoS | Distributed Denial of Service |
| DR | Disaster Recovery |
| EDI | Electronic Data Interchange |
| ERP | Enterprise Resource Planning |
| FX | Foreign Exchange |
| GDPR | General Data Protection Regulation |
| HMAC | Hash-based Message Authentication Code |
| HSM | Hardware Security Module |
| JWT | JSON Web Token |
| KMS | Key Management Service |
| KYC | Know Your Customer |
| MFA | Multi-Factor Authentication |
| PCI-DSS | Payment Card Industry Data Security Standard |
| PO | Purchase Order |
| POD | Proof of Delivery |
| RBAC | Role-Based Access Control |
| RPS | Requests Per Second |
| TLS | Transport Layer Security |
| TPS | Transactions Per Second |
| TTL | Time To Live |
| UPI | Unified Payments Interface |
| VPC | Virtual Private Cloud |
| VRP | Vehicle Routing Problem |
| WMS | Warehouse Management System |
| XSS | Cross-Site Scripting |

## Marketplace Terms

| Term | Definition |
|------|-----------|
| **Settlement Cycle** | The periodic process (e.g., weekly) of calculating and disbursing seller payouts after deducting commissions and fees. |
| **Commission Rate** | The percentage of each sale that the platform retains as its fee. Varies by category (e.g., 15% electronics, 20% apparel). |
| **TCS** | Tax Collected at Source — in jurisdictions like India, the marketplace collects tax on behalf of sellers and remits to the government. |
| **Seller Tier** | Classification of sellers by performance and volume (new, standard, premium, enterprise). Higher tiers get better commission rates and faster settlement. |
| **Clawback** | Recovery of previously settled funds from a seller's future payouts, typically due to returns or chargebacks after settlement. |
| **Seller Score** | Composite rating of a seller's performance based on buyer reviews, delivery timeliness, cancellation rate, and policy compliance. |
| **Double-Entry Ledger** | Accounting system where every transaction creates equal debit and credit entries. Used in settlement to ensure financial integrity. |
| **Allocated Inventory** | Inventory that a seller has specifically assigned to one sales channel, preventing overselling across platforms. |
| **Seller BFF** | Backend for Frontend service dedicated to the seller dashboard, aggregating data from multiple internal services. |

## Growth & Engagement Terms

| Term | Definition |
|------|-----------|
| **Collaborative Filtering** | Recommendation technique that predicts a user's interests based on preferences of similar users. |
| **Content-Based Filtering** | Recommendation technique that suggests items similar to those a user has previously interacted with, based on item attributes. |
| **Cold Start** | The challenge of making recommendations for new users (no interaction history) or new items (no user feedback). |
| **CTR** | Click-Through Rate — percentage of recommendation impressions that result in a click. Key metric for recommendation quality. |
| **Feature Store** | Centralized repository for storing, managing, and serving ML features for both training and inference. |
| **User Embedding** | A dense vector representation of a user's preferences, learned by neural networks from interaction data. |
| **Price Sensitivity Score** | A per-user metric indicating how responsive they are to price changes. Used for personalized pricing display. |
| **Points Accrual** | The process of earning loyalty points through purchases or other qualifying actions. |
| **Points Redemption** | The process of spending earned loyalty points for discounts or rewards. |
| **Tier Qualification** | The process of evaluating whether a loyalty member has earned enough points to advance to the next tier. |
| **Coupon Budget** | The total monetary value allocated to a promotional campaign. When exhausted, no more redemptions are allowed. |
| **Wardrobing** | Fraudulent behavior where a buyer purchases items, uses them temporarily, and returns them. |

## Logistics Terms

| Term | Definition |
|------|-----------|
| **Putaway** | The warehouse process of placing received goods into designated bin locations for storage. |
| **Pick Path** | The route a warehouse worker follows to collect items for orders. Optimizing pick paths reduces fulfillment time. |
| **Zone Picking** | A warehouse strategy where each worker is responsible for items in their assigned zone only. |
| **Wave Picking** | Grouping orders into time-based waves, typically aligned with carrier pickup schedules. |
| **Bin Location** | A specific storage position in a warehouse, identified by aisle, shelf, and position coordinates. |
| **Carrier Cutoff** | The deadline by which packages must be staged for a carrier to meet the day's pickup. |
| **Last Mile** | The final leg of delivery from the local distribution hub to the buyer's doorstep. Most expensive and complex part of shipping. |
| **Proof of Delivery (POD)** | Evidence that a package was delivered, typically a photo, signature, or GPS confirmation. |
| **VRP Solver** | Software that solves the Vehicle Routing Problem — optimizing delivery routes for cost, time, and constraints. |
| **Dynamic Re-Routing** | Adjusting delivery routes in real-time based on changing conditions (traffic, new orders, driver delays). |
| **Shipment Group** | A subset of order items that will be fulfilled from the same warehouse and shipped together. |
| **Fulfillment Split** | When items in a single order are shipped from multiple warehouses, creating multiple shipments. |
