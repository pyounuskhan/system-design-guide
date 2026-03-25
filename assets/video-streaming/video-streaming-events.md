# Video & Streaming Platforms — Event Catalog

## Video Lifecycle Events

### `video.upload.completed`
```json
{"event_type": "video.upload.completed", "data": {"video_id": "vid_abc", "creator_id": "usr_xyz", "source_url": "s3://uploads/vid_abc/source.mp4", "duration_sec": 600, "source_resolution": "3840x2160", "size_bytes": 2147483648}}
```
**Consumers**: Transcoding Scheduler, Thumbnail Generator, Metadata Enrichment

### `video.transcode.started`
```json
{"event_type": "video.transcode.started", "data": {"job_id": "job_123", "video_id": "vid_abc", "profiles": ["240p", "360p", "480p", "720p", "1080p", "4K"]}}
```
**Consumers**: Creator Dashboard (show progress)

### `video.transcode.completed`
```json
{"event_type": "video.transcode.completed", "data": {"job_id": "job_123", "video_id": "vid_abc", "variants": [{"resolution": "1080p", "codec": "h264", "bitrate_kbps": 6000, "vmaf": 94.2}], "total_duration_min": 45}}
```
**Consumers**: DRM Encryptor, CDN Pre-warm, Metadata Service

### `video.ready`
```json
{"event_type": "video.ready", "data": {"video_id": "vid_abc", "manifest_url": "https://cdn.example.com/vid_abc/master.m3u8", "thumbnail_url": "https://cdn.example.com/vid_abc/thumb.jpg"}}
```
**Consumers**: Recommendation Engine, Search Indexer, Creator Notification, Subscriber Notification

### `video.deleted`
```json
{"event_type": "video.deleted", "data": {"video_id": "vid_abc", "reason": "creator_request"}}
```
**Consumers**: Storage Cleanup, CDN Purge, Search Index, Recommendation Model

---

## Playback Events

### `playback.started`
```json
{"event_type": "playback.started", "data": {"video_id": "vid_abc", "user_id": "usr_xyz", "session_id": "sess_123", "device": "mobile_ios", "quality": "720p", "ttfb_ms": 1200}}
```
**Consumers**: Analytics, Watch History, Recommendation Feedback

### `playback.heartbeat`
```json
{"event_type": "playback.heartbeat", "data": {"video_id": "vid_abc", "user_id": "usr_xyz", "session_id": "sess_123", "position_sec": 180, "quality": "1080p", "buffer_sec": 12, "rebuffer_count": 0}}
```
**Consumers**: Watch History (resume position), QoE Analytics, ABR Tuning

### `playback.completed`
```json
{"event_type": "playback.completed", "data": {"video_id": "vid_abc", "user_id": "usr_xyz", "watch_duration_sec": 580, "video_duration_sec": 600, "completion_pct": 96.7, "avg_quality": "1080p", "total_rebuffers": 1}}
```
**Consumers**: Watch History, Recommendation Engine (strong signal), Analytics, Creator Analytics

### `playback.quality.changed`
```json
{"event_type": "playback.quality.changed", "data": {"video_id": "vid_abc", "session_id": "sess_123", "from": "1080p", "to": "720p", "reason": "bandwidth_drop", "buffer_sec": 3}}
```
**Consumers**: QoE Analytics, ABR Algorithm Tuning

### `playback.rebuffer`
```json
{"event_type": "playback.rebuffer", "data": {"video_id": "vid_abc", "session_id": "sess_123", "duration_ms": 2300, "position_sec": 45, "quality_at_rebuffer": "1080p", "cdn_pop": "iad-edge-01"}}
```
**Consumers**: QoE Analytics, CDN Performance Monitoring (identify underperforming PoPs)

---

## Live Streaming Events

### `live.stream.started`
```json
{"event_type": "live.stream.started", "data": {"stream_id": "live_abc", "creator_id": "usr_xyz", "title": "Friday Q&A", "ingest_server": "ingest-us-east-01"}}
```
**Consumers**: Subscriber Notification, CDN Pre-warm, Discovery (live tab)

### `live.stream.ended`
```json
{"event_type": "live.stream.ended", "data": {"stream_id": "live_abc", "duration_sec": 7200, "peak_viewers": 125000, "total_chat_messages": 450000}}
```
**Consumers**: VOD Archiver (convert to on-demand), Analytics, Creator Dashboard

### `live.chat.message`
```json
{"event_type": "live.chat.message", "data": {"stream_id": "live_abc", "message_id": "msg_123", "user_id": "usr_viewer", "content": "Amazing stream!", "is_superchat": false}}
```
**Consumers**: Chat Broadcast, Real-time Moderation, Analytics

### `live.viewer.joined`
```json
{"event_type": "live.viewer.joined", "data": {"stream_id": "live_abc", "user_id": "usr_viewer", "cdn_pop": "lax-edge-03"}}
```
**Consumers**: Viewer Count Aggregator, Analytics

---

## Search & Discovery Events

### `search.query`
```json
{"event_type": "search.query", "data": {"user_id": "usr_xyz", "query": "how to cook pasta", "results_count": 250, "latency_ms": 120}}
```
**Consumers**: Query Suggestion Builder, Analytics, Trending Topics

### `recommendation.impression`
```json
{"event_type": "recommendation.impression", "data": {"user_id": "usr_xyz", "surface": "homepage", "videos_shown": ["vid_001", "vid_002", "vid_003"], "algorithm": "deep_ranking_v3"}}
```
**Consumers**: CTR Analytics, Model Evaluation

### `recommendation.click`
```json
{"event_type": "recommendation.click", "data": {"user_id": "usr_xyz", "video_id": "vid_002", "surface": "homepage", "position": 2, "algorithm": "deep_ranking_v3"}}
```
**Consumers**: Feature Store (user profile update), Model Feedback Loop

---

## Consumer Groups

| Topic | Consumer Group | Parallelism | Guarantee |
|-------|---------------|-------------|-----------|
| `video.*` | `transcoding-scheduler` | 6 | At-least-once |
| `video.ready` | `search-indexer` | 12 | At-least-once |
| `video.ready` | `recommendation-engine` | 6 | At-least-once |
| `playback.*` | `watch-history-writer` | 24 | At-least-once |
| `playback.*` | `qoe-analytics` | 12 | At-least-once |
| `playback.completed` | `recommendation-feedback` | 12 | At-least-once |
| `live.*` | `notification-service` | 6 | At-least-once |
| `live.chat.*` | `chat-broadcast` | 24 | At-least-once |
| `live.chat.*` | `moderation-pipeline` | 12 | At-least-once |
| `search.*` | `analytics-pipeline` | 6 | At-least-once |
