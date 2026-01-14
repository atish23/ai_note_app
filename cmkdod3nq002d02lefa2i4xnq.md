---
title: "Understanding Multi-Peer Video Conferencing: From P2P to SFU"
datePublished: Wed Jan 14 2026 07:03:59 GMT+0000 (Coordinated Universal Time)
cuid: cmkdod3nq002d02lefa2i4xnq
slug: understanding-multi-peer-video-conferencing-from-p2p-to-sfu
tags: webrtc, system-design, video-conferencing

---

### What is a Peer and How Do They Connect?

So when we talk about conference apps like Zoom, Google Meet, or WhatsApp group calls, we're essentially talking about multiple devices connecting to each other in real-time. Each device is called a peer. A peer is basically any participant in the call—your laptop, mobile phone, or any client that's part of the video conference.

How do peers connect? At the basic level, peers need to establish a connection to send and receive video and audio streams. In the simplest case, when there are just two peers (let's say Atish calling Rohit), they can establish a direct connection to each other. But when there are multiple peers, things get more complex. The key challenge is that each peer needs to somehow transmit its data to all other peers and receive data from all of them.

This is where the architecture matters. The way peers connect depends entirely on which architecture you choose—whether it's P2P, Mesh, MCU, or SFU.

---

### What is WebRTC and Why Use UDP Instead of TCP?

Before diving into different architectures, we need to understand WebRTC. WebRTC (Web Real-Time Communication) is a protocol and technology that enables real-time communication directly in web browsers and applications. It allows peers to establish connections and exchange audio, video, and data directly.

Now, here's the critical part: normal HTTP uses TCP (Transmission Control Protocol), but for real-time video conferencing, this becomes a problem.

Why not use TCP? TCP is designed to ensure that every packet of data reaches its destination in order and without loss. It has built-in error correction and retransmission. While this sounds good for reliability, it's terrible for real-time communication. Here's why:

Imagine you're in a video call and a few packets of video data get lost. TCP will pause the entire stream and wait for those lost packets to be resent. This causes buffering, freezing, and latency. A 200ms delay might not seem like much, but in a real-time conversation, it becomes extremely noticeable and frustrating.

So instead, we use UDP (User Datagram Protocol). UDP is connectionless and doesn't guarantee delivery or order. If a few packets get lost? UDP doesn't care—it just keeps sending. This is perfect for video because:

1. Losing a few video frames is acceptable. Your eye won't even notice if one or two frames are missing.
    
2. Speed is prioritized over perfection. A fast, slightly degraded video is better than a perfectly buffered but delayed one.
    
3. Low latency is achieved. UDP has minimal overhead, so data travels much faster.
    

WebRTC uses UDP to transmit media streams. This is the foundation that makes real-time video calls possible with acceptable latency.

---

### Architectures: P2P, Mesh, MCU, and Why SFU?

Now that we understand peers and UDP, let's talk about how multiple peers can connect using different architectures.

## 1\. Peer-to-Peer (P2P)

In P2P, two peers connect directly to each other. Atish sends his video stream directly to Rohit, and Rohit sends his stream directly to Atish. No server involvement for media, no processing overhead.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1768371636079/1dd18022-e5a9-4935-a2aa-d24dd627f308.png align="center")

Advantages:

* No server cost for media handling
    
* Direct connection means lowest possible latency
    
* Simple to implement for 1:1 calls
    

Problems:

* Doesn't scale. As soon as you add a third peer, it becomes complicated.
    
* Each peer would need to connect to every other peer individually.
    

## 2\. Mesh Network

A mesh extends P2P to multiple peers. Here, every peer connects to every other peer. With 3-4 peers, it might seem okay. But let's imagine 10-12 peers.

Peer 1 has to:

* Send its video stream to peers 2, 3, 4, 5... up to 12 (11 outgoing connections)
    
* Receive video streams from all other 11 peers (11 incoming streams to decode)
    
* Process and potentially display 11 different video feeds
    

Multiply this for all 12 peers, and you have each client uploading and downloading massive amounts of data while decoding multiple streams. The CPU and bandwidth usage explodes exponentially. It's a mess.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1768371648736/c13e139e-3b64-4810-bd0e-e18a58fc33f6.png align="center")

Advantages:

* Still no server cost for media
    

Problems:

* Bandwidth consumption is massive
    
* Doesn't scale beyond a handful of participants
    

## 3\. MCU (Multipoint Control Unit)

To solve the mesh problem, MCU was introduced. Here's how it works:

Each peer sends a single stream to a central server (MCU). The MCU then:

* Receives all streams from all peers
    
* Decodes them
    
* Mixes/composites them into one combined video layout (like a grid showing all participants)
    
* Re-encodes the mixed video
    
* Sends this single combined stream back to each peer
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1768373789523/1c4aaa62-edb0-4405-ac4c-9d75ae227472.png align="center")

Advantages:

* Each client only uploads one stream and receives one stream. Much simpler on the client side.
    
* Can handle many more participants than mesh
    

Problems:

* The server is doing heavy work: decoding multiple streams, compositing them, and re-encoding. This is CPU-intensive.
    
* High latency: All this processing takes time. You have encoding latency, processing latency, and transmission latency stacked together.
    
* Very expensive server infrastructure needed
    
* Not ideal for modern scalable applications
    

## 4\. SFU (Selective Forwarding Unit) — The Smart Choice

SFU is where we get the best of both worlds. Here's how it works:

Each peer sends its stream(s) to the SFU server. The server doesn't mix or compose anything. Instead, it:

* Inspects which streams are relevant
    
* Decides which streams should go to which peers
    
* Forwards each stream separately (without combining)
    
* Each peer receives multiple individual streams
    
* The peer's client decides what to do with these streams: which ones to display, which to hide, which quality to accept, etc.
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1768374038865/9846e327-a5ad-4de3-97a7-b0410dcc19d6.png align="center")

Advantages:

* Far less CPU overhead than MCU. The server isn't mixing; it's just routing.
    
* Better latency. No heavy composition work means faster processing.
    
* Peers control their own experience. They can choose to watch high-quality streams from speakers and lower quality from others.
    
* Bandwidth management. Peers can decide to pause certain streams or request lower resolutions.
    
* Highly scalable. One SFU server can handle many more participants than an MCU because it's doing less work.
    
* Significantly lower server costs compared to MCU
    

This is why modern platforms like Zoom, Google Meet, and others use SFU-based architectures. It's the sweet spot between server cost, scalability, and latency.

---

**Conclusion**

When you build a multi-party video conferencing application, your architecture choice directly impacts scalability, latency, and costs.

P2P works for 1:1 calls. Mesh doesn't scale. MCU is expensive and slow. SFU is the architecture driving most modern real-time platforms because it balances all these concerns. It's efficient, scalable, and cost-effective.

Understanding these differences helps you make informed decisions when designing your own real-time communication systems.