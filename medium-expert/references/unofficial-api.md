# Medium Unofficial API (mediumapi.com)

## Overview

Third-party API actively maintained at `mediumapi.com`. Available via RapidAPI.

- **Base URL:** `https://medium2.p.rapidapi.com`
- **Auth:** `x-rapidapi-key: YOUR_KEY` header on every request
- **41 endpoints** — all GET (read-only; cannot publish or write)
- **ID-based:** most endpoints return IDs, not full objects; chain calls to get details
- **Use for:** research, content analysis, audience discovery, tag research, scraping article data

**Not a replacement for the official API** — cannot create posts.

---

## User Endpoints

| Endpoint | Returns |
|---|---|
| `GET /user/id_for/{username}` | `user_id` from username |
| `GET /user/{user_id}` | Name, bio, tier, follower count, verification status |
| `GET /user/{user_id}/articles` | Up to 250 article IDs (use `next` param to paginate) |
| `GET /user/{user_id}/top_articles` | Top 10 article IDs |
| `GET /user/{user_id}/following` | Up to 500 user IDs per request (`next` for pagination) |
| `GET /user/{user_id}/followers` | User IDs of followers (`count` ≤25, `after` for pagination) |
| `GET /user/{user_id}/publication_following` | Publication IDs the user follows |
| `GET /user/{user_id}/publications` | Publication IDs where user is admin or contributor |
| `GET /user/{user_id}/interests` | Tags the user follows |
| `GET /user/{user_id}/lists` | Public list IDs created by user |
| `GET /user/{user_id}/books` | Published books (title, description, co-authors, cover) |

---

## Article Endpoints

| Endpoint | Returns |
|---|---|
| `GET /article/{article_id}` | Title, subtitle, author, claps, tags, publication, word count, reading time |
| `GET /article/{article_id}/content` | Plain text of article (no image captions/embeds) |
| `GET /article/{article_id}/markdown` | Article as `.md` |
| `GET /article/{article_id}/html` | HTML (`fullpage` bool, optional `style_file` for custom CSS) |
| `GET /article/{article_id}/assets` | All media: images, YouTube links, Gists, hyperlinks |
| `GET /article/{article_id}/responses` | Comment/response IDs (treatable as article IDs) |
| `GET /article/{article_id}/fans` | User IDs of people who clapped |
| `GET /article/{article_id}/related` | 4 related article IDs |
| `GET /article/{article_id}/recommended` | 10 Medium-recommended article IDs |

**Note:** `article_id` is the hash at the end of a Medium URL (e.g., `abc1234567de` from `medium.com/story/title-abc1234567de`).

---

## Publication Endpoints

| Endpoint | Returns |
|---|---|
| `GET /publication/id_for/{slug}` | `publication_id` from slug or custom domain |
| `GET /publication/{publication_id}` | Name, tagline, followers, creators, social handles, logo |
| `GET /publication/{publication_id}/articles` | 25 most recent article IDs (`from` date param optional) |
| `GET /publication/{publication_id}/newsletter` | Newsletter name, description, creator, subscriber count, image |

---

## Tag / Discovery Endpoints

| Endpoint | Returns |
|---|---|
| `GET /tag/{tag}` | Follower count, story count, writer count, child tags |
| `GET /related_tags/{tag}` | Related tag strings |
| `GET /root_tags` | All top-level Medium categories |
| `GET /recommended_users/{tag}` | Up to 250 user IDs recommended for a tag |
| `GET /latestposts/{topic_slug}` | 25 newest article IDs in a topic |
| `GET /top_writers/{topic_slug}` | Top author user IDs in a niche (`count` up to 250) |
| `GET /topfeeds/{tag}/{mode}` | 25 article IDs by mode: `hot`, `new`, `top_year`, `top_month`, `top_week`, `top_all_time` |
| `GET /recommended_feed/{tag}` | Up to 25 recommended article IDs per page (pages 1–20) |
| `GET /archived_articles/{tag}` | Up to 20 historical article IDs by tag, year, month |

---

## Search Endpoints

| Endpoint | Returns |
|---|---|
| `GET /search/articles?query={q}` | Up to 1,000 matching article IDs |
| `GET /search/publications?query={q}` | Up to 1,000 publication IDs |
| `GET /search/users?query={q}` | Up to 1,000 user IDs |
| `GET /search/lists?query={q}` | Up to 1,000 list IDs |
| `GET /search/tags?query={q}` | Up to 1,000 matching tags |

---

## List Endpoints

| Endpoint | Returns |
|---|---|
| `GET /list/{list_id}` | Name, author, description, creation date, article count, claps |
| `GET /list/{list_id}/articles` | Article IDs in the list |
| `GET /list/{list_id}/responses` | Response IDs on the list |

---

## Common Patterns

**Lookup a writer's top articles:**
```
GET /user/id_for/username          → user_id
GET /user/{user_id}/top_articles   → [article_ids]
GET /article/{article_id}          → metadata for each
```

**Research a tag:**
```
GET /tag/machine-learning           → follower count, story count
GET /topfeeds/machine-learning/hot  → trending article IDs
GET /top_writers/machine-learning   → top writer user IDs
```

**Analyze a publication:**
```
GET /publication/id_for/towards-data-science   → publication_id
GET /publication/{id}                          → follower count, info
GET /publication/{id}/articles                 → recent article IDs
```

**Full-text article for analysis:**
```
GET /article/{article_id}/markdown   → full article in markdown
GET /article/{article_id}/content    → plain text
```
