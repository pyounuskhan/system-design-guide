# Video & Streaming Platforms — Operational Runbooks

## Runbook 001: Transcoding Queue Backlog

### Severity: P2 (High)
### Detection: `transcoding.queue.depth > 10,000` or `transcoding.sla.breached` (jobs > 2 hours old)

### Impact
- New videos delayed in becoming available. Creators see "Processing" for hours instead of minutes.

### Investigation
1. Check GPU worker utilization: `kubectl top pods -l app=transcoder`
2. Check for poison jobs (repeatedly failing): query DLQ
3. Check if a burst of long/4K videos is causing longer-than-normal encode times
4. Check S3 latency (source file reads)

### Resolution
1. **Scale up**: Add transcoding worker pods (up to GPU quota)
2. **Priority rebalance**: Ensure short videos (< 5 min) aren't stuck behind 12-hour videos
3. **Poison jobs**: Send to DLQ; alert content team; don't let failures block the queue
4. **Emergency**: If SLA widely breached, temporarily disable lower-priority variants (skip 240p/360p) to clear the queue faster

---

## Runbook 002: CDN Cache Hit Rate Drop

### Severity: P1 (High)
### Detection: `cdn.edge.cache_hit_rate < 80%` or `cdn.origin.bandwidth > 25 PB/day`

### Impact
- Increased origin load, higher latency for viewers, higher bandwidth costs.

### Investigation
1. Check if a viral video is causing mass cache misses (new content not yet cached)
2. Check if CDN config changed (cache TTL reduced, purge event)
3. Check if origin is returning errors (5xx → CDN doesn't cache)
4. Check segment naming — any changes that invalidate existing cache keys?

### Resolution
1. **Viral content**: Trigger manual pre-warm to all edge PoPs
2. **Config issue**: Revert cache TTL; verify cache headers on origin responses
3. **Origin errors**: Fix origin issue; CDN will re-cache on successful responses
4. **Long-term**: Increase edge cache size; implement origin shield if not present

---

## Runbook 003: High Rebuffering Rate

### Severity: P1 (High — directly impacts viewer experience)
### Detection: `playback.rebuffer_rate > 2%` (sessions with at least one rebuffer)

### Impact
- Viewers experience playback stalls. Every 1% rebuffer increase = ~3% watch time drop.

### Investigation
1. **Regional?** Check rebuffer rate by CDN PoP. If one region is affected, likely CDN/network issue.
2. **Device-specific?** If mobile-only, may be ABR algorithm issue on mobile clients.
3. **Content-specific?** If only new videos, may be encoding issue (bitrate too high for target).
4. **CDN-specific?** Check per-CDN metrics if using multi-CDN.

### Resolution
1. **Regional CDN issue**: Steer traffic to alternate CDN or PoP using DNS/traffic manager
2. **ABR issue**: Push client update; reduce aggressive quality ramp-up
3. **Encoding issue**: Re-encode affected videos with lower peak bitrate
4. **Network congestion**: Nothing platform can do; ABR should adapt automatically

---

## Runbook 004: Live Stream Ingest Failure

### Severity: P1 (High for active streams)
### Detection: `live.ingest.error_rate > 5%` or creator reports stream dropping

### Investigation
1. Check ingest server health and capacity
2. Check creator's network (packet loss shown in RTMP stats)
3. Check if specific ingest region is overloaded
4. Check for software update on ingest servers (recent deploy?)

### Resolution
1. **Creator network issue**: Suggest lower bitrate/resolution to creator
2. **Ingest server overload**: Scale up or redirect to less-loaded ingest server
3. **Ingest server crash**: Auto-failover to backup server; creator reconnects automatically within 30 seconds
4. **Regional outage**: Redirect RTMP endpoint DNS to alternate region

---

## Runbook 005: DRM License Server Degraded

### Severity: P1 (High — premium content unplayable)
### Detection: `drm.license.error_rate > 5%` or `drm.license.latency_p99 > 3s`

### Impact
- Viewers cannot start playing DRM-protected content. Free content unaffected.

### Investigation
1. Check which DRM system is affected (Widevine, FairPlay, PlayReady)
2. Check license server health and logs
3. Check HSM key server connectivity
4. Check if certificate rotation recently occurred

### Resolution
1. **Server overload**: Scale license server instances
2. **HSM connectivity**: Verify network path to HSM; failover to backup HSM
3. **Certificate issue**: Rollback to previous certificate; investigate rotation failure
4. **Vendor outage (Widevine/FairPlay)**: Nothing we can do for the vendor-hosted parts; communicate to users; free content still works

### Mitigation
- Cache licenses client-side for offline playback
- License proxy that caches recent licenses for retry scenarios

---

## Runbook 006: Recommendation Quality Degradation

### Severity: P2 (High — impacts engagement)
### Detection: `recommendation.ctr < baseline - 10%` or `recommendation.watch_through_rate declining`

### Investigation
1. Check if recent model deployment occurred
2. Check if feature store is returning stale data
3. Check if candidate generation is producing fewer candidates
4. Check if a content moderation change removed a large pool of recommendable content

### Resolution
1. **Bad model deploy**: Rollback to previous model version
2. **Feature store issue**: Fix feature pipeline; pre-computed features may need refresh
3. **Candidate pool issue**: Check content indexing pipeline
4. **Temporary**: Fallback to trending/popular-based recommendations until model recovers

---

## Runbook 007: Major Live Event Preparation

### Severity: Proactive (run 48 hours before scheduled event)
### Context: Concert, sports event, or creator event expected to draw > 1M concurrent viewers

### Checklist

**48 hours before:**
- [ ] Confirm ingest server capacity in creator's region
- [ ] Pre-warm CDN edges in expected viewer regions
- [ ] Scale live transcoding workers to 3x normal
- [ ] Scale chat service WebSocket gateways to expected viewer count
- [ ] Configure chat rate limits (sampling at > 10K msg/sec)
- [ ] Notify CDN providers of expected traffic with time and volume estimate
- [ ] Set up dedicated monitoring dashboard for the event

**1 hour before:**
- [ ] Creator performs test stream; verify all quality levels working
- [ ] Verify DRM licenses (if premium) issuing correctly
- [ ] On-call engineer assigned to event for duration
- [ ] Viewer count monitoring active

**During event:**
- Monitor: concurrent viewers, rebuffer rate, chat message rate, CDN origin load
- Be ready to: scale workers, switch CDN, increase chat sampling, extend viewer capacity

**After event:**
- [ ] Trigger VOD archival from live recording
- [ ] Capture event metrics for capacity planning
- [ ] Scale down resources
