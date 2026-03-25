# Social Media & Content Platforms — Glossary

## Core Terms

| Term | Definition |
|------|-----------|
| **DAU/MAU** | Daily/Monthly Active Users — primary engagement metrics |
| **Fanout-on-Write** | Pre-compute feeds at write time by pushing post_id to each follower's cache |
| **Fanout-on-Read** | Compute feeds at read time by pulling from followed users' post lists |
| **Hybrid Fanout** | Fanout-on-write for regular users (< 10K followers), fanout-on-read for mega-creators |
| **Write Amplification** | One post creating N cache writes (one per follower) |
| **Social Graph** | Network of follow/friend relationships between users |
| **Feed Ranking** | ML model that orders posts by predicted engagement (P(like), P(comment), P(share)) |
| **Candidate Generation** | First stage of ranking: reduce 1000+ candidates to 500 using lightweight model |
| **Fine Ranking** | Second stage: deep model scores remaining candidates for final feed |
| **Engagement Rate** | (likes + comments + shares) / impressions |
| **Impression** | Single instance of content displayed to a user |
| **Mega-Creator** | User with > 10K followers requiring special fanout handling |
| **Profile Card** | Lightweight cached profile data (username, avatar, badge) embedded in every feed item |
| **TAO** | Facebook's purpose-built distributed graph store (The Associations and Objects) |
| **Signal Protocol** | Cryptographic protocol for E2E encrypted messaging (used by Signal, WhatsApp) |
| **Double Ratchet** | Key derivation algorithm in Signal Protocol providing forward secrecy |
| **HLS** | HTTP Live Streaming — adaptive bitrate video delivery protocol |
| **DASH** | Dynamic Adaptive Streaming over HTTP |
| **Transcoding** | Converting video to multiple resolution/bitrate variants |
| **ABR** | Adaptive Bitrate — player automatically selects quality based on network conditions |
| **RTMP** | Real-Time Messaging Protocol — used for live video ingest from creators |
| **PhotoDNA** | Microsoft's image hashing technology for detecting known CSAM |
| **Perceptual Hash** | Image fingerprint that is similar for visually similar images (unlike cryptographic hash) |
| **Content Moderation** | Detecting and actioning content that violates platform policies |
| **Coordinated Inauthentic Behavior (CIB)** | Network of accounts working together to mislead or manipulate |
| **Astroturfing** | Coordinated campaigns designed to appear grassroots |
| **Dunbar's Number** | ~150 — theoretical limit of meaningful social relationships per person |
| **WebSocket** | Persistent bidirectional TCP connection for real-time communication |
| **SSE** | Server-Sent Events — one-directional server-to-client push |
| **Bloom Filter** | Probabilistic data structure for set membership queries with no false negatives |
| **HyperLogLog** | Probabilistic cardinality estimation (approximate count of unique elements) |

## Abbreviations

| Abbreviation | Full Form |
|-------------|-----------|
| APNs | Apple Push Notification service |
| CDN | Content Delivery Network |
| CIB | Coordinated Inauthentic Behavior |
| CSAM | Child Sexual Abuse Material |
| CTR | Click-Through Rate |
| E2E | End-to-End (Encryption) |
| FCM | Firebase Cloud Messaging |
| FPS | Frames Per Second |
| ML | Machine Learning |
| NLP | Natural Language Processing |
| NSFW | Not Safe For Work |
| PEP | Politically Exposed Person |
| T&S | Trust & Safety |
| UGC | User-Generated Content |
