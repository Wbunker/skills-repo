# YouTube Studio — Creator Workflow Reference

## Table of Contents
1. [Upload workflow](#upload-workflow)
2. [Title and description optimization](#title-and-description-optimization)
3. [Thumbnail best practices](#thumbnail-best-practices)
4. [Chapters](#chapters)
5. [End screens](#end-screens)
6. [Cards](#cards)
7. [Captions and subtitles](#captions-and-subtitles)
8. [Scheduling and visibility](#scheduling-and-visibility)
9. [Mobile vs desktop capability matrix](#mobile-vs-desktop-capability-matrix)

---

## Upload workflow

1. Go to **studio.youtube.com** → click the **Create** button (camera+) → **Upload video**
2. Drag-and-drop or browse — recommended format: MP4 (H.264 video, AAC audio); also supports MOV, AVI, WMV, FLV, MKV, WebM
3. While uploading, complete the **Details** tab:
   - Title (required)
   - Description
   - Thumbnail (upload custom or pick auto-generated frame)
   - Tags
   - Audience (Made for Kids designation — required by COPPA)
   - Age restriction (optional)
4. **Video elements** tab: add end screens, cards, captions
5. **Checks** tab: copyright and monetization policy checks run automatically
6. **Visibility** tab: set visibility + optional scheduled date/time → click **Save** or **Schedule**

Processing time varies by resolution: 1080p may take a few minutes; 4K can take 30+ minutes after upload completes.

---

## Title and description optimization

### Titles
- Recommended length: **60–70 characters** (longer titles truncate in search results)
- Front-load the primary keyword — YouTube reads left to right
- Format that works: `[Keyword]: [Compelling Benefit or Hook]`
- Use natural language humans would search; avoid keyword-stuffing
- Numbers and specificity increase CTR: "5 Ways to…" outperforms "Ways to…"

### Descriptions
- **First 1–2 lines** appear before the "Show more" fold — treat as a hook; include primary keyword
- Structure for a long description:
  ```
  [Hook sentence with primary keyword]
  [What the video covers / value prop]
  
  CHAPTERS:
  0:00 Intro
  1:30 [Section]
  ...
  
  LINKS:
  [Website, newsletter, social, etc.]
  
  ABOUT THIS CHANNEL:
  [Brief channel description + CTA to subscribe]
  
  TAGS / KEYWORDS: [secondary keywords, spelling variants]
  ```
- Descriptions are not heavily indexed for search, but keywords here support topical relevance

### Tags
- Lower algorithmic priority than title and thumbnail
- Useful for: spelling variants, acronym vs full name, related topic clusters
- Tags are not shown to viewers but are indexed
- First tag should be the exact primary keyword

---

## Thumbnail best practices

**Specifications:**
- Minimum: 1280×720 px (16:9 aspect ratio)
- Maximum file size: 2 MB
- Formats: JPG, PNG, GIF, BMP
- Custom thumbnails require verified account (phone verification)

**Design principles:**
- Bold, high-contrast imagery — thumbnails display at small sizes on mobile
- Include 3–5 word text overlay at large font size (readable at thumbnail size)
- Show a human face when possible — faces increase CTR
- Create visual contrast with YouTube's white/dark background
- Text and key visual elements should not be near edges (may be cropped on some surfaces)
- Consistent branding across channel (color palette, font, layout style)
- The thumbnail + title must work together to tell a complete story
- Avoid misleading thumbnails — they increase click-through but reduce watch time, punishing the video algorithmically

---

## Chapters

Chapters add a progress bar with named segments and allow viewers to jump to sections. They also appear as rich results in Google search.

**Requirements:**
- At least 3 timestamps
- First timestamp must be `0:00`
- Minimum 10 seconds per chapter
- Format must be exact: `0:00 Chapter Name` on its own line in the description

**Example:**
```
0:00 Intro
1:45 Setting up your account
4:20 First upload walkthrough
9:00 Optimizing your title
12:30 Thumbnail design tips
15:00 Final thoughts
```

Chapters can be disabled per-video: in Studio → Video details → scroll down → uncheck "Allow automatic chapters"

---

## End screens

End screens appear during the **last 5–20 seconds** of a video. The video must be at least **25 seconds** long.

**Maximum 4 elements per video.**

| Element type | Notes |
|-------------|-------|
| Video or Playlist | Link to another video or playlist on YouTube |
| Subscribe button | Prompts viewer to subscribe to your channel |
| Channel | Feature another YouTube channel |
| Link (external URL) | Requires YouTube Partner Program membership |

**Best practices:**
- Add end screens to every video — they extend watch time and channel engagement
- Direct viewers to watch a related or recommended next video
- Place subscribe button in a consistent screen position across all videos
- Leave 5–20 seconds of "end card" content designed to show behind end screen elements

To add: Studio → Content → select video → **Editor** tab → End screen section

---

## Cards

Cards are interactive notifications that appear at custom timestamps during a video. They pop up in the upper-right corner.

**Maximum 5 cards per video.**

| Card type | Notes |
|-----------|-------|
| Video | Link to any YouTube video |
| Playlist | Link to a playlist |
| Channel | Feature another channel |
| Link (external URL) | Requires YouTube Partner Program |

**Best practices:**
- Add a card near the point in the video most relevant to the linked content
- Verbally prompt viewers: "Check out the card in the top right corner"
- Use to redirect viewers who may be watching the wrong video for their use case

To add: Studio → Content → select video → **Editor** tab → Cards section

---

## Captions and subtitles

YouTube auto-generates captions for most videos. Accuracy varies by audio quality and accent.

**To edit auto-captions:**
Studio → Content → select video → **Subtitles** tab → select language → Edit

**To upload a caption file:**
Supported formats: `.srt`, `.vtt`, `.sbv`, `.ttml`, `.dfxp`

Studio → Content → select video → **Subtitles** tab → **Add language** → Upload file

**Why captions matter:**
- Accessibility (legal requirement in many contexts)
- Improves watch time for viewers in noisy/silent environments
- Keywords in captions are indexed by YouTube search
- Required for some monetization in certain regions

---

## Scheduling and visibility

| Setting | Behavior |
|---------|----------|
| Private | Only you (and explicitly invited users) can see it |
| Unlisted | Anyone with the link can watch; not shown in search or channel page |
| Public | Visible to everyone; appears in search and recommendations |
| Scheduled | Sets a future date/time for automatic publish to Public |

**Scheduling tips:**
- Publish when your audience is most active — check Audience tab in Analytics for "When your viewers are on YouTube"
- Scheduled uploads notify subscribers via the subscription feed at publish time
- You can schedule up to 15 unlisted premieres simultaneously

**Premier vs. regular upload:**
- Premiere creates a scheduled watch page with countdown; viewers can gather in chat before the video goes live
- Good for community-building around new releases

---

## Mobile vs desktop capability matrix

| Feature | Desktop (studio.youtube.com) | Mobile (YouTube Studio app) |
|---------|------------------------------|------------------------------|
| Video upload | Full workflow | Simplified; can record directly |
| Custom thumbnails | Full upload | Available, limited |
| End screens | Full editor | Not available |
| Cards | Full editor | Not available |
| Chapters editor | Full | Not available |
| Bulk video editing | Available | Not available |
| Monetization settings | Full control | Not available |
| Channel customization | Full (banner, layout, sections) | Not available |
| Analytics | Full (all tabs + date ranges) | Quick summary + real-time |
| Comment moderation | Full | Available — best mobile use case |
| Push notifications | Available | Best on mobile |
| Live streaming setup | Full | Supported on eligible devices |
| Caption editor | Full | Not available |
| Scheduling | Full | Not available |

**Rule of thumb:** Use mobile for comments, notifications, and quick stats checks. Use desktop for everything else.
