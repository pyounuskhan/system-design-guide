# Social Media & Content Platforms — Operational Runbooks

## Runbook 001: Feed Cache (Redis) Cluster Failure

### Severity: P0 (Critical)
### Detection: `redis.feed.cluster.unreachable` or `feed.load.error_rate > 50%`

### Impact
- All users see empty or stale feeds
- Primary product surface is down

### Response
1. **Immediate (< 5 min)**: Switch feed reads to degraded mode:
   - Serve trending/popular posts as fallback feed
   - Show "Feed is temporarily loading differently" banner
2. **If Redis recoverable (< 30 min)**:
   - Wait for Redis cluster auto-recovery (replica promotion)
   - Verify cluster health: `redis-cli cluster info`
   - Feeds will be stale but functional; fanout workers rebuild caches
3. **If Redis unrecoverable**:
   - Switch to DB-backed feed computation (slow, 2-5s per feed)
   - Prioritize rebuilding feeds for active users (recently online)
   - Rebuild feed cache for all users in background (hours)

### Prevention
- Redis Cluster with 3+ replicas per shard
- Regular Redis persistence snapshots (RDB every 15 min)
- Automated failover testing monthly

---

## Runbook 002: Fanout Worker Backlog

### Severity: P1 (High)
### Detection: `kafka.consumer_lag.fanout_workers > 100,000` or `feed.freshness.delay > 60s`

### Impact
- New posts appearing in feeds with minutes of delay instead of seconds
- Users see stale content

### Investigation
1. Check Kafka consumer lag per partition
2. Check fanout worker CPU/memory utilization
3. Check if a mega-creator post triggered excessive fanout (miscategorized as regular user)
4. Check Redis latency (slow Redis = slow fanout)

### Resolution
1. **Scale up**: Increase fanout worker replicas (up to Kafka partition count)
2. **Mega-creator leak**: If a user with > 10K followers is being fanned out on write, add to mega-creator list immediately
3. **Redis slow**: Address Redis issues first (see Runbook 001)
4. **Kafka partition hot**: Rebalance partitions; check partition key distribution

---

## Runbook 003: Media Pipeline Backlog

### Severity: P2 (High)
### Detection: `media.processing.queue_depth > 50,000` or `media.processing.latency_p99 > 5min`

### Impact
- Posts appear without images/videos (placeholder shown)
- Stories and Reels creation delayed

### Investigation
1. Check transcoding worker count and utilization
2. Check for unusually large/complex media (8K video, very long videos)
3. Check S3 upload latency
4. Check for poison messages (media that fails processing repeatedly)

### Resolution
1. Scale up transcoding workers
2. Send poison messages to DLQ; alert content team
3. If S3 issues: check S3 service health; switch to backup region
4. Prioritize: process stories/reels before regular post images (time-sensitive)

---

## Runbook 004: Content Moderation ML Model Degraded

### Severity: P1 (High)
### Detection: `moderation.model.latency_p99 > 500ms` or `moderation.model.error_rate > 5%`

### Impact
- Violating content not caught before distribution
- Potential advertiser safety and regulatory risk

### Response
1. **Immediate**: Fall back to rules-only layer (lower recall but no latency)
2. Check model serving infrastructure (GPU utilization, memory, model loading)
3. If recent model deploy: rollback to previous model version
4. Alert Trust & Safety team: increase human review capacity
5. Monitor for increase in user reports (indicates missed violations)

---

## Runbook 005: Viral Event (Unexpected Traffic Spike)

### Severity: Proactive
### Detection: `post.creation.rate > 3x baseline` or `feed.request.rate > 2x baseline`

### Impact
- Global event (election, natural disaster, celebrity incident) causes traffic spike
- Systems may approach capacity limits

### Response
1. **Monitor**: Activate event dashboard; assign on-call to watch key metrics
2. **Scale preemptively**: Increase API gateway, feed service, fanout workers by 2x
3. **Cache aggressively**: Increase CDN TTLs for trending content
4. **Moderation alert**: Spike may include misinformation/harmful content; alert T&S
5. **Rate limit if needed**: Reduce non-critical API rate limits (e.g., search, analytics)

---

## Runbook 006: WebSocket Gateway Overload (Messaging/Notifications)

### Severity: P1 (High)
### Detection: `websocket.connections > 90% capacity` or `websocket.message_delivery.latency > 5s`

### Impact
- Notifications and messages delayed
- Users see "connecting..." in chat

### Response
1. Scale WebSocket gateway instances
2. If connection count is the limit: increase max connections per instance or add instances
3. Verify presence service is routing correctly across gateway instances
4. If messages are backed up: increase Kafka consumer group for delivery workers
5. Fallback: clients switch to polling (30s interval) if WebSocket fails

---

## Runbook 007: Coordinated Abuse Attack

### Severity: P1 (High)
### Detection: `abuse.network.detected` event with high confidence, or spike in user reports

### Response
1. **Do NOT publicly acknowledge the attack** (may encourage escalation)
2. Review detected account network in T&S dashboard
3. If confirmed coordinated:
   - Suspend all accounts in the network
   - Remove all content posted by the network
   - Rate-limit new account creation from associated IPs/devices
4. If targeting specific users:
   - Enable enhanced protections for targeted users (comment filtering, mention restrictions)
   - Notify targeted users with support resources
5. Post-incident: update abuse detection models with new signals from this attack
