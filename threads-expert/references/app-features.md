# Threads App Features

## Post Types

### Text Posts
- Up to **500 characters** per post (emojis, URLs, and punctuation all count toward the limit)
- **URLs do NOT consume character quota** — a significant advantage over X/Twitter
- Line breaks, whitespace, and emojis supported and encouraged for readability

### Text Attachments (added October 2025)
- Expandable "Read more" section appended to any post
- Up to **10,000 characters** (~1,500–2,000 words)
- Supports formatting: bold, italic, underline, strikethrough, inline links
- Cannot be edited after posting

### Image Posts
- Up to **10 images** per post (app interface)
- Supported formats: JPEG, PNG, WebP, GIF (static)
- Max file size: **8 MB per image**
- Recommended size: 1080 × 1350 px (4:5 portrait); 1:1 square also common
- In a multi-image post all photos are cropped to match the first image's aspect ratio

### Video Posts
- Max duration: **5 minutes**
- Max file size: ~500 MB in-app (up to 1 GB via API)
- Supported formats: MP4 (H.264 or HEVC codec), MOV
- Recommended aspect ratios: 9:16 (portrait), 1:1, or 4:5
- Recommended: hook viewers in the first 3 seconds; add subtitles for accessibility

### Carousels
- Mix images and videos in one post
- Up to **20 items** per carousel (API; app may show fewer slots in UI)
- All items should share a consistent aspect ratio

### Polls
- Up to **4 options**
- Poll duration can be set by creator
- Results visible after voting or when poll closes

### GIFs
- Via GIPHY integration (in-app GIF picker)
- Tenor API support ended March 31, 2026; GIPHY is the sole GIF source as of February 2026
- GIF attachments added to posts in October 2025

### Voice Notes
- Short audio recordings; popular for story-sharing and Q&A responses

### Ghost Posts (December 2025)
- Posts that auto-archive after **24 hours**
- No separate Stories format — ghost posts serve as ephemeral content on Threads

### Spoiler Tags (June 2025)
- Hide post content behind a spoiler warning tap
- Expanded to images and videos in July 2025

### Reposts, Quotes, and Replies
- **Repost**: share another user's post to your own followers with no added text
- **Quote**: repost with your own commentary added (shows original post inline)
- **Reply**: threaded conversation beneath a post; replies do not count against the 250 API posts/day limit
- **Like**: heart-tap engagement; visible in notifications

---

## Feeds

### For You (Default Feed)
- Algorithmic recommendations, similar in concept to TikTok's FYP
- Surfaces content from accounts you don't follow based on interest signals
- Ranking factors: your activity patterns (likes, replies, reposts), creator connection (whether you follow them on Threads or Instagram), post recency, engagement velocity
- Meta has been rebalancing (2025–2026) to increase weight given to accounts you actually follow

### Following Feed
- Shows only posts from accounts you explicitly follow on Threads
- Roughly chronological; some algorithmic reordering may occur

---

## Discovery: Search, Topics, and Trending

### Search
- Keyword search for public posts and accounts
- **Topic tag search**: search by topic name surfaces all posts tagged with that topic
- **"From: username" syntax** (September 2025): filter results to posts from a specific account
- **Date range filters** for narrowing results to a time window
- Fediverse user search: enter a federated handle (e.g., `@user@mastodon.social`) to find and follow from Threads

### Topic Tags (Not Hashtags)
- Threads uses **topic tags** as the primary content categorization mechanism
- A topic tag is a single word or phrase added to a post to signal its subject
- They surface posts in interest-based feeds and search
- Traditional hashtags (with `#`) are supported but not actively promoted by the algorithm
- Emoji hashtags are supported
- Posts with a topic tag consistently get more views than posts without
- October 2025: hashtags are hidden at the end of posts in the UI (moved out of inline view)

### Trending Now
- Shows hot topics in the US (with plans to expand to other countries)
- Updated in real time based on sudden spikes in post volume around a topic
- AI-generated summaries of trending topics added in 2025

### Profile Interest Tags (March 2025)
- Users add interest tags to their profile
- Threads automatically creates a custom feed from every tag on your profile
- Helps surface relevant content and follow suggestions

---

## Profiles

- **Display name**: up to 30 characters
- **Username**: up to 30 characters
- **Bio**: up to 150 characters
- **Links**: up to 5 links in bio (added May 2025)
- **Interest tags** on profile for discovery
- **Pinned posts**: pin one or more posts to the top of your profile
- **Active status indicator**: shows when you were recently active (can be disabled)
- **Post count indicator**: "1/3"-style labels on multi-part threads (September 2025)

---

## Direct Messages (DMs)

- Launched platform-wide: **July 2025**
- One-on-one private conversations between mutual connections
- **Group chats** up to 50 users (November 2025)
- Photo sharing in DMs (July 2025)
- GIF and sticker support in DMs (testing as of late 2025)
- Message requests system (users can control who can contact them)
- DMs are NOT accessible via the Threads API — no programmatic DM sending or reading

---

## Notifications

- Notified when someone: replies to your post, reposts, quotes, likes, or mentions you (`@handle`)
- **Reply control settings** per post: everyone (default), followers only, or mentioned accounts only
- **Hide replies from activity tab** (eye icon, October 2025) — manage noise from unwanted replies
- Post notification controls (customizable per account)

---

## Cross-Posting to Instagram

- **Share to Instagram Story**: share any public Threads post directly to your Instagram Story without leaving the app (simplified in February 2026)
- The Threads post is automatically formatted into a full-screen Stories frame
- Cross-posting from Instagram to Threads is also supported
- Native posts on Threads outperform cross-posted content in the algorithm

---

## Lists
- Threads does **not have a native Lists feature** similar to X/Twitter lists
- The closest equivalent is the profile-based interest tag feeds and topic tag feeds
- Communities feature (launched 2025 in US + South Korea) provides topic-based group spaces

---

## Threads Web App (threads.net)
- Full-featured web interface at **threads.net**
- Supports posting, reading, replying, search, and profile management
- Desktop: rearrangeable column layout (pinned columns feature, 2024)
- Side-swipe engagement UI (swipe right to like) available on mobile
- Analytics (Insights) accessible on desktop

---

## ActivityPub / Fediverse Integration

### What It Is
- ActivityPub is a W3C open standard for decentralized social networking
- It allows communication between independent servers (Mastodon, BookWyrm, WriteFreely, WordPress, etc.)
- Threads is the largest app running on ActivityPub — 400M+ users

### What It Means for Users
- **Opt-in sharing**: Threads users can opt in to have their posts shared to the fediverse
- Users who opt in get a fediverse address (e.g., `@username@threads.net`) visible to Mastodon users
- **Fediverse feed inside Threads** (June 2025): a dedicated feed showing posts from Mastodon, BookWyrm, WriteFreely, and other federated platforms
- **Search fediverse users** in Threads directly — find and interact with their posts without leaving Threads
- **Content moderation caveat**: content in the fediverse feed is not algorithmically ranked and is not subject to Threads' own content moderation rules

### Current Limitations
- Replies from Threads users to fediverse posts are not yet supported in all contexts
- The fediverse feed requires opt-in to fediverse sharing on Threads
- Not all federated platforms are supported; more are being added over time

---

## Notable 2025–2026 Feature Timeline

| Date | Feature |
|---|---|
| Jan 2025 | Mobile analytics (Insights) for all users; ad testing (US + Japan) |
| Mar 2025 | Interest tags on profiles; Trending Now improvements |
| May 2025 | Cross-posting to Instagram Stories; account creation without Instagram; up to 5 bio links |
| Jun 2025 | Spoiler alerts feature; DM testing begins; fediverse feed and user search launched |
| Jul 2025 | DMs rolled out platform-wide; spoiler tags for images/videos; photo sharing in DMs |
| Aug 2025 | 400 million monthly active users milestone |
| Sep 2025 | Auto post count indicators; Communities testing; "From: username" search |
| Oct 2025 | Hashtags hidden at end of posts; eye icon to hide replies; ghost posts in development; group chats launched |
| Nov 2025 | Group chats up to 50 users; time management settings (daily limits, sleep mode); podcast integration testing |
| Dec 2025 | Ghost posts enabled; Dear Algo feed personalization testing; AI interaction summaries on profiles |
| Jan 2026 | Global ads rollout to all users |
| Feb 2026 | Dear Algo feed personalization; simplified Instagram sharing; GIPHY GIF support added |
| Mar 2026 | Web Intents expanded (reply/quote parameters); oEmbed without access tokens |
