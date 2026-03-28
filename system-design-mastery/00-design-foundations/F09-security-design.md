# F09. Security Design

## Part Context
**Part:** Part 0 — System Design Foundations & Principles
**Position:** Chapter F09 of F12
**Why this part exists:** Security is not a feature bolted onto a finished system — it is an architectural property that must be woven into every layer from the earliest design decisions. This chapter provides a comprehensive reference for authentication, authorization, infrastructure hardening, and application-level defenses that every system design must address.

---

## Overview

Every system design conversation eventually reaches the same question: "How do you secure this?" The answer is never a single technology or a checkbox exercise. Security design is the discipline of making principled decisions about identity, access, confidentiality, integrity, and availability — decisions that compound across every service boundary, data store, network hop, and user interaction in a distributed system.

This chapter performs a deep-dive into **four domain areas** that together form a complete security architecture:

### Section 1 — Authentication
The mechanisms that establish identity:

1. **OAuth 2.0** — the authorization framework that underpins modern identity, covering all grant types, token lifecycle, and storage strategies.
2. **JSON Web Tokens (JWT)** — the self-contained token format, its structure, signing algorithms, validation pipeline, and common pitfalls.
3. **Session-Based Authentication** — server-side session management, session stores, cookie security attributes, and session lifecycle.
4. **Multi-Factor Authentication (MFA)** — TOTP, WebAuthn/FIDO2, SMS weaknesses, and recovery code strategies.
5. **Single Sign-On (SSO)** — SAML vs OIDC, identity federation, cross-service session management, and enterprise integration.
6. **API Authentication** — API keys, OAuth2 for machine-to-machine, mutual TLS, and HMAC signature schemes.

### Section 2 — Authorization
The mechanisms that enforce access control:

1. **Role-Based Access Control (RBAC)** — role hierarchies, role explosion, dynamic roles, and practical modeling.
2. **Attribute-Based Access Control (ABAC)** — policy-driven access, policy decision points, and XACML patterns.
3. **Relationship-Based Access Control (ReBAC)** — Google Zanzibar, Authzed/SpiceDB, and permission checks as graph traversals.
4. **Policy Engines** — OPA (Open Policy Agent), Cedar, Casbin, and how to decouple policy from code.
5. **Row-Level Security** — database-level enforcement, multi-tenant isolation, and query-rewriting strategies.

### Section 3 — Infrastructure Security
The hardening of networks, secrets, and traffic:

1. **Encryption** — at rest, in transit, application-level, envelope encryption, and key rotation.
2. **Secrets Management** — HashiCorp Vault, AWS Secrets Manager, rotation strategies, and zero-trust secret distribution.
3. **Rate Limiting** — per-user, per-IP, per-API-key, distributed rate limiting, and token bucket implementation.
4. **DDoS Protection** — L3/L4 vs L7 attacks, WAF rules, origin hiding, and challenge pages.

### Section 4 — Application Security
The defense of code and data:

1. **OWASP Top 10** — injection, broken authentication, XSS, CSRF, SSRF, with prevention patterns.
2. **Input Validation** — allow-list vs deny-list, parameterized queries, and content security policy.
3. **Secure Development Lifecycle** — threat modeling (STRIDE), security reviews, and dependency scanning.
4. **Zero Trust Architecture** — never trust always verify, micro-segmentation, and identity-aware proxies.

Every section is written to be useful for learners building mental models, engineers designing production systems, and candidates preparing for system design interviews.

---

## Why Security Design Matters in Real Systems

- A single authentication bypass can expose every user account in the system — identity is the outermost perimeter.
- Authorization flaws (IDOR, privilege escalation) consistently rank among the most exploited vulnerability classes in production systems.
- Encryption at rest and in transit is not optional — regulatory frameworks (GDPR, HIPAA, PCI-DSS, SOC 2) require it, and breaches without it carry amplified legal and financial consequences.
- Rate limiting and DDoS protection are availability concerns as much as security concerns — an unprotected API can be trivially overwhelmed.
- Supply chain attacks (compromised dependencies, leaked secrets in CI/CD) have become the dominant attack vector for modern cloud-native systems.
- Security is the single topic that crosses every system design interview domain: storage, networking, compute, APIs, and data pipelines all have security dimensions.

---

## Problem Framing

### Threat Landscape

Modern distributed systems face a multi-layered threat landscape:

- **External attackers** — credential stuffing, API abuse, injection attacks, DDoS.
- **Insider threats** — employees with over-provisioned access, compromised developer machines, leaked secrets.
- **Supply chain attacks** — malicious dependencies, compromised CI/CD pipelines, stolen signing keys.
- **Compliance requirements** — GDPR, HIPAA, PCI-DSS, SOC 2, FedRAMP impose minimum security controls.
- **Zero-day vulnerabilities** — unpatched systems become targets within hours of disclosure.

### Design Principles

Every security design decision in this chapter is guided by these principles:

1. **Defense in depth** — no single control is sufficient; layer multiple defenses so that the failure of one does not compromise the system.
2. **Least privilege** — every identity (user, service, process) receives only the minimum permissions necessary for its function.
3. **Fail closed** — when a security control encounters an error, it denies access rather than allowing it.
4. **Zero trust** — no network location, no prior authentication event, and no internal service is implicitly trusted.
5. **Separation of duties** — critical operations require multiple approvals or distinct identities.

---

# Section 1: Authentication

Authentication answers the question: **"Who are you?"** It is the process of verifying that an entity (user, service, device) is who it claims to be. Every subsequent security decision — authorization, audit logging, rate limiting — depends on a correct and unforgeable identity.

This section covers the six major authentication mechanisms used in modern distributed systems, from user-facing OAuth 2.0 flows to machine-to-machine mutual TLS.

---

## 1.1 OAuth 2.0

> **Version note (OAuth 2.1):** OAuth 2.1 (draft consolidation of OAuth 2.0 + best-practice RFCs) makes PKCE mandatory for all clients, removes the implicit grant entirely, removes the resource-owner password credentials grant, and requires refresh token rotation or sender-constraining. See Section 4.16 for a dedicated OAuth 2.1 / OIDC Modern Standards deep-dive.

### 1.1.1 What OAuth 2.0 Is (and Is Not)

OAuth 2.0 is an **authorization delegation framework** — it allows a user to grant a third-party application limited access to their resources without sharing their credentials. Despite its name, OAuth 2.0 is widely used as the foundation for authentication when combined with OpenID Connect (OIDC).

Key terminology:

| Term | Definition |
|------|-----------|
| **Resource Owner** | The user who owns the data (e.g., a GitHub user) |
| **Client** | The application requesting access (e.g., a CI/CD tool) |
| **Authorization Server** | Issues tokens after authenticating the user (e.g., GitHub's OAuth server) |
| **Resource Server** | Hosts the protected resources (e.g., GitHub's API) |
| **Access Token** | A credential that grants access to a resource |
| **Refresh Token** | A credential used to obtain a new access token without re-authentication |
| **Scope** | A string that defines the permissions being requested |
| **Grant Type** | The method used to obtain an access token |

### 1.1.2 Authorization Code Grant

The authorization code grant is the most secure and most common flow for server-side web applications. It uses a two-step process: first obtain an authorization code via the browser, then exchange it for tokens via a back-channel server-to-server call.

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant C as Client App (Server)
    participant AS as Authorization Server
    participant RS as Resource Server

    U->>C: 1. Click "Login with Provider"
    C->>U: 2. Redirect to AS /authorize
    Note over U,AS: ?response_type=code<br/>&client_id=xxx<br/>&redirect_uri=xxx<br/>&scope=openid profile<br/>&state=random123
    U->>AS: 3. User authenticates & consents
    AS->>U: 4. Redirect to client redirect_uri
    Note over AS,U: ?code=auth_code_xyz<br/>&state=random123
    U->>C: 5. Browser follows redirect with code
    C->>AS: 6. POST /token (back-channel)
    Note over C,AS: grant_type=authorization_code<br/>&code=auth_code_xyz<br/>&client_id=xxx<br/>&client_secret=xxx<br/>&redirect_uri=xxx
    AS->>C: 7. Return access_token + refresh_token
    C->>RS: 8. API call with access_token
    RS->>C: 9. Protected resource
```

**Why the code exchange matters:** The authorization code is transmitted through the browser (front-channel), which is inherently less secure. The actual tokens are obtained via a server-to-server call (back-channel) that includes the client secret. This means:
- The access token never passes through the browser.
- The authorization code is single-use and short-lived (typically 60 seconds).
- Even if an attacker intercepts the code, they cannot exchange it without the client secret.

**The `state` parameter** prevents CSRF attacks. The client generates a random value, includes it in the authorization request, and verifies it matches when the callback arrives. Without this, an attacker could forge a callback URL and trick the user into linking an attacker-controlled account.

### 1.1.3 Authorization Code with PKCE

PKCE (Proof Key for Code Exchange, pronounced "pixy") extends the authorization code grant for public clients — applications that cannot securely store a client secret (mobile apps, single-page applications, CLI tools).

```mermaid
sequenceDiagram
    participant U as User
    participant C as Client (Public)
    participant AS as Auth Server

    Note over C: Generate code_verifier (random 43-128 chars)
    Note over C: code_challenge = BASE64URL(SHA256(code_verifier))
    C->>AS: 1. /authorize + code_challenge + code_challenge_method=S256
    AS->>U: 2. Login prompt
    U->>AS: 3. Authenticate & consent
    AS->>C: 4. Authorization code
    C->>AS: 5. /token + code + code_verifier
    Note over AS: Verify: SHA256(code_verifier) == stored code_challenge
    AS->>C: 6. Access token + refresh token
```

**How PKCE prevents interception attacks:**
1. The client generates a cryptographically random `code_verifier` (43-128 characters).
2. It derives a `code_challenge` by hashing the verifier with SHA-256 and Base64URL-encoding it.
3. The `code_challenge` is sent with the authorization request.
4. The `code_verifier` is sent with the token exchange request.
5. The authorization server verifies that `SHA256(code_verifier)` matches the stored `code_challenge`.
6. An attacker who intercepts the authorization code cannot use it because they do not have the `code_verifier`.

**PKCE is now recommended for ALL clients**, including confidential (server-side) clients, as per OAuth 2.1. It adds defense-in-depth even when a client secret is available.

> **OAuth 2.1 update:** In OAuth 2.1, PKCE is **mandatory** for every authorization code grant — not just public clients. The implicit grant is removed entirely. See Section 4.16 for the full OAuth 2.1 changes.

### 1.1.4 Client Credentials Grant

The client credentials grant is used for **machine-to-machine** communication where no user is involved. The client authenticates directly with its own credentials.

```
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=service-inventory
&client_secret=s3cr3t-k3y
&scope=inventory:read inventory:write
```

**Use cases:**
- Microservice-to-microservice calls within a trusted network.
- Batch processing jobs that access APIs on behalf of the system (not a specific user).
- CI/CD pipelines that deploy code or access infrastructure APIs.

**Security considerations:**
- Client secrets must be rotated regularly and stored in a secrets manager (never in code or environment variables).
- Scope the tokens as narrowly as possible — a service that only reads inventory should not have write permissions.
- Short token lifetimes (5-15 minutes) limit the blast radius if a token is leaked.
- Consider mTLS-based client authentication as a stronger alternative to client secrets.

### 1.1.5 Device Authorization Grant (Device Flow)

The device flow is designed for input-constrained devices (smart TVs, IoT devices, CLI tools) that cannot easily handle browser redirects.

```mermaid
sequenceDiagram
    participant D as Device (Smart TV)
    participant AS as Auth Server
    participant U as User (Phone/Laptop)

    D->>AS: 1. POST /device/code (client_id, scope)
    AS->>D: 2. device_code + user_code + verification_uri
    D->>D: 3. Display: "Go to example.com/device, enter code: ABCD-1234"
    U->>AS: 4. User visits URI, enters code
    U->>AS: 5. User authenticates & consents
    loop Polling
        D->>AS: 6. POST /token (device_code, grant_type=device_code)
        AS->>D: 7. authorization_pending OR access_token
    end
    Note over D: Stop polling when token received
```

**Key design decisions:**
- The device polls the token endpoint at a server-specified interval (typically 5 seconds).
- The server returns `authorization_pending` until the user completes authentication.
- The `device_code` has a configurable expiration (typically 15 minutes).
- The `user_code` must be short enough to type easily (6-8 alphanumeric characters, often formatted as `XXXX-XXXX`).

### 1.1.6 Token Types

OAuth 2.0 defines two token types in practice:

**Bearer Tokens:**
- The most common type. Possession of the token is sufficient to use it.
- Transmitted in the `Authorization: Bearer <token>` header.
- Must be protected in transit (TLS) and at rest (secure storage).
- If stolen, anyone can use it — there is no proof-of-possession requirement.

**DPoP (Demonstration of Proof-of-Possession) Tokens:**
- Bind the token to a specific client key pair.
- The client generates a DPoP proof (a signed JWT) for each request.
- Even if the access token is intercepted, it cannot be used without the private key.
- Specified in RFC 9449, gaining adoption in high-security environments.

### 1.1.7 Refresh Tokens

Refresh tokens solve the tension between short-lived access tokens (security) and avoiding frequent re-authentication (user experience).

**Refresh token lifecycle:**

| Phase | Behavior |
|-------|----------|
| **Issuance** | Returned alongside the access token during the initial token exchange |
| **Storage** | Must be stored securely (server-side session, encrypted cookie, OS keychain) |
| **Usage** | Client sends refresh token to `/token` endpoint to get a new access token |
| **Rotation** | Best practice: issue a new refresh token with each use and invalidate the old one |
| **Revocation** | Must be revocable by the authorization server (e.g., on logout or password change) |
| **Expiration** | Typically 7-90 days; sliding window resets on each use |

**Refresh token rotation** is critical for detecting theft. When a refresh token is used, the server issues a new one and invalidates the old. If an attacker steals a refresh token and uses it, the legitimate client's next refresh attempt will fail (because its token was already consumed), triggering a security alert and revoking the entire token family.

```mermaid
sequenceDiagram
    participant C as Client
    participant AS as Auth Server

    Note over C,AS: Initial auth: access_token_1 + refresh_token_1
    C->>AS: Use refresh_token_1
    AS->>C: access_token_2 + refresh_token_2
    Note over AS: Invalidate refresh_token_1

    Note over C: Attacker steals refresh_token_1
    Note over C: Attacker tries to use refresh_token_1
    C->>AS: Use refresh_token_1 (stolen)
    AS->>AS: Token already used — REUSE DETECTED
    AS->>AS: Revoke entire token family
    AS->>C: Error: token revoked
```

### 1.1.8 Token Storage Strategies

Where tokens are stored determines the attack surface:

| Storage Location | Pros | Cons | Best For |
|-----------------|------|------|----------|
| **HttpOnly Secure Cookie** | Not accessible to JavaScript; automatic transmission | Vulnerable to CSRF (mitigated by SameSite); cookie size limits | Server-rendered web apps |
| **In-memory (JS variable)** | Not persisted; not accessible from other tabs | Lost on page refresh; not accessible to service workers | SPAs with short sessions |
| **sessionStorage** | Scoped to tab; cleared on tab close | Accessible to XSS; not shared across tabs | SPAs needing tab-level isolation |
| **localStorage** | Persists across sessions | Accessible to XSS; shared across tabs | Avoid for tokens if possible |
| **OS Keychain / Keystore** | Hardware-backed security; not accessible to other apps | Platform-specific API; requires native code | Mobile apps, desktop apps |
| **Backend session** | Token never reaches the client | Requires server-side state; adds latency | BFF (Backend-for-Frontend) pattern |

**The BFF pattern** is the gold standard for SPAs: the frontend talks to a backend proxy (BFF) that manages tokens. The BFF stores tokens server-side and uses HttpOnly cookies for session management with the browser. This eliminates token exposure to JavaScript entirely.

```mermaid
flowchart LR
    subgraph Browser
        SPA[SPA Frontend]
    end
    subgraph Backend
        BFF[BFF Proxy]
        TS[Token Store<br/>Redis/DB]
    end
    subgraph External
        AS[Auth Server]
        API[Resource API]
    end

    SPA -->|HttpOnly Cookie| BFF
    BFF --> TS
    BFF -->|Authorization Code Exchange| AS
    BFF -->|Bearer Token| API
```

---

## 1.2 JSON Web Tokens (JWT)

### 1.2.1 JWT Structure

A JWT is a compact, URL-safe token format consisting of three Base64URL-encoded parts separated by dots:

```
header.payload.signature
```

**Header** — identifies the token type and signing algorithm:
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-2024-03"
}
```

**Payload** — contains claims (assertions about the subject):
```json
{
  "iss": "https://auth.example.com",
  "sub": "user-12345",
  "aud": "https://api.example.com",
  "exp": 1711324800,
  "iat": 1711321200,
  "nbf": 1711321200,
  "jti": "unique-token-id-abc",
  "scope": "read:orders write:orders",
  "email": "user@example.com",
  "roles": ["admin", "editor"],
  "tenant_id": "org-789"
}
```

**Signature** — ensures integrity and authenticity:
```
RSASHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  privateKey
)
```

### 1.2.2 Registered Claims

The JWT specification (RFC 7519) defines seven registered claims:

| Claim | Name | Purpose |
|-------|------|---------|
| `iss` | Issuer | Identifies the token issuer (must match expected value) |
| `sub` | Subject | Identifies the principal (user ID, service ID) |
| `aud` | Audience | Intended recipient(s) of the token |
| `exp` | Expiration | Unix timestamp after which the token is invalid |
| `nbf` | Not Before | Unix timestamp before which the token is invalid |
| `iat` | Issued At | Unix timestamp when the token was issued |
| `jti` | JWT ID | Unique identifier to prevent replay attacks |

### 1.2.3 Signing Algorithms

**Symmetric (HMAC):**

| Algorithm | Mechanism | Key Requirement |
|-----------|-----------|----------------|
| HS256 | HMAC-SHA256 | Shared secret between issuer and verifier |
| HS384 | HMAC-SHA384 | Shared secret |
| HS512 | HMAC-SHA512 | Shared secret |

**Asymmetric (RSA / ECDSA):**

| Algorithm | Mechanism | Key Requirement |
|-----------|-----------|----------------|
| RS256 | RSA-SHA256 | Private key signs, public key verifies |
| RS384 | RSA-SHA384 | Private key signs, public key verifies |
| RS512 | RSA-SHA512 | Private key signs, public key verifies |
| ES256 | ECDSA-SHA256 (P-256) | Private key signs, public key verifies |
| ES384 | ECDSA-SHA384 (P-384) | Private key signs, public key verifies |
| PS256 | RSA-PSS-SHA256 | Private key signs, public key verifies |

**When to use which:**

| Scenario | Algorithm | Reason |
|----------|-----------|--------|
| Single service issues and validates | HS256 | Simpler; secret stays in one service |
| Auth server issues, many services validate | RS256 or ES256 | Services only need the public key; cannot forge tokens |
| High-throughput validation | ES256 | Smaller keys, faster verification than RSA |
| Regulatory requirement for RSA | RS256 / PS256 | FIPS compliance may require RSA |

### 1.2.4 JWT Validation Pipeline

Every service that receives a JWT must perform the following validation steps in order:

```mermaid
flowchart TD
    A[Receive JWT] --> B{Parse Header}
    B -->|Invalid Format| Z[REJECT: Malformed]
    B -->|Valid| C{Check 'alg' header}
    C -->|alg = 'none'| Z2[REJECT: None algorithm]
    C -->|Unexpected alg| Z3[REJECT: Algorithm mismatch]
    C -->|Valid alg| D{Verify Signature}
    D -->|Invalid| Z4[REJECT: Bad signature]
    D -->|Valid| E{Check 'exp' claim}
    E -->|Expired| Z5[REJECT: Token expired]
    E -->|Valid| F{Check 'nbf' claim}
    F -->|Not yet valid| Z6[REJECT: Not yet valid]
    F -->|Valid| G{Check 'iss' claim}
    G -->|Unexpected issuer| Z7[REJECT: Wrong issuer]
    G -->|Valid| H{Check 'aud' claim}
    H -->|Wrong audience| Z8[REJECT: Wrong audience]
    H -->|Valid| I[ACCEPT: Token valid]
```

**Critical validation rules:**

1. **Always verify the signature** — never trust a JWT without cryptographic verification.
2. **Always check `alg`** — the `"alg": "none"` attack tricks validators into skipping signature verification. Your code must reject `none` and only accept explicitly allowed algorithms.
3. **Always check `exp`** — expired tokens must be rejected. Allow a small clock skew tolerance (30-60 seconds).
4. **Always check `iss` and `aud`** — a token meant for Service A should not be accepted by Service B.
5. **Use the `kid` header** to select the correct key from a JWKS (JSON Web Key Set) endpoint, enabling key rotation without downtime.

### 1.2.5 JWT Pitfalls

**Pitfall 1 — The `alg: none` attack:**
If a validator respects the `alg` header from the token itself, an attacker can set `"alg": "none"`, remove the signature, and the token passes validation. **Mitigation:** Never derive the algorithm from the token. Hardcode or configure the expected algorithm.

**Pitfall 2 — Algorithm confusion (RS256 → HS256):**
If a server is configured for RS256, an attacker can change the `alg` to HS256 and sign the token using the RSA public key as the HMAC secret. Since the public key is often publicly available, this allows token forgery. **Mitigation:** Enforce asymmetric algorithms when asymmetric keys are used. Never accept HS256 if the server expects RS256.

**Pitfall 3 — Token bloat:**
JWTs are self-contained, which means every claim you add increases the token size. A token with extensive role hierarchies, permissions, and metadata can exceed cookie size limits (4KB) and add measurable latency to every API call. **Mitigation:** Keep JWTs lean. Store detailed permissions in a cache and use the JWT only for identity and basic claims.

**Pitfall 4 — Inability to revoke:**
JWTs are valid until they expire. If a user logs out or their account is compromised, the JWT remains valid. **Mitigation options:**
- Short expiration (5-15 minutes) with refresh tokens.
- Token revocation list (check a blocklist on each request — adds latency).
- Token versioning (store a version counter per user; reject tokens with old versions).

**Pitfall 5 — Sensitive data in payload:**
The JWT payload is Base64URL-encoded, not encrypted. Anyone with the token can decode and read the payload. **Mitigation:** Never put passwords, secrets, or sensitive PII in a JWT. If you need encrypted tokens, use JWE (JSON Web Encryption).

### 1.2.6 JWT vs Opaque Tokens

| Property | JWT (Self-Contained) | Opaque Token |
|----------|---------------------|--------------|
| **Validation** | Local — no network call needed | Requires introspection endpoint call |
| **Revocation** | Difficult — valid until expiry | Easy — delete from token store |
| **Size** | Large (hundreds to thousands of bytes) | Small (random string, ~32 bytes) |
| **Information** | Contains claims (user, roles, scopes) | Reference only — no embedded data |
| **Privacy** | Payload readable by anyone with the token | Data stays on the server |
| **Performance** | Faster validation (no network hop) | Slower (network call per validation) |
| **Best for** | Microservices with distributed validation | Monoliths, high-security contexts |

---

## 1.3 Session-Based Authentication

### 1.3.1 How Server-Side Sessions Work

Session-based authentication stores user state on the server rather than in the token itself. The flow is:

1. User submits credentials (username + password).
2. Server verifies credentials and creates a session object in a session store.
3. Server returns a **session ID** in a cookie.
4. The browser automatically sends the cookie with every subsequent request.
5. The server looks up the session ID in the session store and retrieves user data.

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Server
    participant SS as Session Store (Redis)

    B->>S: POST /login (username, password)
    S->>S: Verify credentials
    S->>SS: Store session {userId, roles, expiresAt}
    SS->>S: session_id = "abc123"
    S->>B: Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Lax
    B->>S: GET /api/orders (Cookie: session_id=abc123)
    S->>SS: Lookup session "abc123"
    SS->>S: {userId: "user-12345", roles: ["admin"]}
    S->>B: 200 OK (orders data)
```

### 1.3.2 Session Stores

| Store | Pros | Cons | Best For |
|-------|------|------|----------|
| **Redis** | Sub-millisecond lookups, TTL support, clustering | Requires infrastructure; data loss if not persisted | Production systems at scale |
| **Memcached** | Fast, simple | No persistence, no clustering | Simple session caching |
| **Database (PostgreSQL)** | Durable, queryable | Higher latency; session table can grow large | Small-scale apps, audit requirements |
| **In-memory (process)** | Zero latency | Lost on restart; cannot scale horizontally | Development only |
| **Signed cookies** | No server state needed | Size limits (4KB); cannot revoke without blocklist | Stateless architectures |

**Redis is the industry standard** for session storage. A typical Redis session configuration:

```
Key:    session:abc123
Value:  {"user_id": "12345", "roles": ["admin"], "ip": "203.0.113.42", "ua": "Mozilla/5.0..."}
TTL:    3600 (1 hour)
```

### 1.3.3 Cookie Security Attributes

| Attribute | Value | Purpose |
|-----------|-------|---------|
| `HttpOnly` | (flag) | Prevents JavaScript from reading the cookie — mitigates XSS token theft |
| `Secure` | (flag) | Cookie is only sent over HTTPS — prevents interception over HTTP |
| `SameSite=Lax` | Lax | Cookie is sent on top-level navigations but not on cross-origin subrequests — mitigates CSRF |
| `SameSite=Strict` | Strict | Cookie is never sent on cross-origin requests — strongest CSRF protection but breaks some flows |
| `SameSite=None; Secure` | None | Cookie is sent on all requests including cross-origin — required for third-party contexts |
| `Domain` | `.example.com` | Scopes the cookie to the domain and subdomains |
| `Path` | `/api` | Scopes the cookie to a path prefix |
| `Max-Age` | 3600 | Cookie expires after N seconds |
| `Expires` | Date string | Cookie expires at a specific date/time |

**Recommended baseline for session cookies:**
```
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
```

### 1.3.4 Session Lifecycle Management

**Session fixation prevention:** Always regenerate the session ID after authentication. If the session ID is set before login and not changed, an attacker can set a known session ID (via URL parameter or cookie injection) and hijack the session after the user logs in.

**Session invalidation on security events:**
- Password change → invalidate all sessions except current.
- MFA enrollment/removal → invalidate all sessions.
- Suspicious activity detected → invalidate all sessions.
- User-initiated "log out everywhere" → invalidate all sessions.

**Absolute vs sliding expiration:**
- **Absolute timeout** — session expires after a fixed time regardless of activity (e.g., 8 hours). Limits exposure window.
- **Sliding timeout** — session expiration resets on each request (e.g., 30 minutes of inactivity). Better user experience.
- **Best practice:** Use both — sliding timeout of 30 minutes within an absolute timeout of 8 hours.

### 1.3.5 Sessions vs JWTs — When to Use Each

| Consideration | Sessions | JWTs |
|--------------|----------|------|
| **Revocation** | Immediate — delete the session | Difficult — wait for expiry or maintain blocklist |
| **Scalability** | Requires shared session store | Stateless — any server can validate |
| **Latency** | Session store lookup on each request | No lookup needed (self-contained) |
| **Simplicity** | Straightforward; well-understood | Complex; many pitfalls |
| **Mobile/SPA** | Requires cookie support or BFF pattern | Works well with bearer tokens |
| **Microservices** | Challenging to share sessions across services | Each service validates independently |

**Hybrid approach (most common in production):**
- Use **session cookies** between the browser and the BFF/gateway.
- Use **JWTs** for service-to-service communication behind the gateway.
- The gateway translates the session into a short-lived JWT for downstream services.

### 1.3.6 Session Security Hardening

Beyond basic cookie attributes, production session implementations require additional hardening:

**IP binding and fingerprinting:**
Sessions can be bound to the client's IP address or browser fingerprint. If a session is used from a different IP or fingerprint, it is flagged as suspicious.

| Binding Strategy | Pros | Cons |
|-----------------|------|------|
| **Strict IP binding** | Detects session theft from different network | Breaks for users on mobile networks (IP changes frequently) |
| **Subnet binding** | More lenient; allows minor IP changes | Less secure than strict binding |
| **Browser fingerprint** | Detects different browsers/devices | Fingerprints can be spoofed; privacy concerns |
| **Composite score** | Weighted combination of IP, fingerprint, user agent | Most robust; requires tuning |

**Concurrent session limits:**
Control how many active sessions a user can have simultaneously.

```python
class SessionManager:
    def __init__(self, redis_client, max_sessions: int = 5):
        self.redis = redis_client
        self.max_sessions = max_sessions

    def create_session(self, user_id: str, session_data: dict) -> str:
        session_id = generate_secure_random(32)

        # Track all sessions for this user
        user_sessions_key = f"user_sessions:{user_id}"
        existing_sessions = self.redis.zrange(user_sessions_key, 0, -1)

        # If at max, remove the oldest session
        if len(existing_sessions) >= self.max_sessions:
            oldest = existing_sessions[0]
            self.redis.delete(f"session:{oldest}")
            self.redis.zrem(user_sessions_key, oldest)

        # Create the new session
        self.redis.set(
            f"session:{session_id}",
            json.dumps(session_data),
            ex=3600  # 1 hour TTL
        )
        self.redis.zadd(
            user_sessions_key,
            {session_id: time.time()}
        )

        return session_id

    def invalidate_all_sessions(self, user_id: str):
        """Called on password change, account compromise, or 'log out everywhere'"""
        user_sessions_key = f"user_sessions:{user_id}"
        sessions = self.redis.zrange(user_sessions_key, 0, -1)
        for session_id in sessions:
            self.redis.delete(f"session:{session_id}")
        self.redis.delete(user_sessions_key)
```

**Session data minimization:**
Store the minimum data necessary in the session. A session should contain:
- User ID (required for identification)
- Session creation time (for absolute timeout)
- Last activity time (for sliding timeout)
- Authentication level (basic vs MFA-verified)
- Session version (for forced re-authentication)

Avoid storing in the session:
- Full user profile (fetch on demand from the user service)
- Permissions (fetch on demand or cache separately)
- Large data structures (store in a separate cache keyed by session ID)

**Session encryption:**
Even when stored in Redis, session data should be encrypted if it contains sensitive attributes:

```python
from cryptography.fernet import Fernet

class EncryptedSessionStore:
    def __init__(self, redis_client, encryption_key: bytes):
        self.redis = redis_client
        self.cipher = Fernet(encryption_key)

    def set(self, session_id: str, data: dict, ttl: int):
        encrypted = self.cipher.encrypt(json.dumps(data).encode())
        self.redis.set(f"session:{session_id}", encrypted, ex=ttl)

    def get(self, session_id: str) -> dict:
        encrypted = self.redis.get(f"session:{session_id}")
        if not encrypted:
            return None
        return json.loads(self.cipher.decrypt(encrypted).decode())
```

### 1.3.7 Password Security

While passwords are an authentication mechanism (not session management), their handling is closely related to session security.

**Password hashing:**

| Algorithm | Status | Parameters | Notes |
|-----------|--------|-----------|-------|
| **Argon2id** | Recommended | Memory: 64MB, iterations: 3, parallelism: 4 | Winner of Password Hashing Competition; memory-hard |
| **bcrypt** | Acceptable | Cost factor: 12+ | Widely available; not memory-hard |
| **scrypt** | Acceptable | N=32768, r=8, p=1 | Memory-hard; less widely supported than bcrypt |
| **PBKDF2** | Legacy | Iterations: 600,000+ (SHA-256) | NIST approved; not memory-hard; vulnerable to GPU attacks |
| **MD5 / SHA-1** | Dangerous | N/A | Never use for passwords; trivially crackable |

**Password policies (modern recommendations from NIST SP 800-63B):**

| Recommendation | Rationale |
|---------------|-----------|
| Minimum 8 characters, no maximum (except reasonable limit like 128) | Short passwords are guessable; arbitrary maximums limit passphrase use |
| Check against breach databases (Have I Been Pwned API) | Reused passwords are the #1 attack vector |
| No composition rules (uppercase, special characters) | They do not meaningfully increase entropy but frustrate users |
| No periodic forced rotation | Causes weaker passwords (users increment a number) |
| Allow paste in password fields | Encourages password manager use |
| Show password strength meter | Nudges users toward stronger passwords |

**Password breach checking:**

```python
import hashlib
import requests

def is_password_breached(password: str) -> bool:
    """Check if password appears in known breaches using k-Anonymity API."""
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    # Only the first 5 chars of the hash are sent to the API
    response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
    hashes = response.text.splitlines()

    for line in hashes:
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return True  # Password found in breaches
    return False
```

---

## 1.4 Multi-Factor Authentication (MFA)

### 1.4.1 Why MFA Matters

Passwords alone are insufficient. Credential stuffing attacks use billions of leaked username/password pairs to gain access to accounts. MFA adds a second factor that an attacker is unlikely to have, dramatically reducing the success rate of credential-based attacks.

**Factor categories:**

| Factor Type | Description | Examples |
|-------------|-------------|----------|
| **Something you know** | Knowledge factor | Password, PIN, security questions |
| **Something you have** | Possession factor | Phone, hardware key, smart card |
| **Something you are** | Inherence factor | Fingerprint, face recognition, voice |

True MFA requires factors from at least two different categories. A password + security question is NOT true MFA (both are knowledge factors).

### 1.4.2 TOTP (Time-Based One-Time Password)

TOTP generates a 6-digit code that changes every 30 seconds. Both the server and the authenticator app share a secret key, and both independently compute the same code using the current time.

**How TOTP works:**

```
TOTP = TRUNCATE(HMAC-SHA1(secret_key, floor(current_time / 30)))
```

1. During enrollment, the server generates a random secret (typically 20 bytes, Base32-encoded).
2. The secret is shared with the user via QR code (containing a `otpauth://` URI).
3. The user scans the QR code with an authenticator app (Google Authenticator, Authy, 1Password).
4. On each login, the user provides the current 6-digit code.
5. The server computes the expected code and allows a window of +/- 1 time step (90 seconds total) to account for clock drift.

**TOTP strengths:**
- Works offline (no network required for code generation).
- Widely supported by authenticator apps.
- Simple to implement server-side.

**TOTP weaknesses:**
- Phishable — an attacker can relay the TOTP code in real-time through a fake login page.
- Secret must be stored server-side (exposure in a breach allows code generation).
- User experience friction (must open app, read code, type it).

### 1.4.3 WebAuthn / FIDO2

WebAuthn is a W3C standard that enables **phishing-resistant** authentication using public key cryptography and hardware authenticators (security keys, platform biometrics).

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant S as Server
    participant A as Authenticator (Security Key)

    Note over U,S: Registration
    S->>B: Challenge + relying party info
    B->>A: Create credential (challenge, rpId)
    A->>U: User verification (touch/biometric)
    U->>A: Approved
    A->>B: Public key + credential ID + attestation
    B->>S: Store public key for user

    Note over U,S: Authentication
    S->>B: Challenge + allowed credential IDs
    B->>A: Sign challenge with private key
    A->>U: User verification (touch/biometric)
    U->>A: Approved
    A->>B: Signed assertion
    B->>S: Verify signature with stored public key
    S->>S: Authentication success
```

**Why WebAuthn is phishing-resistant:**
- The authenticator binds the credential to the **origin** (domain). A credential created for `bank.com` will not respond to a challenge from `bank-login.com`.
- The private key **never leaves the authenticator** — it cannot be phished, intercepted, or replayed.
- The browser enforces origin checking — the relying party ID must match the page origin.

**Passkeys** (discoverable credentials) extend WebAuthn by syncing credentials across devices via the platform vendor (Apple iCloud Keychain, Google Password Manager, Microsoft). This eliminates the "lost device" problem that plagued hardware-only FIDO2.

### 1.4.4 SMS-Based MFA (and Why It Is Weak)

SMS-based MFA sends a one-time code to the user's phone number. While better than no MFA, it has significant weaknesses:

**Attack vectors:**
- **SIM swapping** — an attacker convinces a carrier to transfer the victim's phone number to a new SIM. The attacker then receives all SMS messages.
- **SS7 interception** — the SS7 protocol (used for telecom routing) has known vulnerabilities that allow message interception.
- **Phishing** — an attacker can relay SMS codes in real-time through a fake login page.
- **Malware** — mobile malware can read SMS messages.

**NIST SP 800-63B** has categorized SMS as a "restricted" authenticator, recommending against it for high-security contexts.

**When SMS MFA is acceptable:**
- As a fallback when no better option is available.
- For low-risk accounts where any MFA is better than none.
- In regions where smartphone penetration for authenticator apps is low.

### 1.4.5 Recovery Codes

Recovery codes are the safety net when the primary MFA method is unavailable (lost phone, broken security key). Design considerations:

- Generate 8-10 single-use recovery codes during MFA enrollment.
- Each code should be 8-12 alphanumeric characters (e.g., `ABCD-1234-EFGH`).
- Store codes as bcrypt hashes (not plaintext) in the database.
- Display codes exactly once during enrollment and instruct the user to store them securely.
- Each code is single-use — mark as consumed after use.
- Allow the user to regenerate a new set (invalidating the old ones).
- Log recovery code usage as a security event for auditing.

### 1.4.6 MFA Implementation Architecture

```mermaid
flowchart TD
    subgraph Login Flow
        L1[User enters email + password]
        L2{Password correct?}
        L3{MFA enrolled?}
        L4[Prompt for MFA code]
        L5{MFA code valid?}
        L6[Create session with auth_level=mfa]
        L7[Create session with auth_level=basic]
        L8[Reject: Invalid credentials]
        L9[Reject: Invalid MFA code]
    end

    L1 --> L2
    L2 -->|No| L8
    L2 -->|Yes| L3
    L3 -->|No| L7
    L3 -->|Yes| L4
    L4 --> L5
    L5 -->|No| L9
    L5 -->|Yes| L6
```

**Step-up authentication:**
Some operations require a higher authentication level than the initial login. Step-up authentication re-verifies the user's identity before allowing sensitive operations.

| Operation | Required Auth Level | Example |
|-----------|-------------------|---------|
| Browse products | Basic (password only) | Shopping |
| View order history | Basic | Account activity |
| Change email address | MFA-verified | Account settings |
| Initiate wire transfer | MFA-verified + recent (within 5 minutes) | Financial operations |
| Change MFA settings | MFA-verified + recent + additional verification | Security settings |
| Delete account | MFA-verified + recent + confirmation email | Destructive action |

```python
def require_auth_level(required_level: str, max_age_seconds: int = None):
    """Decorator for step-up authentication."""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            session = get_session(request)

            if session.auth_level < required_level:
                return redirect_to_mfa_challenge(
                    return_url=request.url,
                    required_level=required_level
                )

            if max_age_seconds and session.mfa_verified_at:
                age = time.time() - session.mfa_verified_at
                if age > max_age_seconds:
                    return redirect_to_mfa_challenge(
                        return_url=request.url,
                        required_level=required_level,
                        reason="session_age_exceeded"
                    )

            return func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_auth_level("mfa", max_age_seconds=300)
def transfer_funds(request):
    # Only reached if MFA was verified within the last 5 minutes
    pass
```

### 1.4.7 Adaptive Authentication

Adaptive authentication dynamically adjusts the authentication requirements based on risk signals:

| Risk Signal | Low Risk | Medium Risk | High Risk |
|------------|----------|-------------|-----------|
| **Known device** | Yes | Partially | No |
| **Known IP/location** | Home/office | Same city | Different country |
| **Time of day** | Business hours | Evening | 3 AM |
| **Login velocity** | Normal | Slightly elevated | Rapid attempts |
| **Action sensitivity** | Read-only | Write | Financial/destructive |

**Adaptive response:**

| Risk Level | Response |
|-----------|----------|
| Low | Allow with password only |
| Medium | Require MFA |
| High | Require MFA + additional verification (email confirmation, security questions) |
| Very High | Block and alert (likely compromised account) |

```mermaid
flowchart LR
    REQ[Login Request] --> RS[Risk Scoring Engine]
    RS --> D1{Risk Score}
    D1 -->|Low: 0-30| A1[Password Only]
    D1 -->|Medium: 31-60| A2[Password + MFA]
    D1 -->|High: 61-80| A3[Password + MFA + Email Verification]
    D1 -->|Critical: 81-100| A4[Block + Alert Security Team]

    subgraph Risk Inputs
        IP[IP Reputation]
        GEO[Geolocation]
        DEV[Device Fingerprint]
        BEH[Behavioral Signals]
        VEL[Login Velocity]
    end

    IP --> RS
    GEO --> RS
    DEV --> RS
    BEH --> RS
    VEL --> RS
```

---

## 1.5 Single Sign-On (SSO)

### 1.5.1 SSO Fundamentals

Single Sign-On allows a user to authenticate once and access multiple applications without re-entering credentials. SSO centralizes authentication at an **Identity Provider (IdP)** and issues assertions to **Service Providers (SPs)**.

```mermaid
flowchart LR
    subgraph IdP [Identity Provider]
        AUTH[Auth Engine]
        DIR[User Directory]
        SSO_SESSION[SSO Session]
    end
    subgraph SP1 [App 1 - CRM]
        A1[Login]
    end
    subgraph SP2 [App 2 - Wiki]
        A2[Login]
    end
    subgraph SP3 [App 3 - CI/CD]
        A3[Login]
    end

    A1 -->|Redirect to IdP| AUTH
    A2 -->|Redirect to IdP| AUTH
    A3 -->|Redirect to IdP| AUTH
    AUTH --> DIR
    AUTH --> SSO_SESSION
    AUTH -->|SAML Assertion / OIDC Token| A1
    AUTH -->|SAML Assertion / OIDC Token| A2
    AUTH -->|SAML Assertion / OIDC Token| A3
```

### 1.5.2 SAML vs OpenID Connect (OIDC)

| Aspect | SAML 2.0 | OIDC |
|--------|----------|------|
| **Protocol** | XML-based | JSON/REST-based (built on OAuth 2.0) |
| **Token Format** | XML assertion (SAML response) | JWT (ID token) |
| **Transport** | HTTP POST binding, HTTP Redirect | Standard HTTP with JSON |
| **Adoption** | Enterprise, legacy systems | Modern apps, mobile, SPAs |
| **Assertion Size** | Large (XML with signatures) | Compact (JWT) |
| **Discovery** | Metadata XML file | `.well-known/openid-configuration` |
| **Complexity** | High (XML canonicalization, signature validation) | Lower (standard JWT validation) |
| **Mobile Support** | Poor (designed for browsers) | Excellent (HTTP/JSON native) |

**Use SAML when:**
- Integrating with enterprise identity systems (Active Directory Federation Services, Okta, OneLogin) that require it.
- The SP only supports SAML.
- Existing SAML infrastructure is in place.

**Use OIDC when:**
- Building new applications.
- Supporting mobile and SPA clients.
- You want a simpler, more developer-friendly protocol.
- You need programmatic access (OIDC includes OAuth 2.0 for API authorization).

### 1.5.3 Identity Federation

Federation enables SSO across organizational boundaries. A user in Organization A can access resources in Organization B without creating a separate account.

**Trust models:**
- **Direct federation** — Organization A and Organization B establish a direct trust relationship. Simple but does not scale (N organizations need N*(N-1)/2 trust relationships).
- **Hub-and-spoke** — a central identity broker mediates trust. Each organization trusts the broker, and the broker handles protocol translation (SAML ↔ OIDC).
- **Mesh federation** — organizations use a shared trust framework (e.g., InCommon for US universities). Each organization publishes metadata, and trust is established through the framework.

### 1.5.4 Cross-Service Session Management

When a user logs out of one application, should they be logged out of all applications? This is the **single logout** problem.

**SAML Single Logout (SLO):**
- The SP sends a `LogoutRequest` to the IdP.
- The IdP sends `LogoutRequest` messages to all SPs the user has active sessions with.
- Each SP destroys its local session and responds with `LogoutResponse`.
- Fragile in practice: if any SP is down or slow, the logout chain breaks.

**OIDC Back-Channel Logout:**
- The IdP sends a signed `logout_token` (JWT) to each RP's back-channel logout endpoint.
- More reliable than SAML SLO because it does not depend on the browser.
- RPs must implement a `/backchannel-logout` endpoint that invalidates the session.

**Practical recommendation:** Implement session timeout as the primary defense. Single logout is a best-effort optimization. Critical systems should have short session lifetimes (15-30 minutes) with re-authentication for sensitive operations.

---

## 1.6 API Authentication

### 1.6.1 API Keys

API keys are the simplest form of API authentication — a long random string that identifies the caller.

**How API keys work:**
```
GET /api/v1/data HTTP/1.1
Host: api.example.com
X-API-Key: sk_live_abc123def456ghi789
```

**API key design decisions:**

| Decision | Recommendation |
|----------|---------------|
| **Format** | Prefix + random bytes (e.g., `sk_live_` for production secret keys, `pk_live_` for publishable keys) |
| **Length** | 32+ random bytes (256 bits of entropy) |
| **Storage** | Hash the key (SHA-256) and store the hash. Only show the full key once at creation. |
| **Transmission** | Always HTTPS. Prefer custom header (`X-API-Key`) over query parameter (query strings appear in logs). |
| **Scoping** | Assign permissions per key. Allow users to create multiple keys with different scopes. |
| **Rotation** | Support key rotation: create new key → update clients → revoke old key. Never require downtime. |
| **Rate limiting** | Associate rate limits with each key. Track usage for billing and abuse detection. |

**API keys are NOT authentication** — they identify the calling application, not the user. They are appropriate for:
- Server-to-server communication where the calling application is known.
- Public APIs with usage-based billing.
- Development/testing environments.

They are NOT appropriate for:
- Authenticating end users (use OAuth 2.0 + OIDC).
- Mobile or frontend applications (keys are easily extracted from client code).

### 1.6.2 OAuth 2.0 for APIs

For user-context API access, the OAuth 2.0 authorization code flow (with PKCE) issues access tokens that carry user identity and scoped permissions. For machine-to-machine API access, the client credentials grant is appropriate.

**API Gateway integration:**
The API gateway validates the OAuth 2.0 access token before routing the request to the backend service. This centralizes authentication and keeps backend services simple.

```mermaid
flowchart LR
    C[Client] -->|Bearer Token| GW[API Gateway]
    GW -->|Validate Token| AS[Auth Server / JWKS]
    GW -->|Inject User Context| SVC[Backend Service]
    SVC -->|Trusted headers| DB[(Database)]
```

### 1.6.3 Mutual TLS (mTLS)

Mutual TLS extends standard TLS by requiring **both** the client and server to present certificates. Standard TLS only authenticates the server to the client; mTLS adds client authentication.

**How mTLS works:**

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant CA as Certificate Authority

    Note over C,S: TLS Handshake
    C->>S: ClientHello
    S->>C: ServerHello + Server Certificate
    S->>C: CertificateRequest (mTLS-specific)
    C->>S: Client Certificate
    S->>CA: Validate client cert against trusted CA
    CA->>S: Valid
    C->>S: CertificateVerify (signed with client private key)
    S->>S: Verify signature — client has private key
    Note over C,S: Encrypted channel established with mutual authentication
```

**mTLS use cases:**
- Service mesh communication (Istio, Linkerd automatically manage mTLS between services).
- Zero-trust networks where IP-based trust is insufficient.
- Financial APIs and regulatory-compliant systems requiring strong mutual authentication.
- IoT device authentication where each device has a unique certificate.

**mTLS operational challenges:**
- Certificate lifecycle management (issuance, rotation, revocation).
- Certificate authority infrastructure (internal CA or commercial CA).
- Debugging is harder (TLS handshake failures are opaque without proper logging).
- Performance overhead (TLS handshake is more expensive than a bearer token check).

### 1.6.4 HMAC Signatures

HMAC (Hash-based Message Authentication Code) signatures authenticate API requests by signing the request content with a shared secret. Unlike bearer tokens, HMAC signatures prove that the request has not been tampered with in transit.

**How HMAC signing works:**

```
# Construct the string to sign
string_to_sign = HTTP_METHOD + "\n"
                + PATH + "\n"
                + QUERY_STRING + "\n"
                + TIMESTAMP + "\n"
                + BODY_HASH

# Compute the signature
signature = HMAC-SHA256(secret_key, string_to_sign)

# Send the request
GET /api/v1/orders HTTP/1.1
Host: api.example.com
X-Timestamp: 1711324800
X-Signature: base64(signature)
X-Key-Id: key-abc123
```

**Why include the timestamp:** To prevent replay attacks. The server rejects requests with timestamps older than 5 minutes. The server must maintain a nonce store or rely on timestamp + request uniqueness to prevent exact replays within the time window.

**HMAC vs Bearer tokens:**

| Property | HMAC Signature | Bearer Token |
|----------|---------------|--------------|
| **Tamper protection** | Yes — request body is signed | No — token is independent of request |
| **Replay protection** | Yes — with timestamp/nonce | No — token can be replayed |
| **Secret exposure** | Secret never sent over the wire | Token sent with every request |
| **Complexity** | Higher — both client and server must implement signing | Lower — just attach the token |
| **Use cases** | Webhooks, high-security APIs (AWS Signature V4) | General-purpose APIs |

---

# Section 2: Authorization

Authorization answers the question: **"What are you allowed to do?"** While authentication establishes identity, authorization determines what that identity can access, modify, or delete. Authorization failures (IDOR, privilege escalation, broken access control) are consistently the #1 vulnerability class in the OWASP Top 10.

This section covers the five major authorization paradigms, from simple role-based models to relationship-based systems like Google Zanzibar.

---

## 2.1 Role-Based Access Control (RBAC)

### 2.1.1 RBAC Fundamentals

RBAC assigns permissions to **roles**, and roles are assigned to **users**. Users inherit all permissions associated with their roles.

```mermaid
flowchart LR
    U1[User: Alice] --> R1[Role: Admin]
    U2[User: Bob] --> R2[Role: Editor]
    U3[User: Carol] --> R3[Role: Viewer]
    U2 --> R3
    R1 --> P1[Permission: read]
    R1 --> P2[Permission: write]
    R1 --> P3[Permission: delete]
    R1 --> P4[Permission: manage_users]
    R2 --> P1
    R2 --> P2
    R3 --> P1
```

**RBAC components:**

| Component | Definition |
|-----------|-----------|
| **User** | An identity (person, service account) that requests access |
| **Role** | A named collection of permissions (e.g., `admin`, `editor`, `viewer`) |
| **Permission** | An allowed action on a resource (e.g., `orders:read`, `users:delete`) |
| **Assignment** | The mapping of users to roles |
| **Session** | The active set of roles for a user in a given context |

### 2.1.2 Role Hierarchy

Roles can be organized in a hierarchy where higher roles inherit all permissions from lower roles:

```
Super Admin
    └── Admin
        └── Manager
            └── Editor
                └── Viewer
```

**Hierarchical RBAC advantages:**
- Reduces redundancy — each role only defines its incremental permissions.
- Simplifies role management — promoting a user grants all lower-level permissions automatically.

**Hierarchical RBAC risks:**
- Over-provisioning — a manager inherits all editor and viewer permissions, even if some are unnecessary.
- Rigidity — the hierarchy assumes a single dimension of authority, which does not map well to matrix organizations.

### 2.1.3 The Role Explosion Problem

As systems grow, the number of roles can explode combinatorially:

**Example scenario:**
- 5 departments (engineering, sales, marketing, support, finance)
- 4 access levels (viewer, editor, manager, admin)
- 3 regions (NA, EU, APAC)
- 2 environments (production, staging)

Naive RBAC: 5 x 4 x 3 x 2 = **120 roles**

Each new dimension multiplies the number of roles. With 10 dimensions of 5 values each, you would need 5^10 = ~10 million roles — obviously unmanageable.

**Solutions to role explosion:**

| Approach | How It Works | Trade-off |
|----------|-------------|-----------|
| **Dynamic roles** | Compose roles from attributes at runtime | More flexible; harder to audit |
| **Role parameterization** | `editor(project=X, region=EU)` | Reduces count; requires policy engine |
| **Transition to ABAC** | Replace roles with attribute-based policies | Most flexible; highest complexity |
| **Scoped roles** | `editor` role + `scope: project-123` on the assignment | Keeps role count low; scope logic needed |
| **Group-based inheritance** | Users belong to groups; groups have roles | Reduces direct role assignments |

### 2.1.4 Dynamic Roles

Dynamic roles are computed at request time based on contextual attributes rather than being statically assigned:

```python
def get_effective_roles(user, resource, context):
    roles = set(user.static_roles)

    # Add dynamic roles based on context
    if resource.owner_id == user.id:
        roles.add("resource_owner")

    if user.department == resource.department:
        roles.add("department_member")

    if context.is_business_hours and user.is_on_call:
        roles.add("on_call_responder")

    if resource.classification == "public":
        roles.add("public_reader")

    return roles
```

Dynamic roles bridge the gap between RBAC and ABAC — they use the familiar concept of roles but derive them from attributes, reducing the number of static role assignments.

### 2.1.5 RBAC Implementation Patterns

**Database schema for RBAC:**

```sql
-- Core tables
CREATE TABLE users (
    id          UUID PRIMARY KEY,
    email       VARCHAR(255) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE roles (
    id          UUID PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id   UUID REFERENCES roles(id)  -- for hierarchy
);

CREATE TABLE permissions (
    id          UUID PRIMARY KEY,
    resource    VARCHAR(100) NOT NULL,  -- e.g., "orders"
    action      VARCHAR(50) NOT NULL,   -- e.g., "read", "write", "delete"
    UNIQUE(resource, action)
);

-- Junction tables
CREATE TABLE user_roles (
    user_id     UUID REFERENCES users(id),
    role_id     UUID REFERENCES roles(id),
    scope       VARCHAR(255),           -- optional: "project:123", "org:456"
    granted_by  UUID REFERENCES users(id),
    granted_at  TIMESTAMP DEFAULT NOW(),
    expires_at  TIMESTAMP,
    PRIMARY KEY (user_id, role_id, scope)
);

CREATE TABLE role_permissions (
    role_id       UUID REFERENCES roles(id),
    permission_id UUID REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);
```

**Permission check query (with hierarchy):**

```sql
WITH RECURSIVE role_tree AS (
    -- Start with the user's directly assigned roles
    SELECT r.id, r.parent_id
    FROM roles r
    JOIN user_roles ur ON r.id = ur.role_id
    WHERE ur.user_id = :user_id
      AND (ur.expires_at IS NULL OR ur.expires_at > NOW())

    UNION ALL

    -- Walk up the hierarchy (child inherits parent permissions)
    SELECT r.id, r.parent_id
    FROM roles r
    JOIN role_tree rt ON r.id = rt.parent_id
)
SELECT EXISTS (
    SELECT 1
    FROM role_permissions rp
    JOIN permissions p ON rp.permission_id = p.id
    JOIN role_tree rt ON rp.role_id = rt.id
    WHERE p.resource = :resource
      AND p.action = :action
) AS has_permission;
```

---

## 2.2 Attribute-Based Access Control (ABAC)

### 2.2.1 ABAC Fundamentals

ABAC evaluates access decisions based on **attributes** of the subject (user), resource, action, and environment — rather than pre-assigned roles. Policies are expressed as rules that combine these attributes.

**Attribute categories:**

| Category | Examples |
|----------|----------|
| **Subject attributes** | user.department, user.clearance_level, user.location |
| **Resource attributes** | document.classification, order.status, file.owner |
| **Action attributes** | action.type (read/write/delete), action.method (GET/POST) |
| **Environment attributes** | time_of_day, ip_address, device_type, risk_score |

**Example ABAC policy (pseudo-code):**

```
PERMIT access
WHERE
    subject.department == resource.department
    AND subject.clearance_level >= resource.classification_level
    AND action.type IN ["read", "list"]
    AND environment.time BETWEEN "08:00" AND "18:00"
    AND environment.ip_network IN corporate_networks
```

### 2.2.2 ABAC Architecture

```mermaid
flowchart TD
    subgraph Application
        PEP[Policy Enforcement Point<br/>API Gateway / Middleware]
    end
    subgraph Policy Engine
        PDP[Policy Decision Point<br/>OPA / Cedar]
        PIP[Policy Information Point<br/>User Store / Resource Metadata]
        PAP[Policy Administration Point<br/>Policy Editor / Git Repo]
    end

    PEP -->|"Can user X do action Y<br/>on resource Z?"| PDP
    PDP -->|Fetch attributes| PIP
    PAP -->|Deploy policies| PDP
    PDP -->|PERMIT / DENY| PEP
```

**ABAC components:**

| Component | Role |
|-----------|------|
| **PEP** (Policy Enforcement Point) | Intercepts requests and enforces the PDP's decision. Typically the API gateway or middleware. |
| **PDP** (Policy Decision Point) | Evaluates the request against policies and returns PERMIT or DENY. This is the policy engine (OPA, Cedar). |
| **PIP** (Policy Information Point) | Provides attribute data (user directory, resource metadata, risk scores) to the PDP for evaluation. |
| **PAP** (Policy Administration Point) | Where policies are authored, reviewed, and deployed. Often a Git repository with CI/CD. |

### 2.2.3 ABAC vs RBAC

| Dimension | RBAC | ABAC |
|-----------|------|------|
| **Granularity** | Coarse (role level) | Fine (attribute level) |
| **Flexibility** | Limited by role definitions | Highly flexible; any attribute combinable |
| **Scalability** | Role explosion with many dimensions | Scales well with dimensions |
| **Auditability** | Easy — "who has which role?" | Harder — must trace policy evaluation |
| **Performance** | Fast — role lookup | Slower — policy evaluation + attribute fetching |
| **Complexity** | Low to moderate | High — policy language, attribute management |
| **Best for** | Simple hierarchies, small organizations | Complex access requirements, regulatory compliance |

### 2.2.4 XACML (eXtensible Access Control Markup Language)

XACML is an OASIS standard for ABAC policy language and architecture. While verbose (XML-based), it defined the PEP/PDP/PIP/PAP architecture that all modern policy systems follow.

**XACML has been largely superseded** by modern policy languages (Rego for OPA, Cedar for AWS) that use more developer-friendly syntax, but the architectural concepts remain foundational.

---

## 2.3 Relationship-Based Access Control (ReBAC)

### 2.3.1 ReBAC Fundamentals

ReBAC determines access based on the **relationships** between subjects and resources, modeled as a graph. Rather than asking "does the user have the admin role?", ReBAC asks "does the user have a viewer relationship with this document?"

**The key insight:** In many systems, access naturally follows relationships — you can edit a document because you are the owner, or because someone shared it with you, or because you are a member of the team that owns it. These relationships form a graph that can be traversed to determine access.

### 2.3.2 Google Zanzibar

Google Zanzibar is the authorization system that powers access control for Google Drive, Google Cloud, YouTube, and other Google services. It handles authorization checks at a scale of millions of requests per second with low latency.

**Zanzibar's data model:**

```
// Relation tuples: <object>#<relation>@<subject>
document:readme#owner@user:alice
document:readme#viewer@team:engineering#member
team:engineering#member@user:bob
team:engineering#member@user:carol
folder:root#viewer@user:alice
document:readme#parent@folder:root

// Permission defined by union/intersection of relations
definition document {
    relation owner: user
    relation editor: user | team#member
    relation viewer: user | team#member

    permission can_edit = owner + editor
    permission can_view = can_edit + viewer + parent->can_view
}

definition folder {
    relation owner: user
    relation viewer: user | team#member

    permission can_view = owner + viewer
}
```

**Zanzibar permission check as graph traversal:**

```mermaid
flowchart TD
    Q["Can Bob view document:readme?"] --> C1{"Bob is owner<br/>of document:readme?"}
    C1 -->|No| C2{"Bob is editor<br/>of document:readme?"}
    C2 -->|No| C3{"Bob is viewer<br/>of document:readme?"}
    C3 -->|No| C4{"Bob is member of a team<br/>that is viewer?"}
    C4 -->|Check| T1["team:engineering#member@user:bob"]
    T1 -->|Yes, Bob is member| C5{"team:engineering is viewer<br/>of document:readme?"}
    C5 -->|Yes| PERMIT[PERMIT]
    C3 -->|Direct match| PERMIT
```

### 2.3.3 Zanzibar-Inspired Systems

| System | Description | Use Case |
|--------|-------------|----------|
| **Authzed / SpiceDB** | Open-source, Zanzibar-inspired. gRPC API. Stores relation tuples and evaluates permission checks. | General-purpose ReBAC for any application |
| **Ory Keto** | Open-source, Zanzibar-inspired. REST and gRPC APIs. | Cloud-native authorization |
| **OpenFGA** | Open-source (by Auth0/Okta). Simple DSL for defining authorization models. | SaaS multi-tenant authorization |
| **Topaz** | Open-source (by Aserto). Combines OPA policies with Zanzibar-style directory. | Hybrid ABAC+ReBAC |

### 2.3.4 ReBAC Performance

Zanzibar achieves low-latency checks through:

1. **Caching** — heavily cached relation tuples (the "leopard" indexing system).
2. **Check request fanout** — parallel graph traversal with early termination on first PERMIT path.
3. **Zookies** — consistency tokens that encode a snapshot of the relation tuple store, enabling "new enemy" problem protection (ensuring that a permission revocation is observed before subsequent checks).

**The "new enemy" problem:** If Alice removes Bob's access to a document, and Bob's next access check is served from a stale cache, Bob might still be allowed access. Zanzibar solves this with zookies — tokens that ensure reads are at least as fresh as a specified write.

### 2.3.5 When to Use ReBAC

| Signal | ReBAC is a good fit |
|--------|-------------------|
| Access is naturally based on sharing/ownership | Google Drive-style sharing |
| Permission inheritance follows a resource hierarchy | Folders → documents, orgs → teams → projects |
| You need fine-grained, per-resource access control | Per-document permissions |
| The access model has many-to-many relationships | Users ↔ teams ↔ projects ↔ resources |
| You need to answer "who has access to X?" efficiently | Compliance auditing, access reviews |

---

## 2.4 Policy Engines

### 2.4.1 Why Externalize Policy

Embedding authorization logic directly in application code creates several problems:
- **Scattered logic** — authorization checks spread across controllers, services, and queries.
- **Hard to audit** — no single place to review all access policies.
- **Coupled to code** — changing a policy requires a code deployment.
- **Inconsistent** — different services implement the same policy differently.

Policy engines solve this by **decoupling authorization decisions from application code**. The application asks the policy engine "is this allowed?" and the engine evaluates the request against a centralized set of policies.

### 2.4.2 Open Policy Agent (OPA)

OPA is a general-purpose policy engine that uses a declarative language called **Rego** to define policies. OPA is CNCF-graduated and widely used for Kubernetes admission control, API authorization, and infrastructure policies.

**OPA architecture:**

```mermaid
flowchart LR
    subgraph Application
        SVC[Service]
    end
    subgraph OPA
        RE[Rego Engine]
        PD[Policy Data<br/>JSON/YAML]
        PB[Policy Bundle<br/>Rego files]
    end
    subgraph External
        BS[Bundle Server<br/>Git / S3]
    end

    SVC -->|"POST /v1/data/authz/allow<br/>{input: {...}}"| RE
    RE --> PD
    RE --> PB
    BS -->|Pull bundles| PB
    RE -->|"true/false + reasons"| SVC
```

**Example Rego policy:**

```rego
package authz

import future.keywords.if
import future.keywords.in

default allow := false

# Admins can do anything
allow if {
    "admin" in input.user.roles
}

# Users can read their own orders
allow if {
    input.action == "read"
    input.resource.type == "order"
    input.resource.owner_id == input.user.id
}

# Managers can read orders in their department
allow if {
    input.action == "read"
    input.resource.type == "order"
    input.user.department == input.resource.department
    "manager" in input.user.roles
}

# Deny access outside business hours for non-admins
deny if {
    not "admin" in input.user.roles
    not is_business_hours
}

is_business_hours if {
    now := time.now_ns()
    hour := time.clock(now)[0]
    hour >= 8
    hour < 18
}
```

**OPA deployment patterns:**

| Pattern | Description | Latency | Best For |
|---------|-------------|---------|----------|
| **Sidecar** | OPA runs as a sidecar container next to the service | <1ms | Kubernetes deployments |
| **Library** | OPA embedded as a Go library in the application | <0.1ms | Go services requiring minimal latency |
| **Daemon** | OPA runs as a host-level daemon shared by multiple services | <2ms | VM-based deployments |
| **Central server** | OPA runs as a shared service | 5-50ms | Simple deployments, development |

### 2.4.3 Cedar

Cedar is a policy language created by AWS, used in Amazon Verified Permissions and AWS-managed services. Cedar is designed to be analyzable — policies can be statically checked for consistency and completeness.

**Example Cedar policy:**

```cedar
// Permit editors to update articles in their department
permit (
    principal in Group::"editors",
    action in [Action::"update", Action::"publish"],
    resource in Department::"engineering"
) when {
    principal.department == resource.department &&
    resource.status != "archived"
};

// Forbid access from untrusted networks
forbid (
    principal,
    action,
    resource
) when {
    !context.network in IpRange::"10.0.0.0/8"
};
```

**Cedar advantages over Rego:**
- Simpler syntax designed specifically for authorization (Rego is general-purpose).
- Static analysis can prove policy properties (e.g., "no two policies conflict").
- Built-in support for hierarchical principal and resource types.

### 2.4.4 Casbin

Casbin is a lightweight, embeddable authorization library supporting multiple models (RBAC, ABAC, ReBAC) through a configurable model file.

**Casbin model definition:**

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _
g2 = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && g2(r.obj, p.obj) && r.act == p.act
```

**Casbin vs OPA vs Cedar:**

| Feature | Casbin | OPA | Cedar |
|---------|--------|-----|-------|
| **Language** | Model + policy CSV | Rego | Cedar |
| **Deployment** | Embedded library | Sidecar/daemon/library | AWS service / library |
| **Flexibility** | High (configurable model) | Very high (general-purpose) | Medium (authorization-focused) |
| **Performance** | Very fast (in-process) | Fast (<1ms sidecar) | Fast |
| **Static analysis** | Limited | Limited | Strong |
| **Ecosystem** | 16+ language adapters | CNCF graduated, wide adoption | AWS native |

---

## 2.5 Row-Level Security

### 2.5.1 What Row-Level Security Is

Row-Level Security (RLS) enforces access control at the database level. Instead of relying on application code to filter data, the database automatically restricts which rows a query can see based on the user's identity.

**Why RLS matters:**
- **Defense in depth** — even if application-level authorization has a bug, the database enforces access control.
- **Centralized enforcement** — all queries (application, reporting tools, admin consoles) go through the same RLS policies.
- **Multi-tenant isolation** — RLS is the most reliable way to prevent data leakage between tenants in a shared database.

### 2.5.2 PostgreSQL RLS Example

```sql
-- Enable RLS on the orders table
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own orders
CREATE POLICY user_orders_policy ON orders
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id')::uuid);

-- Policy: Admins can see all orders
CREATE POLICY admin_orders_policy ON orders
    FOR ALL
    USING (current_setting('app.current_user_role') = 'admin');

-- Policy: Tenant isolation (multi-tenant)
CREATE POLICY tenant_isolation ON orders
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Set the context before queries (typically in a connection pool wrapper)
-- SET app.current_user_id = 'user-12345';
-- SET app.current_tenant_id = 'tenant-789';
-- SET app.current_user_role = 'editor';
```

### 2.5.3 Multi-Tenant Isolation Strategies

| Strategy | Description | Isolation Level | Cost |
|----------|-------------|----------------|------|
| **Separate databases** | Each tenant gets its own database instance | Strongest | Highest (one DB per tenant) |
| **Separate schemas** | Each tenant gets a schema within a shared database | Strong | Moderate |
| **Shared table + RLS** | All tenants share tables; RLS enforces isolation | Adequate | Lowest |
| **Shared table + application filter** | Application adds `WHERE tenant_id = ?` to every query | Weakest (bug-prone) | Lowest |

**The `WHERE tenant_id = ?` approach is dangerous** because a single missing filter in any query leaks data across tenants. RLS eliminates this class of bug entirely — the database enforces the filter even if the application code forgets it.

### 2.5.4 RLS Performance Considerations

- RLS adds a predicate to every query, which can impact query performance. Index the columns used in RLS policies (`user_id`, `tenant_id`).
- Complex RLS policies with subqueries can cause performance degradation. Keep policies simple and test query plans.
- RLS policies are evaluated per-row, which can be expensive for large result sets. Consider materialized views or pre-filtered tables for reporting workloads.
- Connection pool context management adds slight overhead — ensure the context is set before each query and cleared after (to prevent tenant leakage across pooled connections).

---

# Section 3: Infrastructure Security

Infrastructure security protects the foundational layers that applications run on: data at rest and in transit, secrets and credentials, network traffic, and the availability of services under attack. These controls are invisible to end users but catastrophic when absent.

---

## 3.1 Encryption

### 3.1.1 Encryption at Rest

Encryption at rest protects data stored on disk — databases, file systems, object stores, backups. If physical media is stolen or a database dump is exfiltrated, encryption at rest renders the data unreadable without the encryption key.

**AES-256-GCM** is the industry standard for encryption at rest:
- **AES** — Advanced Encryption Standard, a symmetric block cipher.
- **256** — 256-bit key length, providing ~128 bits of security against brute force.
- **GCM** — Galois/Counter Mode, providing authenticated encryption (confidentiality + integrity).

**Storage-level encryption tiers:**

| Tier | What Is Encrypted | Managed By | Protects Against |
|------|-------------------|-----------|-----------------|
| **Full-disk encryption** | Entire disk volume | OS / cloud provider (EBS encryption, BitLocker) | Physical theft, decommissioned hardware |
| **Database encryption (TDE)** | Database files on disk | Database engine (PostgreSQL, MySQL) | Physical theft, stolen backups |
| **Application-level encryption** | Individual fields/columns | Application code | Unauthorized DB access, insider threats |
| **Client-side encryption** | Data before upload | Client application | Server compromise, provider access |

### 3.1.2 Envelope Encryption

Envelope encryption is a pattern where data is encrypted with a **data encryption key (DEK)**, and the DEK itself is encrypted with a **key encryption key (KEK)**. The encrypted DEK is stored alongside the data.

```mermaid
flowchart TD
    subgraph KMS [Key Management Service]
        KEK[Key Encryption Key<br/>KEK — never leaves KMS]
    end
    subgraph Application
        PT[Plaintext Data]
        DEK[Data Encryption Key<br/>Generated per record/file]
        CT[Ciphertext]
        EDEK[Encrypted DEK]
    end

    DEK -->|Encrypt data| CT
    PT --> CT
    KEK -->|Encrypt DEK| EDEK

    Note1[Stored together: Ciphertext + Encrypted DEK]
```

**Why envelope encryption?**
1. **Performance** — encrypting large data with a symmetric DEK is fast. Only the small DEK needs to be encrypted with the KMS (which may involve a network call).
2. **Key rotation** — rotating the KEK only requires re-encrypting the DEKs, not re-encrypting all data.
3. **Isolation** — different data sets use different DEKs. Compromising one DEK does not expose other data.
4. **KMS limits** — cloud KMS services have rate limits on encrypt/decrypt operations. Envelope encryption minimizes KMS calls.

### 3.1.3 Encryption in Transit

Encryption in transit protects data moving between systems — browser to server, service to service, server to database.

**TLS 1.3** is the current standard:
- Reduced handshake to 1-RTT (from 2-RTT in TLS 1.2).
- 0-RTT resumption for repeat connections (with replay protection caveats).
- Removed insecure cipher suites (RC4, 3DES, SHA-1, static RSA key exchange).
- Forward secrecy is mandatory (all key exchanges use ephemeral Diffie-Hellman).

**TLS termination points:**

| Pattern | TLS terminates at | Internal traffic | Use case |
|---------|-------------------|-----------------|----------|
| **Edge termination** | Load balancer / CDN | Plaintext or re-encrypted | Most web applications |
| **End-to-end** | Application server | TLS everywhere | High-security, zero trust |
| **Service mesh** | Sidecar proxy (Envoy) | mTLS between all services | Kubernetes, microservices |
| **Passthrough** | Application server | Load balancer does not inspect | When LB cannot hold certificates |

### 3.1.4 Application-Level Encryption

Application-level encryption encrypts specific fields before they reach the database. This protects against:
- Database administrators reading sensitive data.
- SQL injection attacks that dump table contents.
- Backup exposure (backups contain ciphertext, not plaintext).

**Example — encrypting PII fields:**

```python
from cryptography.fernet import Fernet

class UserService:
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)

    def create_user(self, email: str, ssn: str):
        # Encrypt sensitive fields before storage
        encrypted_ssn = self.cipher.encrypt(ssn.encode())

        # Store in database
        db.execute(
            "INSERT INTO users (email, encrypted_ssn, ssn_hash) VALUES (?, ?, ?)",
            email,
            encrypted_ssn,
            sha256(ssn)  # searchable hash for lookups
        )

    def get_user_ssn(self, user_id: str) -> str:
        row = db.execute("SELECT encrypted_ssn FROM users WHERE id = ?", user_id)
        return self.cipher.decrypt(row.encrypted_ssn).decode()
```

**Searchable encryption challenge:** If a field is encrypted, you cannot query it with `WHERE ssn = '123-45-6789'`. Solutions include:
- Store a keyed hash alongside the ciphertext for equality lookups.
- Use deterministic encryption (same plaintext always produces same ciphertext) — enables equality search but leaks frequency information.
- Use searchable encryption schemes (e.g., CipherSweet) for prefix/range queries.

### 3.1.5 Key Rotation

Key rotation limits the exposure window if a key is compromised. A well-designed key rotation strategy:

1. **Generate new key version** — create a new key while keeping the old one active for decryption.
2. **Encrypt new data with new key** — all new writes use the latest key version.
3. **Re-encrypt existing data** — gradually re-encrypt old data with the new key (background job).
4. **Retire old key** — once all data is re-encrypted, disable the old key version.
5. **Destroy old key** — after a retention period, permanently delete the old key.

**Key rotation frequency:**

| Data Sensitivity | Rotation Frequency |
|-----------------|-------------------|
| Regulatory (PCI-DSS) | Annual or more frequent |
| High sensitivity (PII, health data) | Quarterly |
| Standard business data | Annual |
| Infrastructure keys (TLS certificates) | 90 days (Let's Encrypt default) |
| Signing keys | Annual, with overlap period |

---

## 3.2 Secrets Management

### 3.2.1 The Secrets Problem

Secrets — database passwords, API keys, TLS certificates, encryption keys, service account credentials — are the keys to the kingdom. Mismanaged secrets are the root cause of many breaches:

- Secrets hardcoded in source code are visible in version control history.
- Secrets in environment variables are exposed through process listings, debug endpoints, and crash dumps.
- Secrets in configuration files are copied to developer machines, CI/CD systems, and backup tapes.
- Secrets that are never rotated accumulate risk over time.

### 3.2.2 HashiCorp Vault

Vault is the most widely deployed dedicated secrets management system. It provides:

**Core capabilities:**

| Capability | Description |
|------------|------------|
| **Static secrets** | Key/value store for arbitrary secrets with versioning and access control |
| **Dynamic secrets** | On-demand, short-lived credentials (e.g., database credentials created per request and automatically revoked) |
| **Encryption as a service** | Transit engine provides encrypt/decrypt/sign/verify without exposing keys |
| **PKI** | Issues X.509 certificates from an internal CA |
| **Authentication** | Multiple auth methods (Kubernetes, AWS IAM, OIDC, AppRole) |
| **Audit** | Complete audit log of every secret access |

```mermaid
flowchart TD
    subgraph Applications
        SVC1[Service A]
        SVC2[Service B]
        CI[CI/CD Pipeline]
    end
    subgraph Vault
        AUTH[Auth Backend<br/>K8s / AWS / AppRole]
        SE[Secrets Engine<br/>KV / Dynamic / Transit]
        AUDIT[Audit Log]
        POLICY[Access Policies]
    end
    subgraph Targets
        DB[(Database)]
        CLOUD[Cloud APIs]
    end

    SVC1 -->|Authenticate| AUTH
    AUTH -->|Check policy| POLICY
    POLICY -->|Authorized| SE
    SE -->|Dynamic credential| SVC1
    SVC1 -->|Short-lived creds| DB
    SE -->|Rotate credentials| DB
    AUTH -->|Log access| AUDIT
```

**Dynamic secrets** are Vault's most powerful feature. Instead of storing a static database password that never changes, Vault:
1. Creates a new database user with a unique password for each requesting service.
2. Sets a TTL (e.g., 1 hour) on the credential.
3. Automatically revokes the credential when the TTL expires.
4. If a credential is compromised, the blast radius is limited to one service for a short time.

### 3.2.3 AWS Secrets Manager

AWS Secrets Manager is a managed service for storing and rotating secrets in AWS environments:

| Feature | Description |
|---------|------------|
| **Automatic rotation** | Lambda-based rotation for RDS, Redshift, DocumentDB |
| **Cross-account access** | Share secrets across AWS accounts via resource policies |
| **Versioning** | Maintain previous, current, and pending secret versions |
| **Encryption** | Secrets encrypted with AWS KMS (customer-managed or service-managed keys) |
| **Caching** | Client-side caching SDK to reduce API calls and latency |

### 3.2.4 Secrets Rotation Strategies

| Strategy | Description | Complexity |
|----------|-------------|-----------|
| **Single-user rotation** | Update the secret in place; brief window of invalid credentials | Low |
| **Alternating users** | Maintain two credential sets; rotate one while the other is active | Medium |
| **Dynamic provisioning** | Create new credentials on demand; revoke when done (Vault dynamic secrets) | High |
| **Dual-write** | Update the secret in the secrets manager and the target simultaneously | Medium |

**Alternating user rotation (recommended for databases):**

```
Phase 1: user_a is active, user_b is standby
Phase 2: Rotate user_b's password
Phase 3: Switch active to user_b
Phase 4: Rotate user_a's password
Phase 5: user_b is active, user_a is standby
```

This ensures there is always a valid credential available during rotation.

### 3.2.5 Zero-Trust Secret Distribution

In a zero-trust model, secrets are not distributed at deployment time. Instead:

1. **Identity-based access** — the service authenticates to the secrets manager using its own identity (Kubernetes service account, AWS IAM role, mTLS certificate).
2. **Just-in-time retrieval** — secrets are fetched at runtime, not baked into configuration files or container images.
3. **Short-lived credentials** — credentials expire quickly and must be refreshed, limiting the blast radius of compromise.
4. **No persistent storage** — secrets are held in memory only and never written to disk.

---

## 3.3 Rate Limiting

### 3.3.1 Why Rate Limiting Matters

Rate limiting controls how many requests a client can make in a given time window. It protects against:
- **Abuse** — credential stuffing, scraping, spam.
- **DDoS** — volumetric attacks that overwhelm the system.
- **Cost control** — preventing a single client from consuming disproportionate resources.
- **Fairness** — ensuring no single client starves others of capacity.

### 3.3.2 Rate Limiting Dimensions

| Dimension | Identified By | Use Case |
|-----------|--------------|----------|
| **Per-IP** | Source IP address | Anonymous abuse prevention |
| **Per-user** | Authenticated user ID | Fair usage enforcement |
| **Per-API-key** | API key header | Usage-based billing, plan enforcement |
| **Per-endpoint** | Request path + method | Protecting expensive endpoints |
| **Per-tenant** | Organization/tenant ID | Multi-tenant resource isolation |
| **Global** | Total system throughput | System protection under load |

### 3.3.3 Token Bucket Algorithm

The token bucket is the most widely used rate limiting algorithm. It allows bursts while enforcing an average rate.

**How it works:**

1. A bucket holds tokens with a maximum capacity (burst size).
2. Tokens are added at a fixed rate (refill rate).
3. Each request consumes one token.
4. If the bucket is empty, the request is rejected (429 Too Many Requests).

```python
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity          # max tokens (burst size)
        self.refill_rate = refill_rate    # tokens per second
        self.tokens = capacity            # current tokens
        self.last_refill = time.time()

    def allow_request(self) -> bool:
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```

**Token bucket parameters:**

| Parameter | Meaning | Example |
|-----------|---------|---------|
| `capacity` | Maximum burst size | 100 (allows 100 requests at once) |
| `refill_rate` | Sustained rate | 10/sec (10 requests per second steady state) |

### 3.3.4 Other Rate Limiting Algorithms

| Algorithm | Behavior | Pros | Cons |
|-----------|----------|------|------|
| **Fixed window** | Count requests per fixed time window (e.g., per minute) | Simple to implement | Burst at window boundary (2x rate) |
| **Sliding window log** | Track exact timestamp of each request; count within window | Precise | Memory-intensive (stores all timestamps) |
| **Sliding window counter** | Interpolate between current and previous window counts | Good balance | Approximate (not exact) |
| **Token bucket** | Tokens accumulate; requests consume tokens | Allows bursts; smooth rate | Slightly more complex |
| **Leaky bucket** | Requests enter a queue; processed at fixed rate | Smooth output rate | No burst capability |

### 3.3.5 Distributed Rate Limiting

In a distributed system with multiple server instances, rate limiting must be coordinated. A user hitting different servers should not get N times the rate limit.

**Redis-based distributed rate limiting:**

```lua
-- Redis Lua script for sliding window rate limiting
-- KEYS[1] = rate limit key (e.g., "ratelimit:user:12345")
-- ARGV[1] = window size in milliseconds
-- ARGV[2] = maximum requests per window
-- ARGV[3] = current timestamp in milliseconds
-- ARGV[4] = unique request ID

local key = KEYS[1]
local window = tonumber(ARGV[1])
local max_requests = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local request_id = ARGV[4]

-- Remove entries outside the window
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

-- Count current requests in window
local current = redis.call('ZCARD', key)

if current < max_requests then
    -- Allow request
    redis.call('ZADD', key, now, request_id)
    redis.call('PEXPIRE', key, window)
    return {1, max_requests - current - 1}  -- allowed, remaining
else
    -- Reject request
    return {0, 0}  -- denied, remaining
end
```

**Rate limiting response headers:**

```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1711324860
Retry-After: 30
```

### 3.3.6 Rate Limiting in System Design Interviews

When discussing rate limiting in interviews, cover:
1. **Where** — API gateway (centralized) vs application middleware (per-service) vs both.
2. **Granularity** — which dimension(s) to rate limit on.
3. **Algorithm** — token bucket for most cases; explain the trade-offs.
4. **Storage** — Redis for distributed coordination.
5. **Response** — 429 status code, `Retry-After` header, rate limit headers.
6. **Graceful degradation** — if the rate limiter (Redis) is down, fail open (allow all) or fail closed (deny all)?

---

## 3.4 DDoS Protection

### 3.4.1 DDoS Attack Types

| Layer | Attack Type | Mechanism | Volume |
|-------|------------|-----------|--------|
| **L3/L4** (Network/Transport) | SYN flood | Overwhelm TCP handshake | Very high (Tbps) |
| **L3/L4** | UDP flood | Overwhelm with UDP packets | Very high |
| **L3/L4** | Amplification (DNS, NTP) | Exploit amplification factor of UDP services | Very high |
| **L7** (Application) | HTTP flood | Send legitimate-looking HTTP requests at high volume | Moderate |
| **L7** | Slowloris | Keep connections open with slow, partial requests | Low volume, high impact |
| **L7** | Application-specific | Target expensive endpoints (search, reports) | Low volume, high impact |

### 3.4.2 DDoS Mitigation Architecture

```mermaid
flowchart LR
    ATK[Attacker Traffic] --> CDN[CDN / DDoS Shield<br/>Cloudflare / AWS Shield]
    LEG[Legitimate Traffic] --> CDN
    CDN -->|L3/L4 filtering| WAF[WAF<br/>Rule-based filtering]
    WAF -->|L7 filtering| LB[Load Balancer]
    LB -->|Rate limiting| APP[Application]

    CDN -.->|Block| DROP1[Drop L3/L4 attacks]
    WAF -.->|Block| DROP2[Drop L7 attacks]
    LB -.->|Block| DROP3[Drop excess requests]
```

### 3.4.3 L3/L4 Protection

L3/L4 attacks are volumetric — they overwhelm network bandwidth and connection-handling capacity. Protection must happen at the network edge, before traffic reaches your infrastructure.

**Mitigation strategies:**
- **Anycast routing** — distribute traffic across multiple PoPs (points of presence) globally. Each PoP absorbs a fraction of the attack.
- **BGP blackholing** — route attack traffic to null, sacrificing the target IP but protecting the rest of the network.
- **Scrubbing centers** — route traffic through a DDoS scrubbing service that filters malicious packets and forwards clean traffic.
- **Cloud DDoS services** — AWS Shield Advanced, Cloudflare, Akamai Prolexic absorb volumetric attacks at their edge.

### 3.4.4 L7 Protection

L7 attacks are harder to detect because they use legitimate-looking HTTP requests. Protection involves:

**WAF (Web Application Firewall) rules:**
- Block known bot signatures.
- Rate limit by IP, user agent, and request pattern.
- Challenge suspicious requests with CAPTCHA or JavaScript challenges.
- Block requests with malicious payloads (SQL injection, XSS patterns).

**Behavioral analysis:**
- Detect abnormal request patterns (e.g., 1000 requests to `/search` in 1 minute from a single IP).
- Fingerprint clients based on TLS handshake, HTTP/2 settings, and header ordering (JA3 fingerprinting).
- Use machine learning models to distinguish bots from humans.

**Origin hiding:**
- Never expose the origin server's IP address. All traffic must flow through the CDN/DDoS protection layer.
- Use separate IPs for the origin server that are not discoverable via DNS history or certificate transparency logs.
- Restrict origin server access to only the CDN's IP ranges using security groups/firewall rules.

### 3.4.5 Challenge Pages

Challenge pages are interstitial pages that verify a client is a legitimate browser (not a bot) before granting access:

| Challenge Type | Mechanism | User Impact |
|---------------|-----------|-------------|
| **JavaScript challenge** | Browser must execute JavaScript and return a computed value | Invisible to users; blocks simple bots |
| **CAPTCHA** | User solves a visual puzzle | Visible friction; blocks sophisticated bots |
| **Proof-of-work** | Browser must compute a hash (crypto puzzle) | Slight delay; makes volumetric attacks expensive |
| **Managed challenge** | Cloudflare/AWS selects the least-intrusive challenge based on risk score | Adaptive friction |

---

# Section 4: Application Security

Application security protects the code itself — the inputs it accepts, the outputs it produces, the dependencies it relies on, and the trust boundaries it operates within. Infrastructure security is necessary but not sufficient; a perfectly encrypted network is useless if the application has a SQL injection vulnerability.

---

## 4.1 OWASP Top 10

The OWASP Top 10 is the most widely referenced list of critical web application security risks. This section covers the most architecturally significant entries with prevention patterns.

### 4.1.1 A01: Broken Access Control

Broken access control is the #1 vulnerability class. It occurs when the application fails to enforce who can access what.

**Common manifestations:**

| Vulnerability | Description | Example |
|--------------|-------------|---------|
| **IDOR** (Insecure Direct Object Reference) | User manipulates an ID to access another user's data | `GET /api/orders/12345` → change to `GET /api/orders/12346` |
| **Forced browsing** | Accessing admin pages by guessing URLs | `GET /admin/users` without admin role |
| **Privilege escalation** | Performing actions beyond your role | Regular user calls `DELETE /api/users/789` |
| **Missing function-level access control** | API endpoint lacks authorization check | Backend function accessible without any auth |
| **CORS misconfiguration** | Overly permissive CORS allows cross-origin data theft | `Access-Control-Allow-Origin: *` on authenticated endpoints |

**Prevention patterns:**
- Deny by default — every endpoint requires explicit authorization.
- Centralize access control — use middleware or a policy engine, not per-endpoint checks.
- Use indirect references — map internal IDs to user-scoped identifiers.
- Validate ownership on every request — `WHERE user_id = :current_user AND id = :requested_id`.
- Automated testing — include authorization bypass tests in CI/CD.

### 4.1.2 A02: Cryptographic Failures

Cryptographic failures expose sensitive data through weak or missing encryption.

**Common failures:**

| Failure | Impact | Prevention |
|---------|--------|-----------|
| Transmitting data over HTTP | Data intercepted in transit | Enforce HTTPS everywhere; HSTS header |
| Using MD5/SHA1 for passwords | Passwords cracked quickly | Use bcrypt, scrypt, or Argon2 |
| Hardcoded encryption keys | Key compromised if code leaks | Use KMS or secrets manager |
| Using ECB mode for AES | Patterns visible in ciphertext | Use GCM or CBC with HMAC |
| Weak random number generation | Predictable tokens/keys | Use cryptographically secure PRNG |
| Not encrypting PII at rest | Data exposed in breach | Application-level encryption for sensitive fields |

### 4.1.3 A03: Injection

Injection attacks insert malicious code into a query or command that is executed by the system.

**SQL Injection:**

```
-- Vulnerable: string concatenation
query = "SELECT * FROM users WHERE email = '" + user_input + "'"
-- Attack input: ' OR '1'='1' --
-- Resulting query: SELECT * FROM users WHERE email = '' OR '1'='1' --'

-- Secure: parameterized query
query = "SELECT * FROM users WHERE email = $1"
params = [user_input]
```

**NoSQL Injection:**

```json
// Vulnerable: MongoDB query from user input
{ "username": user_input, "password": user_input }

// Attack input for password: { "$ne": "" }
// Resulting query: { "username": "admin", "password": { "$ne": "" } }
// This matches any non-empty password — authentication bypassed

// Secure: validate and sanitize input types
```

**Command Injection:**

```python
# Vulnerable
os.system("ping " + user_input)
# Attack input: "8.8.8.8; rm -rf /"

# Secure: use parameterized APIs
subprocess.run(["ping", "-c", "1", user_input], shell=False)
```

**Prevention patterns (apply to ALL injection types):**
1. **Parameterized queries** — never concatenate user input into queries.
2. **ORMs** — use an ORM that generates parameterized queries.
3. **Input validation** — validate type, length, format, and range.
4. **Least privilege** — database users should have minimal permissions.
5. **WAF rules** — detect and block common injection patterns.

### 4.1.4 A04: Cross-Site Scripting (XSS)

XSS occurs when an attacker injects malicious JavaScript into a page that other users view.

**XSS types:**

| Type | Mechanism | Persistence |
|------|-----------|------------|
| **Stored XSS** | Malicious script is saved in the database and rendered to other users | Persistent — affects all viewers |
| **Reflected XSS** | Malicious script is reflected from the URL/request into the response | Non-persistent — requires victim to click a link |
| **DOM-based XSS** | Client-side JavaScript processes untrusted data into the DOM | Non-persistent — no server involvement |

**Prevention patterns:**
- **Output encoding** — encode all user-controlled data before rendering in HTML, JavaScript, CSS, or URL contexts.
- **Content Security Policy (CSP)** — restrict which scripts, styles, and resources the browser can load.
- **HttpOnly cookies** — prevent JavaScript from reading session cookies (reduces XSS impact).
- **Sanitization libraries** — use DOMPurify or similar for HTML that must allow some markup.
- **Framework escaping** — modern frameworks (React, Vue, Angular) auto-escape by default; avoid `dangerouslySetInnerHTML` and equivalents.

### 4.1.5 A05: Cross-Site Request Forgery (CSRF)

CSRF tricks a user's browser into making an unintended request to a site where they are authenticated. Because browsers automatically attach cookies, the request carries the user's session.

**CSRF attack flow:**

```mermaid
sequenceDiagram
    participant V as Victim's Browser
    participant E as Evil Site
    participant B as Bank (Victim is logged in)

    V->>E: 1. Visit evil site
    E->>V: 2. Page contains hidden form
    Note over E,V: <form action="bank.com/transfer" method="POST"><br/>  <input name="to" value="attacker"><br/>  <input name="amount" value="10000"><br/></form><br/><script>form.submit()</script>
    V->>B: 3. Browser auto-submits form with session cookie
    B->>B: 4. Bank processes transfer (valid session)
```

**Prevention patterns:**
- **SameSite cookies** — `SameSite=Lax` (default in modern browsers) prevents cookies from being sent on cross-origin POST requests.
- **CSRF tokens** — server generates a random token, embeds it in the form, and validates it on submission. The token is not in a cookie, so cross-origin requests cannot include it.
- **Double-submit cookie** — set a random value in both a cookie and a request header; verify they match (browsers prevent cross-origin sites from setting custom headers).
- **Origin/Referer header checking** — verify that the request origin matches the expected domain.

### 4.1.6 A06: Server-Side Request Forgery (SSRF)

SSRF occurs when an attacker tricks the server into making requests to unintended destinations — typically internal services, metadata endpoints, or external systems.

**SSRF attack scenarios:**

| Scenario | Target | Impact |
|----------|--------|--------|
| Cloud metadata endpoint | `http://169.254.169.254/latest/meta-data/` | Steal IAM credentials, access tokens |
| Internal services | `http://internal-admin.local/api/users` | Access internal APIs not exposed to the internet |
| Port scanning | `http://10.0.0.1:22`, `http://10.0.0.1:3306` | Discover internal network topology |
| File read | `file:///etc/passwd` | Read server files |

**Prevention patterns:**
- **Allow-list URLs/domains** — only permit requests to known, safe destinations.
- **Block private IP ranges** — reject requests to `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`, `127.0.0.0/8`.
- **Disable URL redirects** — an attacker can use a redirect to bypass allow-list checks.
- **Use a dedicated egress proxy** — route all outbound requests through a proxy that enforces destination restrictions.
- **IMDSv2** — require token-based access to cloud metadata endpoints (mitigates SSRF against metadata).

---

## 4.2 Input Validation

### 4.2.1 Allow-List vs Deny-List

| Approach | Definition | Effectiveness |
|----------|-----------|--------------|
| **Allow-list** (whitelist) | Define exactly what is valid; reject everything else | Strong — unknown inputs are rejected |
| **Deny-list** (blacklist) | Define what is invalid; allow everything else | Weak — attackers find inputs not on the list |

**Always prefer allow-list validation.** Deny-lists are inherently incomplete because you cannot enumerate all possible attack payloads.

**Examples:**

```python
# Allow-list: only accept expected values
VALID_SORT_FIELDS = {"name", "date", "price", "rating"}

def validate_sort_field(field: str) -> str:
    if field not in VALID_SORT_FIELDS:
        raise ValidationError(f"Invalid sort field: {field}")
    return field

# Allow-list: regex for expected format
import re
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email: str) -> str:
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Invalid email format")
    if len(email) > 254:
        raise ValidationError("Email too long")
    return email.lower()
```

### 4.2.2 Parameterized Queries

Parameterized queries (prepared statements) separate SQL code from data, making SQL injection impossible regardless of user input:

```python
# VULNERABLE — string concatenation
cursor.execute(f"SELECT * FROM products WHERE category = '{user_input}'")

# SECURE — parameterized query
cursor.execute("SELECT * FROM products WHERE category = %s", (user_input,))

# SECURE — ORM (SQLAlchemy)
products = session.query(Product).filter(Product.category == user_input).all()

# SECURE — query builder (Knex.js)
# knex('products').where('category', user_input)
```

### 4.2.3 Content Security Policy (CSP)

CSP is an HTTP response header that tells the browser which sources of content are trusted. It is the most effective defense against XSS after output encoding.

**CSP header example:**

```
Content-Security-Policy:
    default-src 'self';
    script-src 'self' https://cdn.example.com;
    style-src 'self' 'unsafe-inline';
    img-src 'self' https: data:;
    connect-src 'self' https://api.example.com;
    font-src 'self' https://fonts.googleapis.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
    upgrade-insecure-requests;
```

**CSP directives:**

| Directive | Controls | Example |
|-----------|---------|---------|
| `default-src` | Fallback for all resource types | `'self'` |
| `script-src` | JavaScript sources | `'self' https://cdn.example.com` |
| `style-src` | CSS sources | `'self' 'unsafe-inline'` |
| `img-src` | Image sources | `'self' https: data:` |
| `connect-src` | XHR, WebSocket, Fetch destinations | `'self' https://api.example.com` |
| `frame-ancestors` | Who can embed this page in an iframe | `'none'` (prevents clickjacking) |
| `base-uri` | Restricts `<base>` element | `'self'` |
| `form-action` | Form submission destinations | `'self'` |
| `report-uri` / `report-to` | Where to send CSP violation reports | URL of your reporting endpoint |

**CSP deployment strategy:**
1. Start with `Content-Security-Policy-Report-Only` to monitor violations without breaking functionality.
2. Analyze violation reports to identify legitimate sources that need to be allowed.
3. Iteratively tighten the policy.
4. Switch to enforcement mode (`Content-Security-Policy`).
5. Maintain and update as the application evolves.

---

## 4.3 Secure Development Lifecycle

### 4.3.1 Threat Modeling with STRIDE

Threat modeling is the practice of systematically identifying threats to a system before they are exploited. **STRIDE** is a framework that categorizes threats into six types:

| Category | Threat | Example | Mitigation |
|----------|--------|---------|-----------|
| **S**poofing | Pretending to be someone else | Forged authentication token | Strong authentication, token validation |
| **T**ampering | Modifying data without authorization | Altering a price in an API request | Input validation, integrity checks, HMAC |
| **R**epudiation | Denying an action occurred | User claims they did not place an order | Audit logging, digital signatures |
| **I**nformation Disclosure | Exposing data to unauthorized parties | Stack trace in error response | Error handling, encryption, access control |
| **D**enial of Service | Making a system unavailable | Exhausting connection pool with slow requests | Rate limiting, timeouts, resource limits |
| **E**levation of Privilege | Gaining permissions beyond what is authorized | Regular user accessing admin API | Authorization checks, least privilege |

**Threat modeling process:**

```mermaid
flowchart LR
    A[1. Identify Assets<br/>What are we protecting?] --> B[2. Create Architecture Diagram<br/>Data flow diagram with trust boundaries]
    B --> C[3. Identify Threats<br/>Apply STRIDE to each component]
    C --> D[4. Assess Risk<br/>Likelihood x Impact]
    D --> E[5. Prioritize Mitigations<br/>Address highest risk first]
    E --> F[6. Validate<br/>Verify mitigations are effective]
    F --> A
```

### 4.3.2 Security Reviews

**Code review security checklist:**

| Category | Check |
|----------|-------|
| **Authentication** | All endpoints require authentication (unless explicitly public) |
| **Authorization** | Every data access checks ownership or permissions |
| **Input validation** | All user input is validated and sanitized |
| **Output encoding** | All output is properly encoded for its context |
| **Error handling** | No sensitive data in error messages or stack traces |
| **Logging** | Security events are logged (login, access denied, data changes) |
| **Secrets** | No hardcoded secrets, API keys, or passwords |
| **Dependencies** | No known vulnerable dependencies |
| **HTTPS** | All external communication uses TLS |
| **Headers** | Security headers are set (CSP, HSTS, X-Content-Type-Options) |

### 4.3.3 Dependency Scanning

Modern applications have hundreds of transitive dependencies. A single vulnerable dependency can compromise the entire system.

**Dependency scanning tools:**

| Tool | Ecosystem | Features |
|------|-----------|---------|
| **Dependabot** (GitHub) | All major languages | Automated PRs for vulnerable dependencies |
| **Snyk** | All major languages | Vulnerability database, fix suggestions, CI integration |
| **npm audit** | Node.js | Built-in vulnerability scanning |
| **OWASP Dependency-Check** | Java, .NET | OWASP project, NVD database |
| **Trivy** | Containers, IaC, languages | Multi-target scanning, CI-friendly |
| **Grype** | Containers | Anchore-backed, fast container scanning |

**Dependency management practices:**
- Run dependency scans in CI/CD — fail the build on high/critical vulnerabilities.
- Pin dependency versions — avoid surprise updates that introduce vulnerabilities.
- Maintain a Software Bill of Materials (SBOM) — know exactly what is in your deployment.
- Monitor for new vulnerabilities — subscribe to security advisories for critical dependencies.
- Have a patch SLA — critical vulnerabilities must be patched within 24-72 hours.

### 4.3.4 Security Headers

| Header | Value | Purpose |
|--------|-------|---------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Force HTTPS for 1 year |
| `Content-Security-Policy` | (see CSP section) | Control allowed content sources |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME-type sniffing |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Prevent clickjacking |
| `X-XSS-Protection` | `0` | Disable legacy XSS filter (can cause issues; rely on CSP instead) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referer header leakage |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disable browser features not needed |
| `Cache-Control` | `no-store` (for sensitive pages) | Prevent caching of sensitive data |

---

## 4.4 Zero Trust Architecture

### 4.4.1 Zero Trust Principles

Zero trust is a security model that assumes no implicit trust based on network location. Every request must be authenticated, authorized, and encrypted — regardless of whether it originates from inside or outside the network perimeter.

**Core principles:**

| Principle | Traditional (Perimeter) | Zero Trust |
|-----------|------------------------|------------|
| **Network trust** | Internal network is trusted | No network is trusted |
| **Authentication** | Once at the perimeter | Every request, every service |
| **Authorization** | Broad access after VPN | Least privilege, per-resource |
| **Encryption** | At the perimeter (TLS termination) | End-to-end, including internal |
| **Segmentation** | Flat internal network | Micro-segmented |
| **Monitoring** | Perimeter logs | All traffic logged and analyzed |

### 4.4.2 Zero Trust Architecture Components

```mermaid
flowchart TD
    subgraph User
        DEV[Device]
    end
    subgraph Control Plane
        IAP[Identity-Aware Proxy]
        IDP[Identity Provider]
        PE[Policy Engine]
        DT[Device Trust<br/>Posture Check]
    end
    subgraph Data Plane
        SVC1[Service A]
        SVC2[Service B]
        DB[(Database)]
    end

    DEV -->|1. Request| IAP
    IAP -->|2. Authenticate| IDP
    IAP -->|3. Check device posture| DT
    IAP -->|4. Evaluate policy| PE
    PE -->|5. PERMIT| IAP
    IAP -->|6. Proxy request with identity context| SVC1
    SVC1 -->|7. mTLS + identity header| SVC2
    SVC2 -->|8. Identity-scoped query| DB
```

### 4.4.3 Micro-Segmentation

Micro-segmentation divides the network into small, isolated segments. Each service can only communicate with explicitly allowed peers — eliminating lateral movement for attackers.

**Implementation approaches:**

| Approach | Mechanism | Granularity |
|----------|-----------|-------------|
| **Network policies** (Kubernetes) | NetworkPolicy resources restrict pod-to-pod traffic | Pod / namespace level |
| **Service mesh** (Istio, Linkerd) | mTLS + authorization policies between services | Service level |
| **Firewall rules** (Security Groups) | Cloud provider network rules | Instance / subnet level |
| **Software-defined networking** | Overlay networks with microsegmentation (VMware NSX, Calico) | Workload level |

**Kubernetes NetworkPolicy example:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: order-service-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: order-service
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api-gateway
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: inventory-service
      ports:
        - protocol: TCP
          port: 8080
    - to:
        - podSelector:
            matchLabels:
              app: payment-service
      ports:
        - protocol: TCP
          port: 8080
    - to:
        - namespaceSelector:
            matchLabels:
              name: database
      ports:
        - protocol: TCP
          port: 5432
```

### 4.4.4 Identity-Aware Proxy (IAP)

An identity-aware proxy sits in front of applications and enforces authentication and authorization before any request reaches the application. The application itself does not need to implement authentication — it trusts the proxy's identity headers.

**IAP implementations:**

| Product | Provider | Features |
|---------|----------|----------|
| **Google Cloud IAP** | GCP | Integrates with Google identity, context-aware access |
| **Azure AD Application Proxy** | Azure | On-premises app access without VPN |
| **Pomerium** | Open-source | Identity-aware proxy with policy engine |
| **oauth2-proxy** | Open-source | OAuth2/OIDC authentication proxy |
| **Boundary** | HashiCorp | Session-based access to infrastructure |

### 4.4.5 Zero Trust for APIs

In a zero-trust API architecture:

1. **Every API call carries identity** — JWTs, mTLS certificates, or signed requests.
2. **Every service validates identity** — no service trusts another service implicitly.
3. **Every service checks authorization** — the calling service's identity is checked against the resource being accessed.
4. **All traffic is encrypted** — mTLS between all services, even within the same data center.
5. **All access is logged** — every API call is recorded for audit and anomaly detection.

### 4.4.6 Zero Trust Architecture Deep Dive — Maturity Model

Organizations do not adopt zero trust overnight. A maturity model provides a phased approach:

| Maturity Level | Identity | Device | Network | Workload | Data | Monitoring |
|----------------|----------|--------|---------|----------|------|------------|
| **Level 0 — Traditional** | Passwords only | No posture checks | Flat network, VPN | Implicit trust between services | Encryption at rest only | Perimeter logs only |
| **Level 1 — Initial** | MFA for external access | Basic device inventory | Network segmentation by zone | Service accounts with static credentials | TLS in transit | Centralized logging |
| **Level 2 — Advanced** | MFA everywhere, SSO | Device posture checks, MDM | Micro-segmentation, NetworkPolicies | mTLS between services, short-lived creds | Application-level encryption for PII | SIEM with anomaly detection |
| **Level 3 — Optimal** | Passwordless (FIDO2), continuous auth | Real-time device health, compliance enforcement | Identity-based segmentation, no VPN | Per-request authorization (OPA), SPIFFE identities | Field-level encryption, tokenization | ML-driven threat detection, automated response |

### 4.4.7 SPIFFE/SPIRE — Workload Identity

SPIFFE (Secure Production Identity Framework for Everyone) provides a standard for issuing cryptographic identities to workloads in distributed systems. SPIRE is the reference implementation.

**How SPIFFE works:**

```mermaid
sequenceDiagram
    participant W as Workload (Pod)
    participant SA as SPIRE Agent (Node)
    participant SS as SPIRE Server
    participant CA as Certificate Authority

    W->>SA: 1. Request SVID (via Unix domain socket)
    SA->>SA: 2. Attest workload identity (k8s pod info, Docker labels)
    SA->>SS: 3. Request signing of SVID
    SS->>CA: 4. Sign X.509 certificate
    CA->>SS: 5. Signed certificate
    SS->>SA: 6. Return SVID
    SA->>W: 7. Issue X.509-SVID or JWT-SVID

    Note over W: SVID format: spiffe://trust-domain/workload-path
    Note over W: Example: spiffe://example.com/ns/prod/sa/order-service

    W->>W: 8. Use SVID for mTLS to other workloads
```

**SPIFFE Verifiable Identity Document (SVID):**

| SVID Type | Format | Use Case |
|-----------|--------|----------|
| **X.509-SVID** | X.509 certificate with SPIFFE ID in SAN | mTLS between workloads |
| **JWT-SVID** | JWT with SPIFFE ID as `sub` claim | API authentication, proxied connections |

**SPIRE attestation methods:**

```yaml
# SPIRE Server configuration for Kubernetes attestation
server {
  trust_domain = "example.com"
  bind_address = "0.0.0.0"
  bind_port = "8081"
}

plugins {
  NodeAttestor "k8s_psat" {
    plugin_data {
      clusters = {
        "production" = {
          service_account_allow_list = ["spire:spire-agent"]
        }
      }
    }
  }

  WorkloadAttestor "k8s" {
    plugin_data {
      # Attest based on Kubernetes pod metadata
    }
  }

  KeyManager "disk" {
    plugin_data {
      keys_path = "/run/spire/data/keys.json"
    }
  }
}
```

### 4.4.8 Zero Trust Network Access (ZTNA) vs VPN

| Dimension | Traditional VPN | ZTNA |
|-----------|----------------|------|
| **Access model** | Network-level access to entire subnet | Per-application access |
| **Authentication** | Once at connection time | Per-session, continuous evaluation |
| **Visibility** | User sees all network resources | User sees only authorized applications |
| **Lateral movement** | Full network access after connection | No lateral movement possible |
| **Split tunneling** | Complex configuration | Built-in application routing |
| **Device posture** | Rarely enforced | Required for every connection |
| **Scalability** | VPN concentrator bottleneck | Cloud-native, distributed |
| **User experience** | VPN client, manual connect | Transparent, always-on |

**ZTNA architecture with BeyondCorp model:**

```mermaid
flowchart LR
    subgraph User_Context["User Context"]
        U[User + Device]
        DC[Device Certificate]
        DP[Device Posture Agent]
    end

    subgraph Access_Proxy["Access Tier"]
        AP[Access Proxy]
        ACL[Access Control Engine]
        TI[Trust Inference Engine]
    end

    subgraph Backend["Internal Resources"]
        APP1[Internal App A]
        APP2[Internal App B]
        APP3[Internal App C]
    end

    U -->|"HTTPS + client cert"| AP
    DC -->|"Device identity"| AP
    DP -->|"OS patch level, disk encryption, AV status"| TI
    AP -->|"User identity + device trust score"| ACL
    TI -->|"Trust score: 85/100"| ACL
    ACL -->|"Allow App A, B; Deny App C"| AP
    AP -->|"Authorized proxy"| APP1
    AP -->|"Authorized proxy"| APP2
```

### 4.4.9 Continuous Verification and Adaptive Access

Zero trust does not end after the initial authentication. Continuous verification re-evaluates trust throughout the session:

**Signals for continuous evaluation:**

| Signal Category | Examples | Action on Anomaly |
|----------------|----------|-------------------|
| **Behavioral** | Unusual access time, geographic anomaly, impossible travel | Step-up authentication |
| **Device** | OS patch status changes, disk encryption disabled, jailbreak detected | Reduce trust score, restrict access |
| **Network** | Connection from known-bad IP, TOR exit node, high-risk country | Block or require MFA |
| **Session** | Token age, idle time, privilege escalation attempt | Re-authenticate, reduce scope |
| **Data** | Bulk data download, access to unusual resources | Alert SOC, throttle, require justification |

```python
# Pseudocode: Adaptive access control engine
class AdaptiveAccessEngine:
    def evaluate_request(self, request, session):
        trust_score = self.calculate_trust_score(request, session)

        if trust_score >= 90:
            return AccessDecision.ALLOW
        elif trust_score >= 70:
            return AccessDecision.ALLOW_WITH_MONITORING
        elif trust_score >= 50:
            return AccessDecision.REQUIRE_STEP_UP_AUTH
        else:
            return AccessDecision.DENY

    def calculate_trust_score(self, request, session):
        score = 100

        # Device posture
        if not request.device.is_managed:
            score -= 20
        if not request.device.disk_encrypted:
            score -= 15
        if request.device.os_patch_age_days > 30:
            score -= 10

        # Behavioral analysis
        if self.is_impossible_travel(request, session):
            score -= 40
        if self.is_unusual_access_time(request, session):
            score -= 10

        # Network context
        if request.ip in self.known_bad_ips:
            score -= 50
        if request.geo_country not in session.user.allowed_countries:
            score -= 25

        return max(score, 0)
```

---

## 4.5 Container and Kubernetes Security

Container-based deployments introduce a new layer of security concerns. Kubernetes orchestration adds complexity through its API surface, RBAC model, network model, and secret management.

### 4.5.1 Container Security Lifecycle

```mermaid
flowchart LR
    subgraph Build["Build Phase"]
        BI[Base Image Selection]
        VS[Vulnerability Scan]
        SB[SBOM Generation]
        IS[Image Signing]
    end

    subgraph Deploy["Deploy Phase"]
        AC[Admission Control]
        SV[Signature Verification]
        PS[Pod Security Standards]
    end

    subgraph Runtime["Runtime Phase"]
        RM[Runtime Monitoring]
        NS[Network Segmentation]
        SM[Secret Management]
        AL[Audit Logging]
    end

    BI --> VS --> SB --> IS --> AC --> SV --> PS --> RM
    PS --> NS
    PS --> SM
    PS --> AL
```

### 4.5.2 Container Image Security

**Hardening base images:**

```dockerfile
# BAD: Using a full OS image with unnecessary packages
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip
COPY . /app
RUN pip3 install -r requirements.txt
CMD ["python3", "/app/main.py"]

# GOOD: Distroless image — no shell, no package manager, minimal attack surface
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

FROM gcr.io/distroless/python3-debian12
WORKDIR /app
COPY --from=builder /app/deps /app/deps
COPY . /app
ENV PYTHONPATH=/app/deps
CMD ["main.py"]
```

**Image scanning in CI/CD:**

```yaml
# GitHub Actions — scan container image before push
- name: Build Docker image
  run: docker build -t myapp:${{ github.sha }} .

- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'myapp:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'  # Fail the build on critical/high vulnerabilities

- name: Sign image with Cosign
  run: |
    cosign sign --key cosign.key myapp:${{ github.sha }}
```

### 4.5.3 Kubernetes Pod Security

**Pod Security Standards (PSS):**

| Profile | Description | Use Case |
|---------|-------------|----------|
| **Privileged** | No restrictions | System-level workloads (monitoring agents, CNI) |
| **Baseline** | Prevents known privilege escalations | Most workloads |
| **Restricted** | Heavily restricted, follows hardening best practices | Security-sensitive workloads |

**Restricted pod security context:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      image: myapp:v1.2.3@sha256:abc123...  # Pin by digest
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
        runAsNonRoot: true
      resources:
        limits:
          cpu: "500m"
          memory: "256Mi"
        requests:
          cpu: "100m"
          memory: "128Mi"
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir:
        sizeLimit: "100Mi"
  automountServiceAccountToken: false  # Disable unless needed
```

### 4.5.4 Kubernetes RBAC Best Practices

```yaml
# Principle of least privilege: service-specific ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: order-service
  namespace: production
  annotations:
    # Workload identity for cloud provider access
    iam.gke.io/gcp-service-account: order-svc@project.iam.gserviceaccount.com
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: order-service-role
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["order-service-config"]  # Specific resource, not all configmaps
    verbs: ["get", "watch"]
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["order-service-db-creds"]
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: order-service-binding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: order-service
roleRef:
  kind: Role
  name: order-service-role
  apiGroup: rbac.authorization.k8s.io
```

**Common Kubernetes RBAC anti-patterns:**

| Anti-Pattern | Risk | Fix |
|-------------|------|-----|
| Using `cluster-admin` for workloads | Full cluster access if compromised | Create scoped Roles per service |
| Wildcard verbs (`*`) in rules | Allows delete, patch, escalate | Enumerate specific verbs needed |
| Wildcard resources (`*`) in rules | Access to secrets, RBAC resources | List specific resources |
| Default ServiceAccount with permissions | All pods in namespace share access | Create per-workload ServiceAccounts |
| ClusterRole where Role suffices | Cross-namespace access | Use namespace-scoped Roles |

### 4.5.5 Admission Controllers for Security

Admission controllers intercept requests to the Kubernetes API server and can validate, mutate, or reject them.

```yaml
# Kyverno policy: require non-root containers
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-non-root
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-runAsNonRoot
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        message: "Containers must run as non-root"
        pattern:
          spec:
            containers:
              - securityContext:
                  runAsNonRoot: true
---
# Kyverno policy: require image signatures
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-cosign-signature
      match:
        any:
          - resources:
              kinds:
                - Pod
      verifyImages:
        - imageReferences:
            - "registry.example.com/*"
          attestors:
            - entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
                      -----END PUBLIC KEY-----
```

### 4.5.6 Runtime Security Monitoring

| Tool | Approach | Detection Capabilities |
|------|----------|----------------------|
| **Falco** | eBPF-based syscall monitoring | Unexpected process execution, file access, network connections |
| **Tetragon** | eBPF with enforcement | Process execution, file access, network, with kill capability |
| **KubeArmor** | LSM + eBPF | File, process, network policies per pod |
| **Sysdig Secure** | Kernel instrumentation | Runtime threat detection, compliance, forensics |

**Falco rule example:**

```yaml
- rule: Terminal Shell in Container
  desc: Detect a shell being spawned in a container
  condition: >
    spawned_process and
    container and
    shell_procs and
    not container.image.repository in (allowed_debug_images)
  output: >
    Shell spawned in container
    (user=%user.name container=%container.name
     image=%container.image.repository
     shell=%proc.name parent=%proc.pname)
  priority: WARNING
  tags: [container, shell, mitre_execution]

- rule: Unexpected Outbound Connection
  desc: Detect unexpected outbound network connections from containers
  condition: >
    outbound and
    container and
    not fd.sport in (80, 443, 8080, 8443, 5432, 6379) and
    not container.image.repository in (allowed_network_images)
  output: >
    Unexpected outbound connection
    (container=%container.name image=%container.image.repository
     connection=%fd.name)
  priority: NOTICE
  tags: [container, network, mitre_exfiltration]
```

---

## 4.6 Supply Chain Security

Supply chain security protects the integrity of the software development and delivery pipeline, from source code to production deployment. Modern attacks increasingly target the build process, dependencies, and distribution channels rather than the running application.

### 4.6.1 Attack Vectors

```mermaid
flowchart TD
    subgraph Supply_Chain["Software Supply Chain"]
        SC[Source Code] --> BLD[Build System]
        DEP[Dependencies] --> BLD
        BLD --> ART[Artifacts / Images]
        ART --> REG[Registry]
        REG --> DEP_ENV[Deployment]
    end

    ATK1["Compromised Developer Machine"] -.->|"Inject malicious code"| SC
    ATK2["Dependency Confusion"] -.->|"Malicious package with internal name"| DEP
    ATK3["Typosquatting"] -.->|"evil-loadsh vs lodash"| DEP
    ATK4["Compromised CI/CD"] -.->|"Modify build pipeline"| BLD
    ATK5["Registry Poisoning"] -.->|"Push malicious image"| REG
    ATK6["Stolen Signing Keys"] -.->|"Sign malicious artifacts"| ART

    style ATK1 fill:#ff6b6b,color:#fff
    style ATK2 fill:#ff6b6b,color:#fff
    style ATK3 fill:#ff6b6b,color:#fff
    style ATK4 fill:#ff6b6b,color:#fff
    style ATK5 fill:#ff6b6b,color:#fff
    style ATK6 fill:#ff6b6b,color:#fff
```

### 4.6.2 SLSA Framework (Supply-chain Levels for Software Artifacts)

SLSA provides a graduated framework for supply chain integrity:

| SLSA Level | Requirements | Protections |
|------------|-------------|-------------|
| **Level 0** | No guarantees | No protection |
| **Level 1** | Build process is documented and produces provenance | Mistakes, basic tampering |
| **Level 2** | Provenance is generated by a hosted build service | Tampering after build |
| **Level 3** | Build platform is hardened, provenance is non-falsifiable | Compromised build environment |

**Generating SLSA provenance with GitHub Actions:**

```yaml
name: Build and Sign
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write    # OIDC token for signing
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Build binary
        run: go build -o myapp .

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          artifact-name: sbom.spdx.json

      - name: Generate SLSA provenance
        uses: slsa-framework/slsa-github-generator/.github/workflows/builder_go_slsa3.yml@v1
        with:
          go-version: "1.22"

      - name: Sign with Sigstore
        run: |
          cosign sign-blob --yes --bundle myapp.bundle myapp
```

### 4.6.3 Software Bill of Materials (SBOM)

An SBOM is a formal record of all components in a software artifact, analogous to an ingredients list for food.

**SBOM formats:**

| Format | Standard | Ecosystem |
|--------|----------|-----------|
| **SPDX** | ISO/IEC 5962:2021 | Linux Foundation, broad adoption |
| **CycloneDX** | OWASP standard | Security-focused, supports VEX |
| **SWID** | ISO/IEC 19770-2 | Enterprise software licensing |

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "version": 1,
  "metadata": {
    "component": {
      "name": "order-service",
      "version": "2.1.0",
      "type": "application"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "express",
      "version": "4.18.2",
      "purl": "pkg:npm/express@4.18.2",
      "hashes": [
        {
          "alg": "SHA-256",
          "content": "abc123..."
        }
      ]
    }
  ],
  "vulnerabilities": [
    {
      "id": "CVE-2024-XXXX",
      "source": { "name": "NVD" },
      "ratings": [{ "severity": "high", "score": 8.1 }],
      "affects": [{ "ref": "pkg:npm/express@4.18.2" }],
      "analysis": {
        "state": "not_affected",
        "justification": "code_not_reachable",
        "detail": "Vulnerable code path is not used in our application"
      }
    }
  ]
}
```

### 4.6.4 Dependency Pinning and Lock Files

| Strategy | Example | Protects Against |
|----------|---------|-----------------|
| **Version pinning** | `express@4.18.2` | Unexpected upgrades |
| **Lock files** | `package-lock.json`, `go.sum`, `Cargo.lock` | Transitive dependency changes |
| **Hash verification** | `integrity: "sha512-abc..."` | Tampered packages |
| **Private registry mirror** | Artifactory, Nexus | Upstream registry compromise |
| **Namespace scoping** | `@myorg/internal-lib` | Dependency confusion attacks |

---

## 4.7 Certificate Management and PKI

Public Key Infrastructure (PKI) provides the foundation for identity verification, encrypted communication, and code signing. Effective certificate management prevents outages from expired certificates and security incidents from compromised keys.

### 4.7.1 PKI Architecture

```mermaid
flowchart TD
    subgraph PKI["Public Key Infrastructure"]
        RCA[Root CA<br/>Offline, HSM-protected]
        ICA1[Intermediate CA 1<br/>Server Certificates]
        ICA2[Intermediate CA 2<br/>Client Certificates]
        ICA3[Intermediate CA 3<br/>Code Signing]
    end

    subgraph Certificates["Issued Certificates"]
        SC1[*.example.com<br/>TLS Server Cert]
        SC2[api.example.com<br/>TLS Server Cert]
        CC1[service-a.internal<br/>mTLS Client Cert]
        CC2[service-b.internal<br/>mTLS Client Cert]
        CS1[Release v2.1<br/>Code Signing Cert]
    end

    RCA -->|"Signs"| ICA1
    RCA -->|"Signs"| ICA2
    RCA -->|"Signs"| ICA3
    ICA1 -->|"Issues"| SC1
    ICA1 -->|"Issues"| SC2
    ICA2 -->|"Issues"| CC1
    ICA2 -->|"Issues"| CC2
    ICA3 -->|"Issues"| CS1
```

### 4.7.2 Certificate Lifecycle Management

| Phase | Activities | Automation |
|-------|-----------|------------|
| **Request** | Generate key pair, create CSR | cert-manager, Vault PKI |
| **Issuance** | CA validates request, signs certificate | ACME (Let's Encrypt), internal CA |
| **Distribution** | Deliver cert to service, configure TLS | Kubernetes Secrets, Vault Agent |
| **Monitoring** | Track expiration, validate chain | cert-manager, custom monitoring |
| **Renewal** | Request new cert before expiry | Auto-renewal with cert-manager |
| **Revocation** | Invalidate compromised certificates | CRL, OCSP, OCSP Stapling |

**cert-manager for Kubernetes:**

```yaml
# ClusterIssuer for Let's Encrypt
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: security@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            class: nginx
---
# Automatically managed certificate
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: api-tls
  namespace: production
spec:
  secretName: api-tls-secret
  duration: 2160h    # 90 days
  renewBefore: 720h  # Renew 30 days before expiry
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - api.example.com
    - api-internal.example.com
---
# Internal CA for mTLS certificates
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: internal-ca
spec:
  ca:
    secretName: internal-ca-key-pair
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: order-service-mtls
  namespace: production
spec:
  secretName: order-service-mtls-cert
  duration: 24h       # Short-lived for zero trust
  renewBefore: 8h
  issuerRef:
    name: internal-ca
    kind: ClusterIssuer
  commonName: order-service.production.svc.cluster.local
  dnsNames:
    - order-service.production.svc.cluster.local
  usages:
    - digital signature
    - key encipherment
    - server auth
    - client auth
```

### 4.7.3 Mutual TLS (mTLS) Implementation

mTLS extends standard TLS by requiring both the client and server to present certificates. This provides two-way authentication at the transport layer.

**Standard TLS vs mTLS:**

| Aspect | Standard TLS | Mutual TLS |
|--------|-------------|------------|
| **Server identity** | Verified by client | Verified by client |
| **Client identity** | Not verified at transport layer | Verified by server |
| **Certificate requirement** | Server only | Both client and server |
| **Use case** | Browser to server | Service to service |

**mTLS with Go:**

```go
package main

import (
    "crypto/tls"
    "crypto/x509"
    "log"
    "net/http"
    "os"
)

func setupMTLSServer() *http.Server {
    // Load server certificate and key
    serverCert, err := tls.LoadX509KeyPair("server.crt", "server.key")
    if err != nil {
        log.Fatal(err)
    }

    // Load CA certificate for verifying client certificates
    caCert, err := os.ReadFile("ca.crt")
    if err != nil {
        log.Fatal(err)
    }
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    tlsConfig := &tls.Config{
        Certificates: []tls.Certificate{serverCert},
        ClientAuth:   tls.RequireAndVerifyClientCert,
        ClientCAs:    caCertPool,
        MinVersion:   tls.VersionTLS13,
    }

    return &http.Server{
        Addr:      ":8443",
        TLSConfig: tlsConfig,
        Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            // Extract client identity from verified certificate
            clientCN := r.TLS.PeerCertificates[0].Subject.CommonName
            log.Printf("Authenticated client: %s", clientCN)
            w.Write([]byte("Hello, " + clientCN))
        }),
    }
}

func setupMTLSClient() *http.Client {
    clientCert, _ := tls.LoadX509KeyPair("client.crt", "client.key")
    caCert, _ := os.ReadFile("ca.crt")
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    return &http.Client{
        Transport: &http.Transport{
            TLSClientConfig: &tls.Config{
                Certificates: []tls.Certificate{clientCert},
                RootCAs:      caCertPool,
                MinVersion:   tls.VersionTLS13,
            },
        },
    }
}
```

### 4.7.4 Certificate Pinning

Certificate pinning prevents man-in-the-middle attacks by associating a host with its expected certificate or public key.

| Pinning Strategy | What is Pinned | Flexibility | Risk |
|-----------------|----------------|-------------|------|
| **Certificate pinning** | Exact certificate | Low — must update pin on cert renewal | High — pin rotation requires app update |
| **Public key pinning** | Subject Public Key Info (SPKI) | Medium — survives cert renewal if key unchanged | Medium — key rotation requires app update |
| **CA pinning** | Issuing CA certificate | High — any cert from that CA accepted | Low — but weaker protection |

**Mobile app certificate pinning (Android):**

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2025-06-01">
            <!-- Primary pin (current certificate SPKI hash) -->
            <pin digest="SHA-256">base64encodedSPKIHash1==</pin>
            <!-- Backup pin (next certificate SPKI hash) -->
            <pin digest="SHA-256">base64encodedSPKIHash2==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

---

## 4.8 Security Headers Deep Dive

HTTP security headers form a critical defense layer that instructs browsers how to behave when handling content. Properly configured headers prevent entire classes of attacks.

### 4.8.1 HSTS (HTTP Strict Transport Security)

HSTS ensures that browsers always connect via HTTPS, even if the user types `http://` or clicks an HTTP link.

**Configuration:**

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

| Directive | Purpose |
|-----------|---------|
| `max-age=31536000` | Browser remembers HTTPS-only for 1 year |
| `includeSubDomains` | Applies to all subdomains |
| `preload` | Eligible for browser preload list (hardcoded HTTPS) |

**HSTS deployment sequence:**
1. Ensure all HTTP traffic redirects to HTTPS (301 redirect).
2. Set `max-age=300` (5 minutes) initially to test.
3. Gradually increase: 1 hour, 1 day, 1 week, 1 year.
4. Add `includeSubDomains` after verifying all subdomains support HTTPS.
5. Submit to the HSTS preload list (hstspreload.org) after `max-age >= 31536000`.

**Warning:** HSTS preload is difficult to undo. Once in the preload list, removing it takes months. Ensure all subdomains support HTTPS before preloading.

### 4.8.2 CORS (Cross-Origin Resource Sharing)

CORS controls which origins can make cross-origin requests to your API. Misconfigured CORS is a common source of security vulnerabilities.

**CORS request flow:**

```mermaid
sequenceDiagram
    participant B as Browser (app.example.com)
    participant A as API (api.example.com)

    Note over B: Simple request (GET, no custom headers)
    B->>A: GET /data<br/>Origin: https://app.example.com
    A->>B: 200 OK<br/>Access-Control-Allow-Origin: https://app.example.com

    Note over B: Preflight request (POST with JSON)
    B->>A: OPTIONS /data<br/>Origin: https://app.example.com<br/>Access-Control-Request-Method: POST<br/>Access-Control-Request-Headers: Content-Type, Authorization
    A->>B: 204 No Content<br/>Access-Control-Allow-Origin: https://app.example.com<br/>Access-Control-Allow-Methods: GET, POST<br/>Access-Control-Allow-Headers: Content-Type, Authorization<br/>Access-Control-Max-Age: 86400
    B->>A: POST /data<br/>Origin: https://app.example.com<br/>Content-Type: application/json<br/>Authorization: Bearer token123
    A->>B: 200 OK<br/>Access-Control-Allow-Origin: https://app.example.com
```

**Secure CORS configuration (Express.js):**

```javascript
const cors = require('cors');

// SECURE: Explicit allow-list of origins
const allowedOrigins = [
  'https://app.example.com',
  'https://admin.example.com',
];

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (server-to-server, curl)
    if (!origin) return callback(null, true);

    if (allowedOrigins.includes(origin)) {
      callback(null, origin);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,  // Allow cookies (requires specific origin, not '*')
  maxAge: 86400,      // Cache preflight for 24 hours
}));

// INSECURE PATTERNS TO AVOID:
// Access-Control-Allow-Origin: *              <-- allows any origin
// Access-Control-Allow-Origin: ${req.origin}  <-- reflects any origin (same as *)
// Access-Control-Allow-Credentials: true with Origin: *  <-- browsers reject this
```

**Common CORS misconfigurations:**

| Misconfiguration | Risk | Fix |
|-----------------|------|-----|
| `Access-Control-Allow-Origin: *` | Any website can read responses | Use explicit origin allow-list |
| Reflecting `Origin` header blindly | Same as `*` but bypasses browser restriction with credentials | Validate against allow-list |
| `null` origin allowed | Sandboxed iframes and redirects use `null` origin | Never allow `null` |
| Overly broad regex (`*.example.com`) | Can match `attacker-example.com` | Use exact string matching |

### 4.8.3 Comprehensive Security Headers Configuration

**Nginx configuration:**

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # TLS configuration
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;
    add_header Cross-Origin-Opener-Policy "same-origin" always;
    add_header Cross-Origin-Embedder-Policy "require-corp" always;
    add_header Cross-Origin-Resource-Policy "same-origin" always;

    # Remove server version header
    server_tokens off;

    # For API responses (no caching of sensitive data)
    location /api/ {
        add_header Cache-Control "no-store, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
    }
}
```

### 4.8.4 Subresource Integrity (SRI)

SRI ensures that files fetched from CDNs have not been tampered with by verifying their cryptographic hash.

```html
<!-- Without SRI: if CDN is compromised, malicious JS runs in your context -->
<script src="https://cdn.example.com/lib.js"></script>

<!-- With SRI: browser verifies hash before executing -->
<script
  src="https://cdn.example.com/lib.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8w"
  crossorigin="anonymous">
</script>
```

---

## 4.9 OWASP API Security Top 10

The OWASP API Security Top 10 focuses specifically on API vulnerabilities, which differ from traditional web application risks. APIs are increasingly the primary attack surface for modern systems.

### 4.9.1 API Security Risk Overview

| Rank | Risk | Description |
|------|------|-------------|
| **API1** | Broken Object Level Authorization (BOLA) | Accessing objects belonging to other users by manipulating IDs |
| **API2** | Broken Authentication | Weak authentication mechanisms in API endpoints |
| **API3** | Broken Object Property Level Authorization | Exposing or allowing modification of sensitive object properties |
| **API4** | Unrestricted Resource Consumption | No limits on API resource usage (size, rate, count) |
| **API5** | Broken Function Level Authorization | Accessing admin or privileged functions without authorization |
| **API6** | Unrestricted Access to Sensitive Business Flows | Automated abuse of business logic (ticket scalping, mass purchasing) |
| **API7** | Server-Side Request Forgery (SSRF) | API fetches user-supplied URLs without validation |
| **API8** | Security Misconfiguration | Missing security headers, verbose errors, unnecessary HTTP methods |
| **API9** | Improper Inventory Management | Unmanaged, deprecated, or shadow API endpoints |
| **API10** | Unsafe Consumption of APIs | Trusting data from third-party APIs without validation |

### 4.9.2 BOLA (Broken Object Level Authorization) — Deep Dive

BOLA (also known as IDOR — Insecure Direct Object Reference) is the most critical API vulnerability. It occurs when an API does not verify that the requesting user has permission to access the specific object.

```python
# VULNERABLE: No authorization check on the resource
@app.route('/api/v1/orders/<order_id>')
def get_order(order_id):
    order = db.orders.find_one({'_id': order_id})
    return jsonify(order)  # Any authenticated user can access any order

# SECURE: Verify ownership before returning data
@app.route('/api/v1/orders/<order_id>')
@require_auth
def get_order(order_id):
    user_id = get_current_user_id()
    order = db.orders.find_one({
        '_id': order_id,
        'user_id': user_id  # Ownership check in the query
    })
    if not order:
        return jsonify({'error': 'Not found'}), 404  # 404, not 403 (don't leak existence)
    return jsonify(order)

# EVEN BETTER: Use non-guessable identifiers
# Instead of sequential IDs (1, 2, 3...), use UUIDs or ULIDs
# GET /api/v1/orders/01HX3Z7K8M2N4P5Q6R7S8T9V  (ULID — not guessable)
```

### 4.9.3 API Rate Limiting and Resource Protection

```python
# Comprehensive API rate limiting with multiple dimensions
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200 per day", "50 per hour"]
)

# Per-endpoint limits
@app.route('/api/v1/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Prevent credential stuffing
def login():
    pass

@app.route('/api/v1/search', methods=['GET'])
@limiter.limit("30 per minute")  # Prevent scraping
def search():
    pass

@app.route('/api/v1/export', methods=['POST'])
@limiter.limit("3 per hour")  # Prevent bulk data export abuse
def export_data():
    # Also limit response size
    max_records = 10000
    pass

# Resource consumption limits in API design
@app.route('/api/v1/graphql', methods=['POST'])
def graphql():
    query = request.json.get('query')

    # Prevent deeply nested queries (DoS via query complexity)
    depth = calculate_query_depth(query)
    if depth > 5:
        return jsonify({'error': 'Query too deep'}), 400

    # Prevent wide queries
    breadth = calculate_query_breadth(query)
    if breadth > 100:
        return jsonify({'error': 'Query too wide'}), 400

    # Enforce pagination
    variables = request.json.get('variables', {})
    page_size = variables.get('first', variables.get('last', 100))
    if page_size > 100:
        return jsonify({'error': 'Page size exceeds maximum'}), 400
```

### 4.9.4 API Inventory and Lifecycle Management

**Shadow API detection checklist:**

| Method | Description |
|--------|-------------|
| **API gateway logs** | Analyze traffic for endpoints not in the API catalog |
| **Network traffic analysis** | Monitor for undocumented API calls between services |
| **Code scanning** | Scan repositories for route definitions, compare with API docs |
| **OpenAPI spec diffing** | Compare deployed routes with published API specifications |
| **Automated discovery** | Tools like Akto, Salt Security that learn API inventory from traffic |

```yaml
# API versioning and deprecation strategy
# openapi.yaml
openapi: "3.1.0"
info:
  title: Order Service API
  version: "2.0.0"
paths:
  /api/v2/orders:
    get:
      summary: List orders (current)
      operationId: listOrdersV2
  /api/v1/orders:
    get:
      summary: List orders (deprecated)
      deprecated: true
      description: |
        This endpoint is deprecated and will be removed on 2025-06-01.
        Migrate to /api/v2/orders.
      x-sunset: "2025-06-01"
```

---

## 4.10 Secrets Rotation Patterns (Extended)

Building on Section 3.2.4, this section provides detailed implementation patterns for secrets rotation across different credential types.

### 4.10.1 Database Credential Rotation with Vault

```mermaid
sequenceDiagram
    participant App as Application
    participant VA as Vault Agent
    participant V as HashiCorp Vault
    participant DB as PostgreSQL

    Note over V,DB: Initial setup: Vault has root DB credentials

    App->>VA: 1. Request database credentials
    VA->>V: 2. Read secret/database/creds/order-service
    V->>DB: 3. CREATE ROLE order_svc_v7 WITH PASSWORD 'dynamic_pass' VALID UNTIL '2025-01-01 13:00:00'
    V->>DB: 4. GRANT order_service_role TO order_svc_v7
    DB->>V: 5. Role created
    V->>VA: 6. Return { username: order_svc_v7, password: dynamic_pass, lease_ttl: 1h }
    VA->>App: 7. Inject credentials via file or env

    Note over App: 55 minutes later (approaching TTL)
    VA->>V: 8. Renew lease
    V->>VA: 9. Lease extended

    Note over App: At max TTL or on revocation
    V->>DB: 10. DROP ROLE order_svc_v7
```

### 4.10.2 API Key Rotation Pattern

```python
# Zero-downtime API key rotation using dual-key acceptance
class APIKeyRotation:
    """
    Pattern: Maintain two active keys during rotation window.
    Both the old and new keys are valid during the overlap period.
    """

    def __init__(self, secrets_manager):
        self.secrets_manager = secrets_manager

    def rotate_api_key(self, key_id: str):
        # Step 1: Generate new key
        new_key = generate_secure_key()

        # Step 2: Store new key alongside old key
        current_secret = self.secrets_manager.get_secret(key_id)
        self.secrets_manager.update_secret(key_id, {
            'current': new_key,
            'previous': current_secret['current'],
            'rotated_at': datetime.utcnow().isoformat(),
        })

        # Step 3: Update the external system (e.g., third-party API)
        external_api.update_api_key(new_key)

        return new_key

    def validate_api_key(self, key_id: str, provided_key: str) -> bool:
        """Accept both current and previous key during rotation window."""
        secret = self.secrets_manager.get_secret(key_id)
        if constant_time_compare(provided_key, secret['current']):
            return True
        if secret.get('previous') and constant_time_compare(provided_key, secret['previous']):
            # Log: client is using previous key, should update
            log.warning(f"Client using previous key for {key_id}")
            return True
        return False

    def cleanup_previous_key(self, key_id: str):
        """Called after rotation window expires (e.g., 24 hours)."""
        secret = self.secrets_manager.get_secret(key_id)
        del secret['previous']
        self.secrets_manager.update_secret(key_id, secret)
```

### 4.10.3 TLS Certificate Rotation Pattern

| Phase | Action | Duration |
|-------|--------|----------|
| 1. Pre-rotation | Generate new certificate, validate chain | Automated |
| 2. Deployment | Deploy new cert alongside old cert (dual-cert) | Minutes |
| 3. Verification | Monitor for TLS handshake errors | 1-4 hours |
| 4. Cleanup | Remove old certificate | After verification |

**Rotation without downtime using Kubernetes:**

```yaml
# cert-manager handles this automatically:
# 1. Generates new cert when renewBefore threshold is reached
# 2. Updates the Secret with new cert
# 3. Triggers rolling restart of pods that mount the secret (with reloader)
# 4. Old cert remains valid until expiry

# Stakater Reloader annotation for automatic pod restart on cert change
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  annotations:
    reloader.stakater.com/auto: "true"  # Restart when mounted secrets change
spec:
  template:
    spec:
      containers:
        - name: app
          volumeMounts:
            - name: tls
              mountPath: /etc/tls
              readOnly: true
      volumes:
        - name: tls
          secret:
            secretName: order-service-mtls-cert
```

---

## 4.11 Penetration Testing Methodologies

Penetration testing validates security controls by simulating real-world attacks. It is a critical complement to automated scanning and threat modeling.

### 4.11.1 Testing Methodologies Comparison

| Methodology | Focus | Phases | Best For |
|-------------|-------|--------|----------|
| **OWASP Testing Guide** | Web applications and APIs | Information Gathering, Configuration Testing, Identity Testing, Authentication, Authorization, Session, Input Validation, Error Handling, Cryptography, Business Logic, Client-Side | Web app pentesting |
| **PTES** (Penetration Testing Execution Standard) | General pentesting | Pre-engagement, Intelligence Gathering, Threat Modeling, Vulnerability Analysis, Exploitation, Post-exploitation, Reporting | Broad infrastructure testing |
| **OSSTMM** (Open Source Security Testing Methodology Manual) | Operational security | Scope, Channel, Index, Vectors, Analysis | Comprehensive security audit |
| **NIST SP 800-115** | Technical security testing | Planning, Discovery, Attack, Reporting | Government / compliance-driven testing |

### 4.11.2 API Penetration Testing Checklist

```markdown
## Pre-Engagement
- [ ] Define scope (which APIs, which environments)
- [ ] Obtain written authorization
- [ ] Set up testing environment (staging, not production)
- [ ] Gather API documentation (OpenAPI specs, Postman collections)

## Reconnaissance
- [ ] Enumerate all API endpoints (crawling, documentation, traffic analysis)
- [ ] Identify API technologies (REST, GraphQL, gRPC, WebSocket)
- [ ] Map authentication mechanisms
- [ ] Identify API versioning (v1, v2 endpoints)
- [ ] Discover deprecated/shadow endpoints

## Authentication Testing
- [ ] Test default credentials
- [ ] Test credential stuffing resistance (rate limiting)
- [ ] Test token expiration and refresh flows
- [ ] Test password reset flow for account takeover
- [ ] Test MFA bypass techniques
- [ ] Test JWT algorithm confusion (alg:none, RS256→HS256)
- [ ] Test OAuth flow vulnerabilities (redirect_uri manipulation, state bypass)

## Authorization Testing
- [ ] Test BOLA/IDOR (access other users' resources by changing IDs)
- [ ] Test BFLA (access admin functions as regular user)
- [ ] Test horizontal privilege escalation (user A accessing user B's data)
- [ ] Test vertical privilege escalation (user accessing admin functions)
- [ ] Test mass assignment (send unexpected fields in requests)
- [ ] Test parameter pollution

## Input Validation Testing
- [ ] Test SQL injection on all parameters
- [ ] Test NoSQL injection (MongoDB operator injection)
- [ ] Test command injection
- [ ] Test SSRF (URL parameters, webhooks, file imports)
- [ ] Test XXE (XML input endpoints)
- [ ] Test GraphQL-specific attacks (introspection, batching, deep nesting)

## Business Logic Testing
- [ ] Test race conditions (TOCTOU on financial operations)
- [ ] Test business flow abuse (coupon reuse, referral fraud)
- [ ] Test resource exhaustion (large uploads, deep pagination)
- [ ] Test price manipulation (negative quantities, decimal overflow)
```

### 4.11.3 Automated Security Testing in CI/CD

```yaml
# Security testing pipeline stages
name: Security Pipeline
on: [pull_request]

jobs:
  sast:
    name: Static Application Security Testing
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/owasp-top-ten
            p/r2c-security-audit
            p/jwt
            p/sql-injection

  dependency-scan:
    name: Dependency Vulnerability Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Snyk
        uses: snyk/actions/node@master
        with:
          args: --severity-threshold=high

  dast:
    name: Dynamic Application Security Testing
    runs-on: ubuntu-latest
    needs: [deploy-staging]
    steps:
      - name: Run OWASP ZAP
        uses: zaproxy/action-api-scan@v0.7.0
        with:
          target: 'https://staging-api.example.com/openapi.json'
          format: openapi
          rules_file_name: 'zap-rules.tsv'
          fail_action: true

  container-scan:
    name: Container Image Scan
    runs-on: ubuntu-latest
    steps:
      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '${{ env.IMAGE }}'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

  iac-scan:
    name: Infrastructure as Code Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: terraform/
          framework: terraform
          soft_fail: false
```

---

## 4.12 Compliance Frameworks Comparison

Understanding compliance frameworks is essential for designing systems that meet regulatory requirements. This section compares the four most common frameworks encountered in system design.

### 4.12.1 Framework Overview

| Framework | Full Name | Governing Body | Primary Audience | Certification Type |
|-----------|-----------|---------------|------------------|--------------------|
| **SOC 2** | System and Organization Controls 2 | AICPA | SaaS companies, cloud providers | Attestation report (Type I or Type II) |
| **ISO 27001** | Information Security Management System | ISO/IEC | Any organization | Certification by accredited body |
| **PCI-DSS** | Payment Card Industry Data Security Standard | PCI SSC | Organizations handling card payments | Self-assessment or QSA audit |
| **HIPAA** | Health Insurance Portability and Accountability Act | HHS (US) | Healthcare, health data processors | No formal certification; audit-based |

### 4.12.2 Detailed Comparison

| Dimension | SOC 2 | ISO 27001 | PCI-DSS | HIPAA |
|-----------|-------|-----------|---------|-------|
| **Scope** | Trust Service Criteria (Security, Availability, Confidentiality, Processing Integrity, Privacy) | Information Security Management System (ISMS) | Cardholder data environment (CDE) | Protected Health Information (PHI) |
| **Encryption at rest** | Required for sensitive data | Required per risk assessment | AES-256 or equivalent for stored card data | Required for PHI |
| **Encryption in transit** | Required | Required per risk assessment | TLS 1.2+ for card data in transit | Required for PHI over open networks |
| **Access control** | Role-based, least privilege | Per risk assessment, generally RBAC | Strict need-to-know for CDE | Minimum necessary standard |
| **MFA** | Required for production access | Risk-based | Required for all CDE access | Addressable (must implement or document why not) |
| **Logging and monitoring** | Required, reviewed regularly | Required per risk assessment | 12 months retention, daily log review | Required for PHI access |
| **Vulnerability management** | Regular scanning and patching | Per risk assessment | Quarterly scans, annual pentest | Risk analysis required |
| **Incident response** | Plan required, tested annually | Plan required, tested regularly | Plan required with specific timelines | 60-day breach notification |
| **Vendor management** | Third-party risk assessment | Supplier management required | Third-party service provider management | Business Associate Agreements (BAA) |
| **Audit frequency** | Annual (Type II covers 6-12 month period) | 3-year certification, annual surveillance | Annual assessment | Periodic (no fixed schedule) |
| **Cost for startup** | $50K-$150K | $30K-$100K | $20K-$500K (varies by level) | Varies widely |
| **Time to achieve** | 3-6 months (Type I), 6-12 months (Type II) | 6-12 months | 3-12 months | Ongoing |

### 4.12.3 Compliance Controls Mapping

Many controls overlap across frameworks. A unified control framework reduces duplication:

```
Control: Encryption at Rest
  ├── SOC 2 → CC6.1 (Logical and Physical Access Controls)
  ├── ISO 27001 → A.8.24 (Use of Cryptography)
  ├── PCI-DSS → Requirement 3.5 (Protect stored account data)
  └── HIPAA → §164.312(a)(2)(iv) (Encryption and Decryption)

Control: Access Control / Least Privilege
  ├── SOC 2 → CC6.1, CC6.3 (Role-based access)
  ├── ISO 27001 → A.5.15, A.8.2 (Access control, Privileged access)
  ├── PCI-DSS → Requirement 7 (Restrict access by business need-to-know)
  └── HIPAA → §164.312(a)(1) (Access Control)

Control: Audit Logging
  ├── SOC 2 → CC7.2 (Monitoring activities)
  ├── ISO 27001 → A.8.15 (Logging)
  ├── PCI-DSS → Requirement 10 (Log and monitor all access)
  └── HIPAA → §164.312(b) (Audit Controls)

Control: Incident Response
  ├── SOC 2 → CC7.3, CC7.4 (Evaluate and respond to incidents)
  ├── ISO 27001 → A.5.24-A.5.28 (Incident management)
  ├── PCI-DSS → Requirement 12.10 (Incident response plan)
  └── HIPAA → §164.308(a)(6) (Security Incident Procedures)
```

### 4.12.4 Compliance Architecture for a Multi-Framework Environment

```mermaid
flowchart TD
    subgraph Data_Classification["Data Classification"]
        PHI[PHI Data<br/>HIPAA]
        PCI[Card Data<br/>PCI-DSS]
        PII[PII Data<br/>SOC2 + ISO27001]
        GEN[General Data<br/>SOC2]
    end

    subgraph Controls["Security Controls Layer"]
        ENC[Encryption Service<br/>AES-256-GCM]
        IAM[Identity & Access<br/>RBAC + MFA]
        LOG[Audit Logging<br/>12-month retention]
        MON[Monitoring & Alerting<br/>SIEM]
        IRP[Incident Response<br/>Playbooks]
    end

    subgraph Isolation["Data Isolation"]
        CDE[Cardholder Data Environment<br/>Network-isolated segment]
        HDE[Health Data Environment<br/>Encrypted + access-controlled]
        GDE[General Data Environment<br/>Standard controls]
    end

    PHI --> HDE
    PCI --> CDE
    PII --> GDE
    GEN --> GDE

    CDE --> ENC
    CDE --> IAM
    CDE --> LOG
    HDE --> ENC
    HDE --> IAM
    HDE --> LOG
    GDE --> IAM
    GDE --> LOG

    LOG --> MON
    MON --> IRP
```

### 4.12.5 SOC 2 Type II — What Auditors Look For

| Trust Service Criteria | Key Evidence | Common Gaps |
|----------------------|--------------|-------------|
| **CC1 — Control Environment** | Security policies, org chart, security team | Policies exist but are not followed |
| **CC2 — Communication** | Security training records, policy acknowledgments | No annual security awareness training |
| **CC3 — Risk Assessment** | Risk register, annual risk assessment | Risk assessment is outdated |
| **CC5 — Control Activities** | Change management, code review, CI/CD | No formal change approval process |
| **CC6 — Logical/Physical Access** | RBAC, MFA, access reviews, deprovisioning | Stale accounts, no quarterly access reviews |
| **CC7 — System Operations** | Monitoring, alerting, incident response | No evidence of alert triage |
| **CC8 — Change Management** | Git history, PR reviews, deployment logs | Direct production access without review |
| **CC9 — Risk Mitigation** | Vendor assessments, insurance | No vendor security reviews |

### 4.12.6 Building a Compliance-Ready System from Day One

For startups and early-stage companies, building compliance into the architecture from the start is far cheaper than retrofitting.

**Minimum viable compliance architecture:**

```python
# Audit logging middleware — captures every API access for compliance
import json
import time
import uuid
from functools import wraps

class AuditLogger:
    def __init__(self, log_sink):
        self.log_sink = log_sink  # CloudWatch, BigQuery, etc.

    def log_api_access(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            start_time = time.time()

            # Capture request context
            audit_entry = {
                'request_id': request_id,
                'timestamp': time.time(),
                'user_id': get_current_user_id(),
                'ip_address': get_client_ip(),
                'method': request.method,
                'path': request.path,
                'user_agent': request.headers.get('User-Agent'),
                'resource_type': func.__name__,
            }

            try:
                result = func(*args, **kwargs)
                audit_entry['status_code'] = result.status_code
                audit_entry['success'] = result.status_code < 400
                return result
            except Exception as e:
                audit_entry['status_code'] = 500
                audit_entry['success'] = False
                audit_entry['error'] = str(e)
                raise
            finally:
                audit_entry['duration_ms'] = (time.time() - start_time) * 1000
                # Write to immutable audit log (append-only)
                self.log_sink.write(json.dumps(audit_entry))

        return wrapper

# Usage
audit = AuditLogger(log_sink=cloudwatch_sink)

@app.route('/api/v1/patients/<patient_id>')
@require_auth
@audit.log_api_access
def get_patient(patient_id):
    # HIPAA: Log every access to PHI
    pass
```

---

## 4.13 OAuth 2.0 and OpenID Connect — Extended Flows

This section extends Section 1.1 with detailed OIDC flows, token introspection, and advanced patterns.

### 4.13.1 OpenID Connect (OIDC) Architecture

OIDC adds an identity layer on top of OAuth 2.0. While OAuth 2.0 answers "what can this token access?", OIDC answers "who is this user?"

**Key OIDC additions over OAuth 2.0:**

| OAuth 2.0 Concept | OIDC Addition |
|-------------------|---------------|
| Access Token | **ID Token** (JWT with user identity claims) |
| Authorization Endpoint | **UserInfo Endpoint** (returns user profile) |
| Scopes (`read`, `write`) | **Standard scopes** (`openid`, `profile`, `email`, `address`, `phone`) |
| No discovery standard | **Discovery document** (`/.well-known/openid-configuration`) |
| No key distribution | **JWKS endpoint** (`/.well-known/jwks.json`) |

### 4.13.2 OIDC Authorization Code Flow with ID Token Validation

```mermaid
sequenceDiagram
    participant U as User Browser
    participant App as Application Server
    participant OP as OpenID Provider
    participant JWKS as JWKS Endpoint

    U->>App: 1. GET /login
    App->>U: 2. Redirect to OP /authorize
    Note over U,OP: scope=openid profile email<br/>response_type=code<br/>nonce=random_nonce_xyz

    U->>OP: 3. Authenticate (username/password + MFA)
    OP->>U: 4. Redirect to App callback with code
    U->>App: 5. GET /callback?code=abc123&state=xyz

    App->>OP: 6. POST /token (code + client_secret + code_verifier)
    OP->>App: 7. { access_token, id_token, refresh_token }

    Note over App: 8. Validate ID Token:
    App->>JWKS: 9. GET /.well-known/jwks.json
    JWKS->>App: 10. Public keys

    Note over App: 11. Verify: signature, iss, aud, exp, nonce, iat
    Note over App: 12. Extract claims: sub, name, email, email_verified

    App->>OP: 13. GET /userinfo (access_token)
    OP->>App: 14. { sub, name, email, picture, ... }

    App->>U: 15. Set session cookie, redirect to dashboard
```

### 4.13.3 ID Token Validation Checklist

```python
# Complete ID Token validation implementation
import jwt
import requests
from datetime import datetime, timedelta

class OIDCValidator:
    def __init__(self, issuer, client_id, jwks_uri):
        self.issuer = issuer
        self.client_id = client_id
        self.jwks_uri = jwks_uri
        self._jwks_cache = None
        self._jwks_cache_time = None

    def get_jwks(self):
        """Fetch and cache JWKS (refresh every hour)."""
        if (self._jwks_cache is None or
            datetime.utcnow() - self._jwks_cache_time > timedelta(hours=1)):
            response = requests.get(self.jwks_uri)
            self._jwks_cache = response.json()
            self._jwks_cache_time = datetime.utcnow()
        return self._jwks_cache

    def validate_id_token(self, id_token, expected_nonce):
        """
        Validate an OIDC ID Token per OpenID Connect Core 1.0 Section 3.1.3.7
        """
        # Step 1: Decode header WITHOUT verifying signature (to get kid)
        unverified_header = jwt.get_unverified_header(id_token)

        # Step 2: Reject 'none' algorithm (critical security check)
        if unverified_header.get('alg') == 'none':
            raise ValueError("Algorithm 'none' is not allowed")

        # Step 3: Find the signing key from JWKS
        jwks = self.get_jwks()
        signing_key = None
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break

        if not signing_key:
            raise ValueError(f"Key {unverified_header['kid']} not found in JWKS")

        # Step 4: Verify signature and standard claims
        claims = jwt.decode(
            id_token,
            signing_key,
            algorithms=['RS256', 'ES256'],  # Only allow expected algorithms
            audience=self.client_id,
            issuer=self.issuer,
            options={
                'verify_exp': True,
                'verify_iat': True,
                'verify_aud': True,
                'verify_iss': True,
            }
        )

        # Step 5: Verify nonce (prevents replay attacks)
        if claims.get('nonce') != expected_nonce:
            raise ValueError("Nonce mismatch — possible replay attack")

        # Step 6: Verify iat is not too far in the past
        iat = datetime.utcfromtimestamp(claims['iat'])
        if datetime.utcnow() - iat > timedelta(minutes=10):
            raise ValueError("ID token issued too long ago")

        # Step 7: Verify at_hash if access token present (hybrid flow)
        # (implementation omitted for brevity)

        return claims
```

### 4.13.4 Token Introspection and Revocation

For opaque tokens (non-JWT), the resource server must call the authorization server to validate tokens:

```
# Token Introspection (RFC 7662)
POST /introspect HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW

token=dXNlcm5hbWU6cGFzc3dvcmQ&token_type_hint=access_token

# Response
{
  "active": true,
  "sub": "user-12345",
  "client_id": "order-service",
  "scope": "read:orders write:orders",
  "exp": 1711234567,
  "iat": 1711230967,
  "token_type": "Bearer"
}

# Token Revocation (RFC 7009)
POST /revoke HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW

token=dXNlcm5hbWU6cGFzc3dvcmQ&token_type_hint=refresh_token
```

**When to use introspection vs JWT validation:**

| Dimension | JWT (Self-contained) | Opaque Token + Introspection |
|-----------|---------------------|-------------------------------|
| **Validation** | Local (no network call) | Requires call to auth server |
| **Revocation** | Difficult (must wait for expiry or use blocklist) | Immediate (server-side state) |
| **Performance** | Fast (cryptographic verification only) | Slower (network call per request) |
| **Token size** | Larger (contains claims) | Small (random string) |
| **Best for** | High-throughput microservices | Admin panels, sensitive operations |

---

## 4.14 Threat Model Template (STRIDE-Based)

Threat modeling is the structured process of identifying what can go wrong, how likely it is, and what to do about it. The STRIDE framework provides a systematic approach that every team can apply.

### Step 1: Identify Assets

List everything worth protecting:

| Asset Category | Examples |
|---------------|----------|
| **Data** | User PII, payment info, session tokens, API keys, business-critical records |
| **Services** | Authentication service, payment gateway, order service, admin panel |
| **Credentials** | Database passwords, TLS certificates, signing keys, OAuth client secrets |
| **Infrastructure** | DNS records, load balancers, container registries, CI/CD pipelines |

### Step 2: Draw Trust Boundaries

Map your system into zones with different trust levels:

```mermaid
graph LR
    subgraph External["External Zone (Untrusted)"]
        Browser[Browser / Mobile App]
        ThirdParty[Third-Party Webhooks]
    end

    subgraph DMZ["DMZ (Semi-Trusted)"]
        CDN[CDN / WAF]
        APIGateway[API Gateway]
        LB[Load Balancer]
    end

    subgraph Internal["Internal Zone (Trusted)"]
        AuthService[Auth Service]
        OrderService[Order Service]
        PaymentService[Payment Service]
        DB[(Database)]
        Cache[(Redis Cache)]
    end

    subgraph Restricted["Restricted Zone (Highly Trusted)"]
        HSM[HSM / Key Vault]
        AuditLog[(Audit Log Store)]
        AdminPanel[Admin Panel]
    end

    Browser -->|HTTPS| CDN
    ThirdParty -->|HTTPS + HMAC| APIGateway
    CDN --> LB
    LB --> APIGateway
    APIGateway -->|mTLS| AuthService
    APIGateway -->|mTLS| OrderService
    OrderService -->|mTLS| PaymentService
    OrderService --> DB
    AuthService --> Cache
    PaymentService -->|mTLS| HSM
    AuthService --> AuditLog
```

Every arrow crossing a boundary is an attack surface that requires explicit security controls.

### Step 3: Apply STRIDE per Component

For each component at a trust boundary, evaluate all six threat categories:

| Threat | Question | Example Attack | Typical Mitigation |
|--------|----------|---------------|-------------------|
| **S**poofing | Can an attacker impersonate a user or service? | Stolen JWT used to call Order Service | mTLS, short-lived tokens, token binding |
| **T**ampering | Can data be modified in transit or at rest? | Man-in-the-middle modifies order total | TLS everywhere, signed payloads, checksums |
| **R**epudiation | Can an actor deny performing an action? | Admin claims they never deleted records | Tamper-evident audit logs, signed log entries |
| **I**nformation Disclosure | Can sensitive data leak? | Error messages expose stack traces or PII | PII redaction, structured error responses, encryption at rest |
| **D**enial of Service | Can the service be made unavailable? | Unauthenticated endpoint flooded with requests | Rate limiting, WAF, auto-scaling, circuit breakers |
| **E**levation of Privilege | Can an attacker gain higher permissions? | IDOR allows user to access another user's orders | RBAC enforcement, resource ownership checks, input validation |

### Step 4: Rate Risk (Likelihood x Impact Matrix)

| | **Impact: Low** | **Impact: Medium** | **Impact: High** | **Impact: Critical** |
|---|---|---|---|---|
| **Likelihood: Almost Certain** | Medium | High | Critical | Critical |
| **Likelihood: Likely** | Low | Medium | High | Critical |
| **Likelihood: Possible** | Low | Medium | High | High |
| **Likelihood: Unlikely** | Low | Low | Medium | High |
| **Likelihood: Rare** | Low | Low | Low | Medium |

**Risk rating definitions:**
- **Critical** — Must fix before launch; active exploit path exists.
- **High** — Fix within current sprint; significant data or availability impact.
- **Medium** — Schedule within the quarter; limited blast radius.
- **Low** — Accept or address opportunistically.

### Step 5: Define Mitigations

For each identified threat, define a concrete mitigation with an owner and deadline.

### Worked Example: E-Commerce Checkout Flow Threat Model

| Component | Threat (STRIDE) | Attack Scenario | Risk | Mitigation |
|-----------|-----------------|-----------------|------|------------|
| Checkout API | **S** Spoofing | Attacker replays stolen session cookie | High | HttpOnly + SameSite=Strict cookies, short session TTL, bind session to device fingerprint |
| Checkout API | **T** Tampering | Client modifies item prices in POST body | Critical | Server re-fetches prices from catalog DB; never trust client-supplied prices |
| Payment Service | **I** Info Disclosure | Payment card numbers logged in application logs | Critical | PCI-DSS tokenization; PII redaction middleware; no raw card data outside payment processor |
| Order DB | **T** Tampering | SQL injection modifies order records | High | Parameterized queries only; DB user has no DDL permissions |
| Checkout API | **D** DoS | Bot submits thousands of checkout requests | High | Rate limit per user + per IP; CAPTCHA on checkout; queue-based order processing |
| Order Confirmation | **R** Repudiation | Customer claims they never placed an order | Medium | Signed order receipt emailed; tamper-evident audit log of all order events |
| Admin Endpoint | **E** Elevation | Regular user accesses /admin/orders endpoint | Critical | RBAC middleware on all admin routes; separate admin authentication flow with MFA |

### Blank Threat Model Template

Teams can copy this table for their own systems:

| Component | Trust Boundary | Threat (S/T/R/I/D/E) | Attack Scenario | Likelihood | Impact | Risk Rating | Mitigation | Owner | Status |
|-----------|---------------|----------------------|-----------------|------------|--------|-------------|------------|-------|--------|
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |

---

## 4.15 AuthN/AuthZ in Microservices Blueprint

In a microservices architecture, authentication and authorization are cross-cutting concerns that must be explicitly designed. The monolith's single session store is replaced by a distributed identity fabric.

### 4.15.1 Authentication Patterns

| Pattern | How It Works | Pros | Cons |
|---------|-------------|------|------|
| **API Gateway Auth (Centralized)** | Gateway validates tokens and passes verified identity (claims) downstream | Single enforcement point; services stay simple; easy to change auth provider | Gateway becomes bottleneck and SPOF; all traffic must traverse gateway |
| **Per-Service Auth (Decentralized)** | Each service validates tokens independently using shared public keys (JWKS) | No single point of failure; services are self-contained | Duplicated validation logic; harder to enforce consistent policies; key distribution complexity |
| **Hybrid (Recommended)** | Gateway performs initial token validation + rate limiting; services re-verify claims and enforce fine-grained authorization | Defense in depth; gateway handles coarse checks, services handle domain-specific checks | More complex to implement; requires shared understanding of token format |

### 4.15.2 Token Propagation Patterns

| Pattern | Mechanism | When to Use |
|---------|-----------|-------------|
| **JWT Forwarding** | Gateway forwards the original user JWT to downstream services | Simple; works when all services need the same user context; risk of token scope creep |
| **Token Exchange (RFC 8693)** | Service A exchanges user token for a new token scoped to Service B's needs | Principle of least privilege; downstream service gets only the claims it needs; audit trail shows delegation chain |
| **Phantom Tokens** | Gateway converts opaque tokens to JWTs for internal use; external clients never see JWTs | Best of both worlds — revocable opaque tokens externally, fast JWT validation internally |

### 4.15.3 Authorization Patterns

| Pattern | Description | Best For |
|---------|-------------|----------|
| **Centralized Policy Engine (OPA/Cedar)** | All services query a central policy engine for authorization decisions | Consistent policy enforcement; single audit point; policy-as-code |
| **Embedded Policy** | Each service contains its own authorization logic | Simple services with straightforward rules; low-latency requirements |
| **RBAC** | Permissions assigned to roles; users assigned to roles | Small number of well-defined roles; organizational hierarchies |
| **ABAC** | Permissions based on attributes of user, resource, action, and environment | Complex conditional access; regulatory environments; time-based or location-based rules |
| **ReBAC** | Permissions based on relationships between entities (graph-based) | Document sharing (Google Docs model); social features; hierarchical ownership |

### 4.15.4 Service-to-Service Authentication

| Method | How It Works | Strength |
|--------|-------------|----------|
| **mTLS** | Both client and server present TLS certificates; identity proven cryptographically | Strongest — identity is tied to infrastructure; no bearer tokens to steal |
| **JWT Service Accounts** | Services authenticate with JWTs issued by a shared IdP (client credentials grant) | Familiar pattern; works across network boundaries; easy to scope |
| **SPIFFE/SPIRE** | Services receive cryptographic identities (SVIDs) from a SPIRE server based on workload attestation | Zero-trust native; works across heterogeneous infrastructure; automatic rotation |

### 4.15.5 Full Auth Flow Diagram

```mermaid
sequenceDiagram
    participant User as User (Browser)
    participant GW as API Gateway
    participant Auth as Auth Service
    participant SA as Service A (Orders)
    participant SB as Service B (Payments)
    participant OPA as Policy Engine (OPA)

    User->>GW: 1. Request + Bearer Token
    GW->>GW: 2. Validate JWT signature (JWKS cache)
    GW->>GW: 3. Check token expiry, issuer, audience
    GW->>OPA: 4. Coarse-grained authz check (endpoint-level)
    OPA-->>GW: 5. Allow / Deny

    GW->>SA: 6. Forward request + verified claims header
    SA->>OPA: 7. Fine-grained authz (resource-level)
    OPA-->>SA: 8. Allow / Deny

    SA->>Auth: 9. Token exchange (RFC 8693) — request scoped token for Service B
    Auth-->>SA: 10. New scoped JWT (audience=Service B)

    SA->>SB: 11. Request + scoped JWT (over mTLS)
    SB->>SB: 12. Validate JWT + verify mTLS identity
    SB->>OPA: 13. Authz check for payment operation
    OPA-->>SB: 14. Allow / Deny
    SB-->>SA: 15. Payment result
    SA-->>GW: 16. Order response
    GW-->>User: 17. Response
```

### 4.15.6 Centralized vs Decentralized Auth — Trade-off Comparison

| Dimension | Centralized (Gateway Auth) | Decentralized (Per-Service Auth) | Hybrid |
|-----------|---------------------------|----------------------------------|--------|
| **Complexity** | Low for services | Higher per service | Medium overall |
| **Latency** | Single validation hop | Per-service validation (parallel with JWKS cache) | Gateway + service validation |
| **Resilience** | Gateway is SPOF | No single point of failure | Gateway failure degrades but services can self-validate |
| **Policy consistency** | Easy (one place) | Hard (each service must agree) | Good (shared policy engine) |
| **Token revocation** | Gateway blocklist | Each service must check blocklist | Gateway blocklist + short token TTL |
| **Audit** | Single audit point | Distributed audit logs | Gateway audit + service-level audit |
| **Recommended for** | Small teams, few services | Large teams, high autonomy | Most production microservice architectures |

---

## 4.16 OAuth 2.1 / OIDC Modern Standards

> This section consolidates the evolution from OAuth 2.0 to OAuth 2.1 and provides a reference for modern OIDC integration.

### 4.16.1 OAuth 2.1 Key Changes

OAuth 2.1 is a consolidation of OAuth 2.0 (RFC 6749) plus the security best practices that emerged from years of production deployment. It is not a breaking change but a strict subset.

| Change | OAuth 2.0 | OAuth 2.1 | Rationale |
|--------|-----------|-----------|-----------|
| **PKCE** | Optional (recommended for public clients) | **Mandatory for all clients** | Prevents authorization code interception even for confidential clients |
| **Implicit Grant** | Allowed (response_type=token) | **Removed** | Tokens in URL fragments are leaked via browser history, referrer headers, and logs |
| **Resource Owner Password Credentials** | Allowed (grant_type=password) | **Removed** | Exposes user credentials to the client; incompatible with MFA |
| **Refresh Token Rotation** | Optional | **Required or sender-constrained** | Detects token theft — if a stolen refresh token is used, rotation invalidates both old and new tokens |
| **Exact redirect URI matching** | Recommended | **Required** | Prevents open redirect attacks via partial URI matching |
| **Bearer tokens in query parameters** | Allowed | **Forbidden** | Query parameters are logged in server access logs and browser history |

### 4.16.2 OIDC Essentials

OpenID Connect (OIDC) adds an identity layer on top of OAuth 2.0:

| OIDC Concept | Purpose |
|-------------|---------|
| **ID Token** | JWT containing user identity claims (sub, name, email); returned alongside the access token |
| **UserInfo Endpoint** | REST endpoint returning user profile claims; called with the access token |
| **Discovery Document** | `/.well-known/openid-configuration` — machine-readable metadata about the IdP's endpoints, supported scopes, signing algorithms |
| **JWKS Endpoint** | `/.well-known/jwks.json` — public keys for validating token signatures |
| **Standard Scopes** | `openid` (required), `profile`, `email`, `address`, `phone` |
| **Nonce** | Random value bound to the ID token to prevent replay attacks |

### 4.16.3 Token Best Practices

| Token Type | Recommended TTL | Best Practices |
|-----------|----------------|----------------|
| **Access Token** | 5-15 minutes | Short-lived; never store in localStorage; use in Authorization header only |
| **Refresh Token** | 1-24 hours (with rotation) | Rotate on every use; detect reuse (invalidate family); store in HttpOnly cookie or secure backend |
| **ID Token** | Single-use at login | Validate immediately; do not use as an API credential; verify nonce, iss, aud, exp |

**Token binding** (DPoP — Demonstration of Proof of Possession, RFC 9449): Binds access tokens to a client-generated key pair so that a stolen token cannot be used by a different client. This is the strongest defense against token theft in browser-based applications.

### 4.16.4 OAuth 2.1 + PKCE Authorization Code Flow

```mermaid
sequenceDiagram
    participant User as User (Browser)
    participant App as Client Application
    participant AS as Authorization Server
    participant RS as Resource Server

    Note over App: Generate code_verifier (43-128 random chars)
    Note over App: code_challenge = BASE64URL(SHA256(code_verifier))

    App->>AS: 1. GET /authorize
    Note over App,AS: response_type=code<br/>client_id=app123<br/>redirect_uri=https://app.example.com/callback<br/>scope=openid profile email<br/>state=random_state<br/>nonce=random_nonce<br/>code_challenge=abc123<br/>code_challenge_method=S256

    AS->>User: 2. Display login + consent
    User->>AS: 3. Authenticate (password + MFA)
    AS->>App: 4. Redirect with authorization code
    Note over AS,App: ?code=auth_code_xyz&state=random_state

    App->>AS: 5. POST /token (back-channel)
    Note over App,AS: grant_type=authorization_code<br/>code=auth_code_xyz<br/>client_id=app123<br/>code_verifier=original_verifier<br/>redirect_uri=https://app.example.com/callback

    AS->>AS: 6. Verify SHA256(code_verifier) == stored code_challenge
    AS->>App: 7. { access_token, id_token, refresh_token }

    Note over App: 8. Validate ID token (sig, iss, aud, exp, nonce)

    App->>RS: 9. GET /api/resource + Authorization: Bearer access_token
    RS->>RS: 10. Validate access_token (signature, exp, scope)
    RS->>App: 11. Protected resource

    Note over App: 12. When access_token expires:
    App->>AS: 13. POST /token (grant_type=refresh_token)
    Note over AS: 14. Rotate refresh token (old token invalidated)
    AS->>App: 15. New { access_token, refresh_token }
```

---

## 4.17 Secure Defaults Checklist

Use these checklists during architecture reviews, PR reviews, and go-live readiness checks. Every item represents a default that should be on unless there is a documented exception.

### Web API Defaults

```
[ ] HTTPS only — redirect HTTP to HTTPS; HSTS header with min 1 year max-age and includeSubDomains
[ ] CORS — allowlist specific origins; never use Access-Control-Allow-Origin: *  in production
[ ] Content-Security-Policy (CSP) — restrict script sources; no unsafe-inline / unsafe-eval
[ ] X-Content-Type-Options: nosniff
[ ] X-Frame-Options: DENY  (or use CSP frame-ancestors)
[ ] Referrer-Policy: strict-origin-when-cross-origin
[ ] Permissions-Policy — disable unused browser features (camera, microphone, geolocation)
[ ] Secure cookies — HttpOnly, Secure, SameSite=Strict (or Lax for top-level navigation)
[ ] Response body — never include stack traces, internal IPs, or database error messages
[ ] API versioning — version in URL path or Accept header; reject unversioned requests
```

### Database Defaults

```
[ ] No public internet access — databases live in private subnets only
[ ] Encryption at rest — enabled for all volumes (AES-256 or equivalent)
[ ] TLS in transit — require TLS for all client connections; reject plaintext
[ ] Least-privilege roles — application user has SELECT/INSERT/UPDATE/DELETE only; no DDL, no SUPERUSER
[ ] Separate read/write users — read replicas use read-only credentials
[ ] Connection limits — max connections per user/application; connection pooling (PgBouncer, ProxySQL)
[ ] Audit logging — log all DDL operations, privilege changes, and failed login attempts
[ ] Automated backups — point-in-time recovery enabled; backups encrypted; tested restore procedure
```

### Container Defaults

```
[ ] Non-root user — RUN adduser / USER directive in Dockerfile; never run as UID 0
[ ] Read-only root filesystem — readOnlyRootFilesystem: true  in security context
[ ] No privileged mode — privileged: false; no SYS_ADMIN or NET_ADMIN capabilities
[ ] Drop all capabilities — securityContext.capabilities.drop: ["ALL"]; add back only what is needed
[ ] Minimal base image — use distroless, Alpine, or scratch; no shell, no package manager
[ ] Image scanning — Trivy/Grype/Snyk scan in CI; block deployment on critical/high CVEs
[ ] Signed images — cosign or Notation; enforce signature verification in admission controllers
[ ] No secrets in images — never COPY .env or embed credentials; use mounted secrets or env injection
[ ] Resource limits — set CPU and memory limits to prevent noisy-neighbor and DoS
```

### Kubernetes Defaults

```
[ ] NetworkPolicy — default-deny ingress and egress; explicitly allow required traffic
[ ] PodSecurityStandards — enforce "restricted" profile (no root, no host networking, no privileged)
[ ] RBAC — no cluster-admin bindings for applications; namespace-scoped roles only
[ ] No default service account — automountServiceAccountToken: false; create purpose-specific ServiceAccounts
[ ] Resource quotas — per-namespace quotas for CPU, memory, and pod count
[ ] Admission controllers — enforce policies (Kyverno/OPA Gatekeeper) for image sources, labels, security context
[ ] Secrets encryption — encrypt etcd at rest (EncryptionConfiguration); prefer external secrets operators (ESO)
[ ] Pod-to-pod mTLS — service mesh (Istio/Linkerd) or SPIFFE for workload identity
[ ] Audit logging — enable Kubernetes audit policy; ship logs to SIEM
```

### Cloud Defaults (AWS / GCP / Azure)

```
[ ] No public S3/GCS/Blob storage — block public access at the account/org level; use presigned URLs for sharing
[ ] VPC / private networking — all compute and data resources in private subnets; NAT gateway for outbound
[ ] Security groups / firewall rules — default-deny; allow only required ports and sources
[ ] CloudTrail / Cloud Audit Logs — enabled for all regions; ship to immutable log storage
[ ] IAM — no long-lived access keys; use IAM roles, workload identity, or OIDC federation
[ ] MFA on root / break-glass accounts — hardware key (YubiKey) for root; time-limited access for admin
[ ] GuardDuty / Security Command Center — enabled for anomaly detection
[ ] Config rules / Security Health Analytics — continuous compliance checks for drift detection
[ ] Tagging policy — enforce cost-center, environment, and owner tags for auditability
```

---

## 4.18 Secure Logging, Redaction, and Audit Trails

Logging is a security control, not just an operational convenience. Done right, it provides detection, forensics, and compliance evidence. Done wrong, it becomes a data breach vector.

### 4.18.1 What to Log

| Event Category | Examples | Why |
|---------------|----------|-----|
| **Authentication events** | Login success/failure, MFA challenges, password resets, token issuance | Detect credential stuffing, brute force, account takeover |
| **Authorization failures** | 403 responses, RBAC denials, policy engine rejections | Detect privilege escalation attempts, IDOR |
| **Data access** | Read/write to sensitive tables, file downloads, API calls returning PII | Compliance (HIPAA, SOX); insider threat detection |
| **Admin actions** | Config changes, user provisioning, role assignments, deployment triggers | Separation of duties audit; change management |
| **Security events** | WAF blocks, rate limit triggers, certificate errors, failed mTLS handshakes | Detect active attacks; tune security controls |

### 4.18.2 What NOT to Log

| Data Type | Risk if Logged | Alternative |
|-----------|---------------|-------------|
| **Passwords** (plaintext or hashed) | Credential theft from log storage | Log only "authentication attempt for user_id=X" |
| **Access / refresh tokens** | Token theft enables impersonation | Log token fingerprint (SHA-256 of first 8 chars) |
| **Credit card numbers** | PCI-DSS violation; financial fraud | Log last 4 digits only (e.g., ****1234) |
| **SSN / national ID** | Identity theft | Log only "SSN verified for user_id=X" |
| **PHI (health data)** | HIPAA violation | Log access event without the data itself |
| **Full request/response bodies** | May contain any of the above | Log sanitized summaries; use structured logging |

### 4.18.3 PII Redaction Patterns

| Pattern | How It Works | Use Case |
|---------|-------------|----------|
| **Field Masking** | Replace characters: `john@example.com` becomes `j***@e***.com` | Display in logs and support UIs |
| **Tokenization** | Replace PII with a random token; store mapping in a secure vault | Payment processing; cross-system references without exposing PII |
| **Hashing (one-way)** | SHA-256 of the value; allows correlation without reversibility | Log correlation ("same user across events") without storing PII |
| **Encryption (reversible)** | Encrypt PII with a key stored in KMS; decrypt only with audit trail | Regulatory hold / legal discovery; need to recover original value |

**Log redaction middleware example (Python):**

```python
import re
import json
import hashlib
from functools import wraps

# Patterns for common PII
PII_PATTERNS = {
    'email': (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', lambda m: m.group()[0] + '***@***'),
    'ssn': (r'\b\d{3}-\d{2}-\d{4}\b', lambda m: '***-**-' + m.group()[-4:]),
    'credit_card': (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', lambda m: '****-****-****-' + m.group()[-4:]),
    'bearer_token': (r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', lambda m: 'Bearer [REDACTED]'),
    'password_field': (r'"password"\s*:\s*"[^"]*"', lambda m: '"password": "[REDACTED]"'),
}

def redact_pii(log_message: str) -> str:
    """Redact PII from log messages using pattern matching."""
    redacted = log_message
    for field_name, (pattern, replacer) in PII_PATTERNS.items():
        redacted = re.sub(pattern, replacer, redacted)
    return redacted

def secure_log_context(user_id: str, action: str, resource: str, **extra) -> dict:
    """Create a structured, PII-safe log entry."""
    return {
        'timestamp': '...',  # Use ISO 8601
        'user_id_hash': hashlib.sha256(user_id.encode()).hexdigest()[:16],
        'action': action,
        'resource': resource,
        'ip_hash': extra.get('ip_hash', ''),
        'result': extra.get('result', 'success'),
        'metadata': {k: redact_pii(str(v)) for k, v in extra.items() if k not in ('ip_hash', 'result')},
    }
```

### 4.18.4 Audit Trail Requirements

| Requirement | Implementation | Why |
|------------|----------------|-----|
| **Tamper-evident** | Hash chain — each log entry includes a hash of the previous entry | Detects log deletion or modification |
| **Immutable storage** | Write-once storage (S3 Object Lock, WORM, append-only Kafka topic) | Prevents attackers from covering tracks |
| **Retention policy** | Defined per regulation (see table below); automated lifecycle | Legal compliance; storage cost management |
| **Access control** | Separate from application logs; read access requires justification | Prevents insiders from reading or modifying audit logs |
| **Timestamping** | NTP-synchronized clocks; UTC timestamps; include timezone offset | Forensic correlation across services |

### 4.18.5 Compliance Audit Requirements Comparison

| Requirement | GDPR | SOX | HIPAA | PCI-DSS |
|------------|------|-----|-------|---------|
| **What to log** | Processing activities, consent, data access, data subject requests | Financial transaction changes, access to financial data, system changes | All access to PHI, authentication events, security incidents | All access to cardholder data, authentication, admin actions |
| **Retention period** | As long as necessary for processing purpose; delete when no longer needed | 7 years minimum | 6 years minimum | 1 year minimum; 3 months immediately accessible |
| **Access control** | Data Protection Officer oversight; privacy-by-design | SOX auditor access; segregation of duties evidence | Minimum necessary access; break-glass audit | Need-to-know basis; quarterly access reviews |
| **Tamper protection** | Required (Article 32 — integrity of processing) | Required (Section 302/404 — internal controls) | Required (164.312(c)(1) — integrity controls) | Required (Requirement 10.5 — secure audit trails) |
| **Breach notification** | 72 hours to supervisory authority | Immediate to audit committee | 60 days to HHS and affected individuals | Varies by card brand; typically within 24-72 hours |
| **Right to deletion** | Yes (Right to Erasure, Article 17) | No (retention is mandatory) | No (retention is mandatory) | No (retention is mandatory) |

---

## 4.19 Attack Surface Reduction for Microservices

The attack surface is the sum of all points where an attacker can attempt to enter or extract data from a system. The goal is to minimize this surface area to the smallest possible set.

### 4.19.1 Core Principle

> **Minimize what is exposed; maximize what is monitored.** Every port, endpoint, dependency, and configuration option is a potential attack vector. Remove everything that is not strictly necessary.

### 4.19.2 Network-Level Attack Surface Reduction

| Pattern | Before | After |
|---------|--------|-------|
| **API Gateway as single entry point** | Each microservice has a public IP and exposed port | Only the API Gateway is internet-facing; internal services are in private subnets |
| **Internal services not internet-routable** | Services communicate over public internet | Services use private DNS and VPC-internal addresses; no public IPs |
| **Network segmentation** | Flat network — any service can talk to any other service | NetworkPolicies / security groups enforce least-privilege service-to-service communication |
| **Service mesh** | Direct HTTP between services | mTLS via sidecar proxy (Istio/Linkerd); traffic is encrypted and authenticated automatically |

### 4.19.3 Container Hardening

| Technique | What It Does | Tools |
|-----------|-------------|-------|
| **Minimal base images** | Distroless or scratch images remove shells, package managers, and unnecessary binaries | Google Distroless, Chainguard Images |
| **No shell access** | Without `/bin/sh`, an attacker who gains code execution cannot run arbitrary commands | Distroless images have no shell by default |
| **Read-only root filesystem** | Prevents an attacker from writing malicious files to the container filesystem | `readOnlyRootFilesystem: true` in Kubernetes security context |
| **Drop all capabilities** | Removes Linux capabilities (NET_RAW, SYS_PTRACE, etc.) that enable privilege escalation | `capabilities: { drop: ["ALL"] }` |
| **Seccomp profiles** | Restrict which system calls the container can make; blocks exploit primitives | Kubernetes RuntimeDefault profile; custom profiles for hardened workloads |

### 4.19.4 Dependency Management

| Practice | Purpose | Tools |
|----------|---------|-------|
| **Software Bill of Materials (SBOM)** | Machine-readable inventory of all dependencies; enables rapid response to CVEs | Syft, Trivy, CycloneDX |
| **Vulnerability scanning** | Detect known CVEs in dependencies and base images | Trivy, Grype, Snyk, GitHub Dependabot alerts |
| **Automated updates** | Keep dependencies current; patch vulnerabilities within SLA | Dependabot, Renovate Bot, Mend |
| **Dependency pinning** | Pin exact versions (lock files); prevent supply chain attacks via version injection | package-lock.json, go.sum, poetry.lock |
| **Private registry** | Proxy and cache dependencies; control which packages are allowed | Artifactory, Nexus, GitHub Packages |

### 4.19.5 Runtime Protection

| Tool | What It Does | Detection Examples |
|------|-------------|-------------------|
| **Falco** | Runtime anomaly detection using kernel-level system call monitoring | Unexpected shell execution in container, read of /etc/shadow, outbound connection to suspicious IP |
| **Seccomp profiles** | Whitelist of allowed system calls; blocks everything else | Blocks `ptrace` (used for process injection), `mount` (container escape), `keyctl` (credential theft) |
| **AppArmor / SELinux** | Mandatory access control at the OS level | Restrict file access, network access, and capability usage per container |
| **eBPF-based observability** | Kernel-level monitoring without performance overhead | Cilium Tetragon for network policy enforcement and process monitoring |

### 4.19.6 Attack Surface Before vs After Hardening

```mermaid
graph TB
    subgraph Before["BEFORE: Large Attack Surface"]
        Internet1[Internet] --> S1[Service A :8080<br/>Public IP]
        Internet1 --> S2[Service B :8080<br/>Public IP]
        Internet1 --> S3[Service C :8080<br/>Public IP]
        Internet1 --> DB1[(Database :5432<br/>Public IP)]
        S1 --> S2
        S1 --> S3
        S2 --> S3
        S2 --> DB1
        S3 --> DB1
        S1 --> DB1

        style S1 fill:#ff6b6b,color:#000
        style S2 fill:#ff6b6b,color:#000
        style S3 fill:#ff6b6b,color:#000
        style DB1 fill:#ff6b6b,color:#000
    end

    subgraph After["AFTER: Reduced Attack Surface"]
        Internet2[Internet] --> WAF[WAF / CDN]
        WAF --> GW[API Gateway<br/>Only public endpoint]
        GW -->|mTLS| S4[Service A<br/>Private subnet<br/>Distroless, non-root]
        GW -->|mTLS| S5[Service B<br/>Private subnet<br/>Distroless, non-root]
        S4 -->|mTLS| S6[Service C<br/>Private subnet<br/>Distroless, non-root]
        S5 -->|NetworkPolicy| DB2[(Database<br/>Private subnet<br/>Encrypted, no public IP)]
        S6 -->|NetworkPolicy| DB2

        style GW fill:#51cf66,color:#000
        style S4 fill:#51cf66,color:#000
        style S5 fill:#51cf66,color:#000
        style S6 fill:#51cf66,color:#000
        style DB2 fill:#51cf66,color:#000
    end
```

**Key reductions achieved:**
- **Network exposure:** 4 public endpoints reduced to 1 (API Gateway behind WAF).
- **Service communication:** Unencrypted flat network replaced with mTLS + NetworkPolicies.
- **Database access:** Public IP removed; access restricted to specific services via NetworkPolicy.
- **Container attack surface:** Full OS images replaced with distroless; non-root; read-only filesystem; capabilities dropped.
- **Dependency risk:** SBOM generated; vulnerabilities scanned in CI; automated updates via Renovate.
- **Runtime detection:** Falco monitors for anomalous system calls; seccomp profiles block exploit primitives.

---

# Architectural Decision Records (ADRs)

## ADR-1: JWT vs Session-Based Authentication for the API Layer

**Status:** Accepted

**Context:** The system consists of a web frontend (SPA), mobile clients, and 15+ backend microservices. We need to choose between session-based authentication and JWT-based authentication for the API layer.

**Decision:** Use a hybrid approach:
- **Browser ↔ BFF:** Session-based authentication with HttpOnly cookies stored in Redis.
- **BFF ↔ Microservices:** Short-lived JWTs (5-minute expiry) with RS256 signing.

**Consequences:**
- (+) Browser tokens are not accessible to JavaScript (XSS protection).
- (+) Microservices can validate tokens without calling the auth service.
- (+) Session revocation is immediate for browser sessions (delete Redis key).
- (-) Adds BFF layer complexity.
- (-) JWT revocation between services requires short expiry + cache-based blocklist.

**Alternatives considered:**
- Pure JWT for all clients — rejected because JWT revocation is difficult and tokens are exposed to JavaScript in SPAs.
- Pure sessions for all clients — rejected because it requires a shared session store accessible by all microservices, creating a single point of failure.

---

## ADR-2: Authorization Model Selection

**Status:** Accepted

**Context:** The system has multi-tenant data, per-resource sharing (documents can be shared with specific users and teams), and organizational role hierarchies. We need an authorization model that handles all three.

**Decision:** Use ReBAC (Zanzibar-style) via SpiceDB for fine-grained per-resource authorization, combined with RBAC for coarse organizational roles.

**Consequences:**
- (+) Per-resource sharing is naturally modeled as relationships.
- (+) Permission inheritance through the resource hierarchy (org → team → project → document) is built-in.
- (+) "Who has access to X?" queries are efficient for compliance auditing.
- (-) SpiceDB is an additional infrastructure component to operate.
- (-) Developers must learn the Zanzibar model and relation tuple concepts.

**Alternatives considered:**
- Pure RBAC — rejected because per-resource sharing would require creating a role per resource per user (role explosion).
- Pure ABAC with OPA — rejected because relationship traversal (team membership → project access) is awkward in Rego.

---

## ADR-3: Encryption Strategy

**Status:** Accepted

**Context:** The system handles PII (names, emails, addresses), financial data (payment information), and health data (for a wellness feature). Regulatory requirements include GDPR and SOC 2.

**Decision:** Implement three-tier encryption:
1. **Storage-level** — enable encryption at rest for all databases (RDS encryption) and object stores (S3 SSE-KMS).
2. **Application-level** — encrypt PII fields (SSN, date of birth, health data) using envelope encryption with AWS KMS before storing in the database.
3. **Transit** — TLS 1.3 for all external connections; mTLS between internal services via service mesh.

**Consequences:**
- (+) Database compromise does not expose PII in plaintext.
- (+) Meets GDPR "appropriate technical measures" requirement.
- (+) Key rotation is automated through KMS.
- (-) Application-level encryption prevents database-level search on encrypted fields (requires blind indexes).
- (-) Envelope encryption adds latency (~5ms per KMS call, mitigated by DEK caching).

---

## ADR-4: Rate Limiting Architecture

**Status:** Accepted

**Context:** The API serves both authenticated users and anonymous traffic. We need to protect against abuse, ensure fairness, and support tiered rate limits for different API plans.

**Decision:** Implement two-layer rate limiting:
1. **API Gateway layer** — per-IP rate limiting for anonymous traffic and per-API-key rate limiting for authenticated traffic. Uses Redis-backed sliding window.
2. **Service layer** — per-endpoint rate limiting for expensive operations (search, report generation). Uses local token bucket with periodic Redis sync.

**Consequences:**
- (+) Abuse is caught at the gateway before reaching backend services.
- (+) Expensive endpoints have independent protection.
- (+) Tiered plans (free: 100 req/min, pro: 1000 req/min) are enforceable.
- (-) Two layers add complexity; must ensure consistent behavior.
- (-) Redis dependency for distributed rate limiting; must handle Redis outages (fail-open with logging).

---

## ADR-5: Zero Trust Adoption

**Status:** Accepted

**Context:** The system is deployed on Kubernetes across three regions. Historically, internal services communicated over plaintext HTTP within the cluster. A recent incident where a compromised pod accessed an unrelated database highlighted the need for stronger internal security.

**Decision:** Adopt zero trust incrementally:
1. **Phase 1** — Deploy Istio service mesh with mTLS for all service-to-service communication.
2. **Phase 2** — Implement Kubernetes NetworkPolicies to restrict pod-to-pod traffic to declared dependencies.
3. **Phase 3** — Deploy OPA as an Istio authorization policy engine to enforce per-request authorization for internal APIs.
4. **Phase 4** — Replace VPN-based developer access with identity-aware proxy (Pomerium).

**Consequences:**
- (+) Lateral movement is eliminated — a compromised service cannot access unrelated services.
- (+) All internal traffic is encrypted and authenticated.
- (+) Per-request authorization provides fine-grained access control between services.
- (-) Istio adds operational complexity and resource overhead (~10% CPU increase per pod).
- (-) Requires updating all services to propagate identity context (user JWT or service identity).

---

# Interview Angle

## How Security Comes Up in System Design Interviews

Security is rarely the primary focus of a system design interview, but it is frequently a follow-up dimension that separates strong candidates from average ones. Here is how to weave security into your answers:

### When the Interviewer Asks "How Do You Secure This?"

**Framework for answering:**

1. **Authentication** — how do users prove their identity? Mention OAuth 2.0 + OIDC, JWTs, and session management. For service-to-service, mention mTLS or service accounts.

2. **Authorization** — how do you control who can access what? Mention RBAC for organizational roles, ReBAC for per-resource sharing, and OPA/Cedar for policy externalization.

3. **Data protection** — encryption at rest (AES-256-GCM, KMS), encryption in transit (TLS 1.3), application-level encryption for sensitive fields.

4. **Rate limiting and abuse prevention** — token bucket at the API gateway, per-user and per-IP limits, WAF for L7 protection.

5. **Input validation** — parameterized queries, allow-list validation, CSP headers.

6. **Audit and monitoring** — log all authentication events, authorization decisions, and data access. Alert on anomalies.

### Common Security Questions in Interviews

**Q: "How would you design an authentication system?"**
Cover: OAuth 2.0 with PKCE for user-facing auth, client credentials for service-to-service, JWTs for stateless validation, refresh token rotation, BFF pattern for SPAs.

**Q: "How do you prevent one user from accessing another user's data?"**
Cover: IDOR prevention through ownership checks, RBAC/ReBAC for access control, row-level security as defense in depth, parameterized queries to prevent injection.

**Q: "How do you handle secrets in a microservices architecture?"**
Cover: HashiCorp Vault or AWS Secrets Manager, dynamic secrets with short TTLs, identity-based access (Kubernetes service accounts), no secrets in code or environment variables.

**Q: "What happens if a service is compromised?"**
Cover: Zero trust (the compromised service cannot access unrelated services), micro-segmentation (NetworkPolicies), mTLS (identity is per-service, not per-network), short-lived credentials (blast radius is time-limited), audit logs (detect the compromise quickly).

**Q: "How do you protect against DDoS?"**
Cover: CDN/DDoS shield at the edge (Cloudflare, AWS Shield), WAF for L7 attacks, rate limiting at the gateway, origin hiding, auto-scaling with circuit breakers.

### Key Vocabulary to Use in Interviews

| Term | When to Use It |
|------|---------------|
| **Defense in depth** | When explaining layered security controls |
| **Least privilege** | When discussing access control and permissions |
| **Fail closed** | When describing error handling for security controls |
| **Blast radius** | When discussing the impact of a compromise |
| **Zero trust** | When explaining internal network security |
| **Envelope encryption** | When discussing encryption at scale |
| **Token rotation** | When discussing credential lifecycle |
| **IDOR** | When discussing authorization vulnerabilities |
| **mTLS** | When discussing service-to-service authentication |
| **PKCE** | When discussing OAuth for public clients |

### Security Trade-offs to Discuss

| Trade-off | Dimension A | Dimension B |
|-----------|-------------|-------------|
| **Latency vs security** | mTLS adds handshake overhead | Plaintext is faster but insecure |
| **Usability vs security** | MFA adds friction | No MFA allows credential stuffing |
| **Cost vs security** | DDoS protection services are expensive | Unprotected systems are vulnerable |
| **Complexity vs security** | Zero trust requires significant infrastructure | Flat networks are simpler but less secure |
| **Revocability vs performance** | Sessions allow instant revocation | JWTs avoid session store lookups |
| **Granularity vs simplicity** | ReBAC handles complex sharing models | RBAC is simpler to understand and audit |

---

# Practice Questions

## Fundamentals

**Q1.** You are designing an API for a mobile banking app. The API handles balance inquiries, transfers, and bill payments. Describe the authentication and authorization architecture, including token lifecycle, MFA requirements, and session management.

**Q2.** A SaaS platform uses JWTs with 24-hour expiration for API authentication. Users report that changing their password does not log them out of other devices. Explain the root cause and propose two solutions with trade-offs.

**Q3.** An e-commerce platform uses RBAC with roles: `admin`, `seller`, `buyer`. The platform is adding features where sellers can have employees with different access levels, and buyers can share wishlists with family members. The current RBAC model is showing strain. Propose an authorization model that handles these new requirements.

**Q4.** Explain the difference between OAuth 2.0 authorization code flow and authorization code flow with PKCE. When would you use each? Why is PKCE now recommended for all clients?

**Q5.** A team stores API tokens in localStorage for their SPA. An XSS vulnerability is discovered. Describe the attack chain and propose a more secure token storage strategy.

## Architecture and Design

**Q6.** Design a rate limiting system for a public API that supports:
- Free tier: 100 requests/minute
- Pro tier: 1,000 requests/minute
- Enterprise tier: custom limits
- Burst allowance (2x sustained rate for 10 seconds)
- Distributed across 10 API gateway instances

Specify the algorithm, data store, and failure mode.

**Q7.** You are migrating a monolithic application to microservices. The monolith uses server-side sessions stored in PostgreSQL. Propose a migration strategy for authentication and authorization that does not require a big-bang rewrite.

**Q8.** Design an encryption strategy for a healthcare application that stores patient records, medical images, and appointment data. The application must comply with HIPAA. Address encryption at rest, in transit, and application-level. Explain key management and rotation.

**Q9.** A company discovers that an internal service was compromised and has been exfiltrating data for 3 weeks. The service had access to the user database, payment service, and analytics pipeline. Propose a zero trust architecture that would have limited the blast radius of this incident.

**Q10.** Design a secrets management system for a Kubernetes-based microservices platform with 50 services. Requirements: no secrets in code or config maps, automatic rotation, audit logging, and support for both database credentials and API keys.

## Deep Dives

**Q11.** Compare Google Zanzibar (ReBAC) with OPA (ABAC) for a document collaboration platform (like Google Docs). Consider permission model expressiveness, query patterns, performance, and operational complexity.

**Q12.** A content delivery platform serves 500,000 requests per second. During a recent DDoS attack, the origin servers were overwhelmed despite having a CDN. Diagnose possible causes and propose a comprehensive DDoS mitigation architecture.

**Q13.** Your organization uses SAML-based SSO for 50 internal applications. The business wants to add support for mobile apps and a public API. SAML does not work well for these use cases. Propose a migration strategy from SAML to OIDC that maintains backward compatibility.

**Q14.** Design a multi-tenant authorization system where:
- Each tenant has its own roles and permissions (tenant-defined RBAC).
- Some resources can be shared across tenants.
- Administrators of one tenant cannot see or modify another tenant's configuration.
- The system serves 10,000 tenants with a P99 authorization check latency of <5ms.

**Q15.** A fintech company processes 1 million transactions per day. Each transaction involves a payment service, fraud detection service, ledger service, and notification service. Design the end-to-end security architecture covering: authentication between services, authorization for transaction operations, encryption of financial data, audit logging, and key management.

**Q16.** You are designing a webhook delivery system that sends events to customer-configured HTTPS endpoints. How do you:
- Authenticate the webhook (prove it came from your system)?
- Prevent SSRF when the customer provides a destination URL?
- Handle replay attacks?
- Ensure confidentiality of the payload?

**Q17.** A startup with 5 engineers is building a B2B SaaS product. They have limited security expertise but need to meet SOC 2 Type II requirements within 12 months. Propose a prioritized security roadmap that balances investment with risk reduction, covering the most impactful controls first.

---

# Summary

## Section 1: Authentication — Key Takeaways

| Topic | Key Insight |
|-------|-------------|
| **OAuth 2.0** | Use authorization code + PKCE for all clients; client credentials for machine-to-machine; short-lived access tokens + refresh token rotation |
| **JWT** | Validate signature, algorithm, expiration, issuer, and audience on every request; prefer RS256/ES256 for multi-service validation; keep payloads lean |
| **Sessions** | HttpOnly + Secure + SameSite cookies; Redis for session store; regenerate session ID after login; absolute + sliding timeout |
| **MFA** | WebAuthn/FIDO2 is phishing-resistant; TOTP is widely supported; SMS is weak but better than nothing; always provide recovery codes |
| **SSO** | OIDC for new systems, SAML for enterprise legacy; session management across services is the hard problem |
| **API Auth** | API keys for identification (not authentication); mTLS for mutual authentication; HMAC for tamper-proof requests |

## Section 2: Authorization — Key Takeaways

| Topic | Key Insight |
|-------|-------------|
| **RBAC** | Simple and effective for organizational hierarchies; watch for role explosion; use scoped roles to reduce count |
| **ABAC** | Flexible but complex; use when RBAC cannot express the required policies; externalize with OPA or Cedar |
| **ReBAC** | Natural fit for resource-sharing models; Zanzibar-style systems handle complex permission inheritance; operational overhead is real |
| **Policy Engines** | Decouple authorization from code; OPA for general-purpose; Cedar for analyzable authorization; Casbin for embedded use |
| **Row-Level Security** | Defense in depth for multi-tenant data; PostgreSQL RLS eliminates missing-filter bugs; index RLS columns |

## Section 3: Infrastructure Security — Key Takeaways

| Topic | Key Insight |
|-------|-------------|
| **Encryption** | AES-256-GCM at rest; TLS 1.3 in transit; envelope encryption for scale; application-level for sensitive fields |
| **Secrets** | Never in code; use Vault or Secrets Manager; dynamic secrets with short TTLs; identity-based access |
| **Rate Limiting** | Token bucket for most cases; Redis for distributed coordination; two layers (gateway + service); fail-open with logging if Redis is down |
| **DDoS** | CDN/shield at the edge for L3/L4; WAF for L7; rate limiting at the gateway; hide origin IPs |

## Section 4: Application Security — Key Takeaways

| Topic | Key Insight |
|-------|-------------|
| **OWASP Top 10** | Broken access control is #1; parameterized queries prevent injection; CSP prevents XSS; SameSite cookies prevent CSRF |
| **Input Validation** | Always allow-list; never deny-list; validate on the server regardless of client validation |
| **Secure SDLC** | STRIDE threat modeling; dependency scanning in CI/CD; security headers on all responses |
| **Zero Trust** | Never trust the network; authenticate every request; mTLS between services; micro-segment with NetworkPolicies |

---

## Quick Reference: Security Design Checklist

Use this checklist when designing or reviewing any system:

```
Authentication
  [ ] User authentication mechanism defined (OAuth 2.0 + OIDC / sessions)
  [ ] Token storage strategy chosen (HttpOnly cookies / BFF / OS keychain)
  [ ] Token expiration and refresh strategy defined
  [ ] MFA required for sensitive operations
  [ ] Service-to-service authentication defined (mTLS / JWT / API keys)

Authorization
  [ ] Authorization model selected (RBAC / ABAC / ReBAC)
  [ ] Every endpoint has explicit authorization checks
  [ ] Resource ownership validated on every data access
  [ ] Multi-tenant isolation enforced (RLS / application filter / separate DB)
  [ ] Admin access is scoped and audited

Data Protection
  [ ] Encryption at rest enabled for all data stores
  [ ] TLS 1.3 for all external communication
  [ ] Application-level encryption for PII and sensitive fields
  [ ] Key management and rotation strategy defined
  [ ] Secrets stored in a secrets manager (not code/config)

Network Security
  [ ] Rate limiting configured (per-user, per-IP, per-API-key)
  [ ] DDoS protection at the edge
  [ ] WAF rules for common attack patterns
  [ ] Origin server IPs hidden behind CDN
  [ ] Internal traffic encrypted (mTLS or service mesh)

Application Security
  [ ] Parameterized queries for all database access
  [ ] Input validation (allow-list) on all endpoints
  [ ] CSP header configured
  [ ] Security headers set (HSTS, X-Content-Type-Options, etc.)
  [ ] Dependency scanning in CI/CD
  [ ] Threat model documented and reviewed

Monitoring and Response
  [ ] Authentication events logged
  [ ] Authorization failures logged and alerted
  [ ] Data access patterns monitored for anomalies
  [ ] Incident response plan documented
  [ ] Security patches applied within SLA
```
