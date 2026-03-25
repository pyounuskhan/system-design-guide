# Video & Streaming Platforms — Glossary

## Video Encoding Terms

| Term | Definition |
|------|-----------|
| **Codec** | Compression algorithm: H.264 (AVC), H.265 (HEVC), VP9, AV1. Each generation achieves ~30-50% better compression. |
| **Container** | File format wrapping video+audio tracks: MP4, WebM, TS (Transport Stream), fMP4. |
| **Bitrate** | Amount of data per second of video. Higher bitrate = higher quality but more bandwidth. |
| **Bitrate Ladder** | The set of resolution/bitrate variants produced for a video for ABR streaming. |
| **GOP** | Group of Pictures — a sequence of frames starting with a keyframe. GOPs are independently decodable. |
| **Keyframe (I-frame)** | A full image frame; starting point for decoding. Segments must begin at keyframe boundaries. |
| **Per-Title Encoding** | Analyzing content complexity to optimize the bitrate ladder per video rather than using a fixed ladder. |
| **Per-Shot Encoding** | Netflix's approach: optimize bitrate for each scene/shot independently, then concatenate. |
| **VMAF** | Video Multi-method Assessment Fusion — Netflix's perceptual quality metric (0-100). 93+ is "good". |
| **SSIM** | Structural Similarity Index — objective quality metric comparing original and encoded frames. |
| **PSNR** | Peak Signal-to-Noise Ratio — basic quality metric; VMAF is preferred for perceptual quality. |
| **Transcoding** | Re-encoding video from one codec/resolution/bitrate to another. CPU or GPU intensive. |
| **Transmuxing** | Changing the container format without re-encoding (fast, lossless). E.g., MP4 → TS. |
| **HDR** | High Dynamic Range — wider brightness and color range. Formats: HDR10, Dolby Vision, HLG. |
| **NVENC** | NVIDIA's hardware video encoder — 5-10x faster than CPU encoding with acceptable quality. |

## Streaming Protocols

| Term | Definition |
|------|-----------|
| **HLS** | HTTP Live Streaming — Apple's ABR protocol. Uses .m3u8 manifests and .ts/.fmp4 segments. Dominant on iOS. |
| **DASH** | Dynamic Adaptive Streaming over HTTP — ISO standard. Uses .mpd manifests. Preferred on Android. |
| **CMAF** | Common Media Application Format — unified segment format compatible with both HLS and DASH manifests. |
| **LL-HLS** | Low-Latency HLS — Apple's extension for < 5s live latency using partial segments and blocking playlist reload. |
| **LL-DASH** | Low-Latency DASH — DASH variant with chunked transfer encoding for reduced latency. |
| **WebRTC** | Web Real-Time Communication — sub-second latency protocol for interactive streaming and video calls. |
| **RTMP** | Real-Time Messaging Protocol — legacy but widely used for live ingest from encoders (OBS, Streamlabs). |
| **SRT** | Secure Reliable Transport — modern live ingest protocol with error correction for unreliable networks. |
| **ABR** | Adaptive Bitrate — player dynamically selects quality level per segment based on network conditions. |
| **Manifest** | Playlist file listing available quality levels and segment URLs. .m3u8 (HLS) or .mpd (DASH). |
| **Segment** | Small chunk of video (2-10 seconds) independently requestable by the player. |
| **Partial Segment** | LL-HLS feature: player can request a segment before it's fully encoded. |

## CDN & Delivery

| Term | Definition |
|------|-----------|
| **CDN** | Content Delivery Network — globally distributed cache network for serving content from nearby servers. |
| **PoP** | Point of Presence — a CDN edge location. Major CDNs have 200-300+ PoPs worldwide. |
| **Origin** | The authoritative source server for content. CDN edges fetch from origin on cache miss. |
| **Origin Shield** | A regional cache layer between origin and edge PoPs, reducing load on origin. |
| **Cache Hit Rate** | Percentage of requests served from cache vs. fetched from origin. Target: 85-95%. |
| **TTFB** | Time to First Byte — time from request to first byte of video data. Target: < 2s. |
| **Rebuffering** | Playback stall while the player waits for more data. Primary quality-of-experience metric. |
| **Pre-warming** | Proactively pushing content to CDN edges before viewers request it. Used for new releases. |
| **Signed URL** | URL with embedded authentication token to prevent hotlinking. Expires after a set period. |
| **Multi-CDN** | Using multiple CDN providers and routing based on performance, cost, and availability. |
| **Traffic Steering** | Directing viewers to the optimal CDN PoP based on real-time performance data. |

## DRM

| Term | Definition |
|------|-----------|
| **DRM** | Digital Rights Management — technology preventing unauthorized copying/viewing of content. |
| **Widevine** | Google's DRM. L1 (hardware-secured, required for HD/4K), L3 (software-only, SD). |
| **FairPlay** | Apple's DRM for iOS, macOS, and Apple TV. Required for any DRM content on Apple devices. |
| **PlayReady** | Microsoft's DRM for Windows, Xbox, and some smart TVs. |
| **CENC** | Common Encryption — ISO standard allowing single encryption with multiple DRM license servers. |
| **License** | A DRM key delivered to the player for decrypting content. Obtained from a license server. |
| **TEE** | Trusted Execution Environment — hardware-isolated area for secure key management (e.g., ARM TrustZone). |
| **Offline License** | DRM license allowing content to be downloaded and watched without internet for a limited time. |
| **Forensic Watermark** | Invisible per-viewer watermark embedded in video to trace the source of piracy. |

## Abbreviations

| Abbreviation | Full Form |
|-------------|-----------|
| ABR | Adaptive Bitrate |
| ASR | Automatic Speech Recognition |
| AV1 | AOMedia Video 1 (next-gen open codec) |
| AVC | Advanced Video Coding (H.264) |
| DAU | Daily Active Users |
| DVR | Digital Video Recorder (live stream rewind) |
| FPS | Frames Per Second |
| HDR | High Dynamic Range |
| HEVC | High Efficiency Video Coding (H.265) |
| QoE | Quality of Experience |
| UGC | User-Generated Content |
| VOD | Video on Demand |
