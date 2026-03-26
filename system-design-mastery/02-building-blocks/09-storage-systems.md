# 9. Storage Systems

## Part Context
**Part:** Part 2 - Core System Building Blocks  
**Position:** Chapter 9 of 60
**Why this part exists:** This section moves from framing to mechanics by explaining the infrastructure components that repeatedly appear in real-world systems.  
**This chapter builds toward:** choosing the right storage medium for media, persistence, content delivery, and long-term cost control

## Overview
Storage is not one thing. Databases, filesystems, block volumes, object stores, archival tiers, and CDNs all exist because different kinds of data want different handling. System designers need to match storage technology to access pattern, durability requirement, cost sensitivity, and operational model.

This chapter focuses on the storage systems that commonly appear around applications: file, block, and object storage, along with blob serving and CDN delivery. These choices become especially important in media-heavy and globally distributed products.

## Why This Matters in Real Systems
- Using the wrong storage model can create permanent performance and cost penalties.
- Media-heavy products live or die by storage and delivery design, not only by API code.
- Durability, egress cost, and lifecycle management are all architecture concerns.
- Storage choices often determine how the rest of the system must be modeled.

## Core Concepts
### Block, file, and object storage
These three models expose different abstractions and fit different workloads.

### Blob storage and media handling
Large unstructured files such as images, videos, logs, and backups usually belong in object storage rather than relational tables.

### Durability, replication, and lifecycle
Storage systems differ in how they replicate data, recover from failure, and manage old or cold data.

### CDN integration
A CDN extends storage to the edge, improving performance and reducing origin traffic for globally consumed content.

## Key Terminology
| Term | Definition |
| --- | --- |
| Block Storage | Low-level attachable storage volumes optimized for filesystems and database engines. |
| File Storage | Shared hierarchical storage exposed through filesystem semantics. |
| Object Storage | A storage model for blobs addressed as objects with metadata. |
| Blob | A large binary object such as an image, video, or document. |
| Origin | The source system from which a CDN fetches content when it is not cached at the edge. |
| Egress | Data transferred out of the source environment, often a major cost driver. |
| Lifecycle Policy | Rules for moving, archiving, or deleting data over time. |
| Durability | The probability that stored data remains preserved over time and across failures. |

## Detailed Explanation
### Choose storage by access pattern
Databases often need block-level performance because they manage their own pages and transactions. Shared developer assets may want a filesystem interface. Media uploads, logs, backups, and downloadable artifacts often fit object storage because they are large, append-light, and consumed over HTTP or CDN paths.

### Object storage changes application architecture
Once blobs live in object storage, the application usually stores metadata and references separately in its transactional store. This is a healthy pattern because the binary payload and the control-plane metadata have different performance and scaling needs.

### Durability is not just a number on a brochure
Highly durable storage usually relies on replication, checksums, and background repair. Architects still need to think about accidental deletion, regional requirements, backup policy, and recovery objectives. Durable storage does not eliminate the need for data management.

### CDNs shift the economics of content delivery
Without a CDN, origin systems pay the latency and bandwidth cost for every viewer. With a CDN, frequently accessed content is served from the edge. This changes not only performance but also how origins are scaled, how cache headers are designed, and how egress cost behaves.

### Storage lifecycle drives long-term cost
The total storage bill is not only about the cost per GB today. Retention period, backup policy, access frequency, cross-region replication, and retrieval behavior all shape long-term economics. Architects should think in lifecycles, not snapshots.

## Diagram / Flow Representation
### Storage Selection View
```mermaid
flowchart TD
    Data[Data type] --> Kind{Access pattern?}
    Kind -->|Low-level random I/O| Block[Block Storage]
    Kind -->|Shared filesystem semantics| File[File Storage]
    Kind -->|Large blobs / HTTP delivery| Object[Object Storage]
    Object --> CDN[CDN / Edge Delivery]
```

### Media Serving Path
```mermaid
sequenceDiagram
    participant U as User
    participant App as App Service
    participant Meta as Metadata DB
    participant Obj as Object Store
    participant CDN as CDN
    U->>App: Request media page
    App->>Meta: Read metadata
    Meta-->>App: Object reference
    App-->>U: Signed URL / asset URL
    U->>CDN: Fetch media
    CDN->>Obj: Cache miss fetch
    Obj-->>CDN: Object bytes
    CDN-->>U: Stream asset
```

## Real-World Examples
- YouTube stores raw uploads and transcoded renditions as objects, not inside its transactional metadata database.
- Amazon product images are served from storage systems optimized for object delivery and fronted by edge caches.
- Netflix content delivery depends on edge distribution because origin-only delivery would be too slow and expensive.
- Google Drive separates document metadata and collaboration state from the large file objects themselves.

## Case Study
### YouTube-style video storage

A video platform is an excellent storage case because it combines huge binary objects, metadata, transcoding pipelines, and global playback traffic.

### Requirements
- Accept large user uploads reliably and durably.
- Store original and processed video assets efficiently.
- Serve playback data globally with low latency.
- Keep metadata such as ownership, title, visibility, and processing state strongly manageable.
- Control long-term storage and delivery cost as the catalog grows.

### Design Evolution
- A simple version may store uploads durably and keep metadata in a relational store.
- As transcoding is added, the system creates multiple output renditions and stores them separately from the source upload.
- As global playback grows, CDN distribution becomes essential to reduce latency and origin load.
- As the library ages, lifecycle policies can move older or less frequently accessed assets into colder tiers if product behavior allows.

### Scaling Challenges
- Large binary data overwhelms transactional databases if stored in the wrong place.
- CDN miss traffic can still overload origins if cache behavior is poorly designed.
- Replication and backup multiply effective storage size beyond the raw uploaded bytes.
- Egress cost can become as important as raw storage cost for popular media systems.

### Final Architecture
- Object storage for uploaded and processed media assets.
- A metadata database for ownership, titles, visibility, and processing state.
- CDN delivery for media segments, thumbnails, and static assets.
- Lifecycle and archival policies tied to access patterns and business retention rules.
- Observability for origin load, CDN hit rate, storage growth, and retrieval latency.

## Architect's Mindset
- Choose storage media based on access semantics, not habit.
- Separate metadata from large binary objects early in the design.
- Treat egress and lifecycle policy as first-class cost concerns.
- Remember that durability still requires deletion controls, backup thinking, and recovery planning.
- Use CDN strategy as part of storage architecture, not as an afterthought.

## Common Mistakes
- Storing large media blobs in the primary relational database without a strong reason.
- Ignoring egress cost when planning content-heavy systems.
- Treating storage as only capacity and forgetting access pattern and lifecycle.
- Assuming highly durable storage removes the need for backup or recovery planning.
- Using the same storage class for hot data and archival data.

## Interview Angle
- Storage questions usually appear in media systems, backup systems, file systems, and large content products.
- Strong answers explain why metadata and blobs belong in different layers and how CDNs reduce origin pressure.
- Candidates stand out when they discuss storage lifecycle, durability, and cost rather than only raw capacity.
- A weak answer uses “S3” or another product name without explaining the access pattern it fits.

## Quick Recap
- Storage systems exist in different forms because workloads differ.
- Block, file, and object storage should be selected according to access pattern and semantics.
- Large blobs generally belong in object storage, with metadata stored separately.
- CDNs improve global delivery performance and reduce origin load.
- Lifecycle and egress costs are part of architecture, not accounting afterthoughts.

## Practice Questions
1. Why is object storage usually a better fit for images and videos than a relational database?
2. When would block storage be the better choice?
3. How does separating metadata from blobs simplify architecture?
4. Why does CDN design belong in a storage discussion?
5. What is the effect of lifecycle policies on long-term cost?
6. How would you design storage for a document-sharing platform?
7. What kinds of mistakes drive egress cost unexpectedly high?
8. How would you explain durability versus backup to a teammate?
9. What would you monitor in a content-serving storage system?
10. How does origin protection relate to storage design?

## Further Exploration
- Carry these ideas into the YouTube and Instagram system design chapters later in the book.
- Study storage classes, archival tiers, and signed URL patterns in more depth.
- Practice mapping storage types to three products: backup service, photo app, and shared filesystem.





## Navigation
- Previous: [Message Queues & Event Systems](08-message-queues-event-systems.md)
- Next: [Scalability](../03-distributed-systems/10-scalability.md)
