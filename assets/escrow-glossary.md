# Escrow System Glossary

## Domain Terms

| Term | Definition |
| --- | --- |
| Escrow contract | The formal agreement that controls amount, parties, release policy, and dispute behavior |
| Custodial partner | The PSP or bank that legally holds or settles funds on behalf of the platform |
| Hold account | The internal or external balance bucket representing money currently locked in escrow |
| Inspection window | The post-fulfillment time period during which the buyer may inspect or dispute |
| Seller reserve | Amount temporarily withheld from seller payouts for risk reasons |
| Split settlement | A dispute outcome that sends some money to seller and some back to buyer |

## Technical Abbreviations

| Abbreviation | Expansion |
| --- | --- |
| PSP | Payment service provider |
| KYC | Know your customer |
| AML | Anti-money laundering |
| DLQ | Dead-letter queue |
| DR | Disaster recovery |
| RPO | Recovery point objective |
| RTO | Recovery time objective |
| OLTP | Online transaction processing |
| SoT | Source of truth |

## Interview Shorthand
- "Shadow ledger" means the internal balance-tracking model the platform trusts for accounting and audit, even if money is held by an external provider.
- "Pending but uncertain" means the system cannot yet prove final provider truth and must avoid acting as though the outcome is final.
- "Region-affined writer" means a legal entity or tenant writes in one primary region to preserve simpler financial invariants.

## Important Formulas
- Average QPS = daily requests / 86,400
- Active funded working set = daily new escrows * average hold duration in days
- Evidence storage growth = daily uploads * average file size * replication multiplier
- Gross escrow volume = sum(amount_minor) for funded escrows over a time range
