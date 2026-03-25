# Fintech & Payments — Glossary & Abbreviations

## Core Payment Terms

| Term | Definition |
|------|-----------|
| **Authorization** | Real-time approval from the card issuer to proceed with a transaction. Funds are held but not yet transferred. |
| **Capture** | The action that converts an authorization hold into an actual charge. Merchant initiates capture after fulfillment. |
| **Void** | Cancellation of an authorization before capture. No money moves; the hold is released. |
| **Settlement** | The actual transfer of funds between banks/PSPs after capture. Typically T+1 to T+3. |
| **Chargeback** | A forced payment reversal initiated by the cardholder's bank, typically due to fraud or dispute. |
| **Representment** | The merchant's response to a chargeback, providing evidence that the charge was legitimate. |
| **Interchange Fee** | Fee paid by the acquirer to the issuer for each card transaction. Varies by card type, merchant category, and region. |
| **Acquirer** | The bank/processor that processes payments on behalf of the merchant. |
| **Issuer** | The bank that issued the cardholder's credit or debit card. |
| **BIN** | Bank Identification Number — first 6-8 digits of a card number, identifying the issuing bank and card type. |
| **PAN** | Primary Account Number — the full card number. Must be tokenized per PCI-DSS. |
| **Tokenization** | Replacing sensitive card data with a non-reversible token for secure storage and processing. |
| **3D Secure (3DS)** | Card authentication protocol where the issuer verifies the cardholder's identity (e.g., via SMS OTP or biometric). Shifts fraud liability from merchant to issuer. |
| **SCA** | Strong Customer Authentication — PSD2 requirement for two-factor authentication on electronic payments in the EU. |
| **Decline** | The issuer refuses the transaction. Reasons include insufficient funds, expired card, or fraud suspicion. |
| **Soft Decline** | A decline that may succeed on retry (e.g., issuer timeout). |
| **Hard Decline** | A decline that will not succeed on retry (e.g., stolen card, account closed). |

## Ledger Terms

| Term | Definition |
|------|-----------|
| **Double-Entry Bookkeeping** | Accounting method where every transaction creates equal and opposite debit and credit entries. Ensures the books always balance. |
| **Journal Entry** | A record of a financial transaction, consisting of two or more postings that sum to zero. |
| **Posting** | A single debit or credit entry in the ledger, always part of a balanced journal entry. |
| **Chart of Accounts** | The hierarchical structure of all ledger accounts (assets, liabilities, equity, revenue, expenses). |
| **Balance Invariant** | The rule that total debits must equal total credits across all ledger postings. Violation indicates a bug. |
| **Accrual** | Recording revenue/expense when earned/incurred, not when cash moves. |
| **Reconciliation** | The process of comparing internal records with external records (bank statements, PSP reports) to identify discrepancies. |
| **Write-off** | Recording a loss for an uncollectable amount (e.g., fraud loss, bad debt). |

## Risk & Compliance Terms

| Term | Definition |
|------|-----------|
| **KYC** | Know Your Customer — regulatory requirement to verify customer identity before providing financial services. |
| **AML** | Anti-Money Laundering — regulations and procedures to detect and prevent money laundering. |
| **SAR** | Suspicious Activity Report — filed with regulators (e.g., FinCEN) when suspicious financial activity is detected. |
| **CTR** | Currency Transaction Report — required for cash transactions exceeding $10,000 (US). |
| **PEP** | Politically Exposed Person — individuals with prominent public functions who pose higher risk for corruption. |
| **OFAC** | Office of Foreign Assets Control — US sanctions enforcement body. |
| **Sanctions Screening** | Checking customers against government sanctions lists (OFAC, EU, UN) before processing transactions. |
| **Structuring** | Deliberate breaking of transactions into smaller amounts to avoid reporting thresholds. A form of money laundering. |
| **Velocity Check** | Monitoring the rate and pattern of transactions to detect abnormal behavior (e.g., too many transactions in short time). |
| **Chargeback Rate** | Percentage of transactions that result in chargebacks. Above 1% triggers card network warnings. |
| **False Positive** | A legitimate transaction incorrectly flagged as fraudulent. Reduces conversion and customer trust. |
| **BNPL** | Buy Now Pay Later — installment payment product where the buyer pays in 3-12 installments. |

## Infrastructure & Protocol Terms

| Term | Definition |
|------|-----------|
| **PSP** | Payment Service Provider — processes payments on behalf of merchants (Stripe, Adyen, Razorpay). |
| **PCI-DSS** | Payment Card Industry Data Security Standard — security requirements for handling card data. |
| **PSD2** | Payment Services Directive 2 — EU regulation mandating open banking APIs and strong authentication. |
| **ACH** | Automated Clearing House — US batch bank transfer system. |
| **SEPA** | Single Euro Payments Area — EU bank transfer system. |
| **SWIFT** | Global interbank messaging network for international wire transfers. |
| **UPI** | Unified Payments Interface — India's real-time bank-to-bank payment system. |
| **RTP** | Real-Time Payments — US instant payment rail operated by The Clearing House. |
| **FPS** | Faster Payments Service — UK instant payment system. |
| **PIX** | Brazil's instant payment system, operated by the Central Bank. |
| **FIX Protocol** | Financial Information eXchange — standard protocol for electronic trading communication. |
| **HSM** | Hardware Security Module — tamper-resistant device for cryptographic key management. |
| **SOX** | Sarbanes-Oxley Act — US regulation requiring financial controls and reporting for public companies. |
| **SOC 2** | Service Organization Control 2 — audit framework for security, availability, and confidentiality. |

## Abbreviations

| Abbreviation | Full Form |
|-------------|-----------|
| APR | Annual Percentage Rate |
| CDE | Cardholder Data Environment |
| DPDK | Data Plane Development Kit |
| FX | Foreign Exchange |
| HFT | High-Frequency Trading |
| NACHA | National Automated Clearing House Association |
| NPCI | National Payments Corporation of India |
| ODFI | Originating Depository Financial Institution |
| RDFI | Receiving Depository Financial Institution |
| RRN | Retrieval Reference Number |
| VPA | Virtual Payment Address (UPI identifier) |
