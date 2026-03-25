# Social Media & Content Platforms — Event Catalog

## Event Bus: Apache Kafka

---

## Post Events

### `post.created`
```json
{"event_type": "post.created", "data": {"post_id": "post_abc", "user_id": "usr_xyz", "post_type": "post", "has_media": true, "privacy": "public", "hashtags": ["tech", "startup"]}}
```
**Consumers**: Fanout Workers, Search Indexer, Moderation, Analytics, Hashtag Trending

### `post.media.ready`
```json
{"event_type": "post.media.ready", "data": {"post_id": "post_abc", "media_id": "med_123", "variants": {"thumbnail": "url", "small": "url", "medium": "url", "large": "url"}}}
```
**Consumers**: Post Service (update URLs), CDN Warmer

### `post.deleted`
```json
{"event_type": "post.deleted", "data": {"post_id": "post_abc", "user_id": "usr_xyz", "reason": "user_request"}}
```
**Consumers**: Feed Cache (remove from all feeds), Search Index, Analytics

---

## Social Graph Events

### `social.follow`
```json
{"event_type": "social.follow", "data": {"follower_id": "usr_abc", "followee_id": "usr_xyz"}}
```
**Consumers**: Feed Rebuild (add followee's recent posts to follower's feed), Notification, Analytics, "People You May Know"

### `social.unfollow`
```json
{"event_type": "social.unfollow", "data": {"follower_id": "usr_abc", "followee_id": "usr_xyz"}}
```
**Consumers**: Feed Cache (optional cleanup), Analytics

---

## Engagement Events

### `engagement.like`
```json
{"event_type": "engagement.like", "data": {"post_id": "post_abc", "user_id": "usr_xyz", "post_owner_id": "usr_owner"}}
```
**Consumers**: Activity Stream, Notification, Analytics, Counter DB Sync

### `engagement.comment`
```json
{"event_type": "engagement.comment", "data": {"comment_id": "cmt_123", "post_id": "post_abc", "user_id": "usr_xyz", "content_preview": "Great post!", "post_owner_id": "usr_owner"}}
```
**Consumers**: Activity Stream, Notification, Moderation, Analytics

### `engagement.share`
```json
{"event_type": "engagement.share", "data": {"post_id": "post_abc", "user_id": "usr_xyz", "share_type": "repost"}}
```
**Consumers**: Fanout (shared post appears in sharer's followers' feeds), Notification, Analytics

---

## Content Events

### `story.created`
```json
{"event_type": "story.created", "data": {"story_id": "story_abc", "user_id": "usr_xyz", "expires_at": "2026-03-23T10:00:00Z"}}
```
**Consumers**: Story Tray Cache, Notification (close friends), Analytics

### `story.expired`
```json
{"event_type": "story.expired", "data": {"story_id": "story_abc", "user_id": "usr_xyz"}}
```
**Consumers**: Storage Cleanup, Story Tray Cache

### `live.started`
```json
{"event_type": "live.started", "data": {"stream_id": "live_abc", "user_id": "usr_xyz", "title": "Q&A Session"}}
```
**Consumers**: Notification (followers), Feed Injection, Analytics

### `live.ended`
```json
{"event_type": "live.ended", "data": {"stream_id": "live_abc", "duration_sec": 3600, "peak_viewers": 45000}}
```
**Consumers**: VOD Processing (save replay), Analytics

---

## Messaging Events

### `message.sent`
```json
{"event_type": "message.sent", "data": {"conversation_id": "conv_abc", "message_id": "msg_123", "sender_id": "usr_xyz", "content_type": "text"}}
```
**Consumers**: Delivery Workers, Notification (if offline), Analytics

### `message.read`
```json
{"event_type": "message.read", "data": {"conversation_id": "conv_abc", "reader_id": "usr_xyz", "read_up_to": "msg_123"}}
```
**Consumers**: Read Receipt Delivery, Analytics

---

## Moderation Events

### `moderation.content.flagged`
```json
{"event_type": "moderation.content.flagged", "data": {"content_id": "post_abc", "content_type": "post", "violation_type": "hate_speech", "confidence": 0.92, "action": "remove"}}
```
**Consumers**: Post Service (remove/label), Notification (creator), Analytics, Account Risk Score

### `moderation.report.submitted`
```json
{"event_type": "moderation.report.submitted", "data": {"report_id": "rpt_abc", "reporter_id": "usr_xyz", "content_id": "post_def", "reason": "harassment"}}
```
**Consumers**: Report Queue, Auto-Triage ML, Analytics

### `abuse.network.detected`
```json
{"event_type": "abuse.network.detected", "data": {"network_id": "net_abc", "account_count": 47, "behavior": "coordinated_spam", "confidence": 0.88}}
```
**Consumers**: Account Action Service (suspend network), T&S Dashboard, Analytics

---

## Consumer Groups

| Topic | Consumer Group | Parallelism | Guarantee |
|-------|---------------|-------------|-----------|
| `post.*` | `fanout-workers` | 24 consumers | At-least-once |
| `post.*` | `search-indexer` | 12 consumers | At-least-once |
| `post.*` | `moderation-pipeline` | 12 consumers | At-least-once |
| `engagement.*` | `activity-stream` | 12 consumers | At-least-once |
| `engagement.*` | `notification-service` | 12 consumers | At-least-once |
| `social.*` | `feed-rebuild` | 6 consumers | At-least-once |
| `message.*` | `delivery-workers` | 24 consumers | At-least-once |
| `moderation.*` | `post-service` | 6 consumers | At-least-once |
| `abuse.*` | `account-action` | 3 consumers | Exactly-once |
