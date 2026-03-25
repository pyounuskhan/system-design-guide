# Communication Systems — Glossary

| Term | Definition |
|------|-----------|
| **WebSocket** | Persistent bidirectional TCP connection over HTTP upgrade; foundation of real-time messaging |
| **Long Polling** | Client makes HTTP request; server holds response until data available or timeout |
| **SSE** | Server-Sent Events — one-directional server-to-client push over HTTP |
| **Signal Protocol** | E2E encryption protocol (X3DH + Double Ratchet) used by Signal, WhatsApp |
| **X3DH** | Extended Triple Diffie-Hellman — key agreement protocol for establishing shared secrets |
| **Double Ratchet** | Key derivation algorithm providing forward secrecy; each message uses a new key |
| **Sender Key** | Optimization for encrypted groups — sender encrypts once, all members decrypt |
| **Forward Secrecy** | Compromising current keys doesn't reveal past messages |
| **Delivery Receipt** | Confirmation that server delivered message to recipient's device (single tick) |
| **Read Receipt** | Confirmation that recipient viewed the message (double blue tick) |
| **Fan-out** | Distributing a message to all group members or channel subscribers |
| **Presence** | Online/offline/away/DND status of a user |
| **Typing Indicator** | Ephemeral signal showing a user is composing a message |
| **APNs** | Apple Push Notification service |
| **FCM** | Firebase Cloud Messaging (Google) — push for Android and web |
| **STUN** | Session Traversal Utilities for NAT — helps discover public IP for WebRTC |
| **TURN** | Traversal Using Relays around NAT — relays media when direct connection fails |
| **SFU** | Selective Forwarding Unit — forwards individual streams to each participant |
| **MCU** | Multipoint Control Unit — mixes streams into one composite |
| **SDP** | Session Description Protocol — describes media capabilities in WebRTC |
| **ICE** | Interactive Connectivity Establishment — finds best network path for WebRTC |
| **WebRTC** | Web Real-Time Communication — browser-native audio/video/data protocol |
| **Simulcast** | Sending multiple quality levels of a video stream; receiver selects best |
| **Last-N** | Only forwarding video for N most recent speakers to save bandwidth |
| **DKIM** | DomainKeys Identified Mail — email authentication via cryptographic signing |
| **SPF** | Sender Policy Framework — email DNS record authorizing sending IPs |
| **DMARC** | Domain-based Message Authentication, Reporting, and Conformance |
| **Dunning** | Retry strategy for failed recurring payments (not messaging-specific but appears in billing) |
