# Escrow System Schema Reference

## Core Tables

### escrow_contract
```sql
create table escrow_contract (
  escrow_id varchar(36) primary key,
  tenant_id varchar(64) not null,
  region_legal_entity varchar(32) not null,
  external_order_id varchar(64),
  buyer_party_id varchar(64) not null,
  seller_party_id varchar(64) not null,
  currency char(3) not null,
  amount_minor bigint not null,
  fee_minor bigint not null default 0,
  state varchar(32) not null,
  release_mode varchar(32) not null,
  release_deadline_at timestamptz,
  dispute_freeze boolean not null default false,
  version bigint not null default 0,
  created_at timestamptz not null,
  updated_at timestamptz not null
);
```

### escrow_milestone
```sql
create table escrow_milestone (
  milestone_id varchar(36) primary key,
  escrow_id varchar(36) not null references escrow_contract(escrow_id),
  title varchar(255) not null,
  amount_minor bigint not null,
  state varchar(32) not null,
  sequence_no int not null,
  due_at timestamptz,
  created_at timestamptz not null,
  updated_at timestamptz not null
);
create index idx_milestone_escrow_seq on escrow_milestone(escrow_id, sequence_no);
```

### funding_attempt
```sql
create table funding_attempt (
  funding_attempt_id varchar(36) primary key,
  escrow_id varchar(36) not null references escrow_contract(escrow_id),
  provider varchar(32) not null,
  provider_reference varchar(128),
  idempotency_key varchar(128) not null,
  amount_minor bigint not null,
  currency char(3) not null,
  state varchar(32) not null,
  created_at timestamptz not null,
  updated_at timestamptz not null
);
create unique index uq_funding_provider_ref on funding_attempt(provider, provider_reference);
```

### payout_attempt
```sql
create table payout_attempt (
  payout_attempt_id varchar(36) primary key,
  escrow_id varchar(36) not null references escrow_contract(escrow_id),
  seller_party_id varchar(64) not null,
  provider varchar(32) not null,
  provider_reference varchar(128),
  amount_minor bigint not null,
  currency char(3) not null,
  state varchar(32) not null,
  retry_count int not null default 0,
  created_at timestamptz not null,
  updated_at timestamptz not null
);
create unique index uq_payout_provider_ref on payout_attempt(provider, provider_reference);
```

### ledger_account
```sql
create table ledger_account (
  account_id varchar(36) primary key,
  tenant_id varchar(64) not null,
  account_type varchar(32) not null,
  owner_type varchar(32) not null,
  owner_id varchar(64) not null,
  currency char(3) not null,
  status varchar(16) not null,
  created_at timestamptz not null
);
create unique index uq_ledger_owner_currency on ledger_account(tenant_id, owner_type, owner_id, account_type, currency);
```

### ledger_entry
```sql
create table ledger_entry (
  ledger_entry_id varchar(36) primary key,
  account_id varchar(36) not null references ledger_account(account_id),
  escrow_id varchar(36),
  direction varchar(8) not null,
  amount_minor bigint not null,
  currency char(3) not null,
  posting_type varchar(32) not null,
  external_reference varchar(128),
  created_at timestamptz not null
);
create index idx_ledger_account_created on ledger_entry(account_id, created_at desc);
create index idx_ledger_escrow_created on ledger_entry(escrow_id, created_at desc);
```

### dispute_case
```sql
create table dispute_case (
  dispute_id varchar(36) primary key,
  escrow_id varchar(36) not null references escrow_contract(escrow_id),
  opened_by varchar(64) not null,
  reason_code varchar(64) not null,
  state varchar(32) not null,
  decision_code varchar(64),
  assigned_queue varchar(64),
  assigned_agent varchar(64),
  created_at timestamptz not null,
  updated_at timestamptz not null
);
create index idx_dispute_queue_state on dispute_case(assigned_queue, state, created_at);
```

### evidence_item
```sql
create table evidence_item (
  evidence_id varchar(36) primary key,
  escrow_id varchar(36) not null references escrow_contract(escrow_id),
  dispute_id varchar(36) references dispute_case(dispute_id),
  uploaded_by varchar(64) not null,
  object_key varchar(512) not null,
  checksum_sha256 varchar(128) not null,
  content_type varchar(128) not null,
  size_bytes bigint not null,
  created_at timestamptz not null
);
create index idx_evidence_escrow_created on evidence_item(escrow_id, created_at desc);
```

### webhook_receipt
```sql
create table webhook_receipt (
  webhook_receipt_id varchar(36) primary key,
  provider varchar(32) not null,
  provider_event_id varchar(128) not null,
  event_type varchar(64) not null,
  payload_hash varchar(128) not null,
  processed_state varchar(32) not null,
  created_at timestamptz not null,
  updated_at timestamptz not null
);
create unique index uq_webhook_provider_event on webhook_receipt(provider, provider_event_id);
```
