# Layer 3: Voice DNA Writer

Generates drafts in your voice using Claude API. Two mechanisms prevent AI-sounding output: format selection (chooses from 6 structures based on topic + your performance history) and voice guardian (auto-rewrites if corporate language or hashtags slip through).

## Post Formats

```python
FORMATS = {
    "short_take":        "Hot take, under 5 lines. Punchy, opinionated.",
    "tactical_playbook": "Numbered how-to. Step-by-step, actionable.",
    "qt_contrast":       "Quote tweet contrast — present opposing view, then your take.",
    "contrarian":        "Goes against consensus. Starts with what everyone believes, then flips it.",
    "resource_drop":     "Curated list with context. Why each item matters.",
    "proof_post":        "Outcome first, method second. Lead with the result.",
}
```

Format is selected based on topic sentiment + which formats perform best on your account (from profile DNA).

## Implementation

```python
# ai/content_writer.py
import os
import json
import anthropic
from ai.profile_analyzer import load_dna

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

FORMATS = {
    "short_take":        "Hot take under 5 lines. Punchy, opinionated, no fluff.",
    "tactical_playbook": "Numbered steps. Practical how-to, each step one line.",
    "qt_contrast":       "Present what others think, then your contrasting take.",
    "contrarian":        "Open with common belief, then flip it with evidence/logic.",
    "resource_drop":     "Curated list: each item + one line why it matters.",
    "proof_post":        "Lead with result/outcome. Then explain how.",
}

CORPORATE_WORDS = [
    "leverage", "synergy", "utilize", "facilitate", "robust",
    "paradigm", "ecosystem", "streamline", "holistic", "scalable",
    "empower", "cutting-edge", "best-in-class", "game-changer",
]


def select_format(topic: dict, profile_dna: dict) -> str:
    sentiment = _quick_sentiment(topic["title"])
    best = profile_dna.get("top_performing_formats", ["short_take"])

    if sentiment == "controversial":
        return "contrarian"
    elif any(word in topic["title"].lower() for word in ["how to", "guide", "steps", "tutorial"]):
        return "tactical_playbook"
    elif any(word in topic["title"].lower() for word in ["top", "best", "list", "resources"]):
        return "resource_drop"
    else:
        return best[0] if best else "short_take"


def _quick_sentiment(title: str) -> str:
    controversial_signals = ["vs", "debate", "wrong", "overrated", "hype", "myth", "bad"]
    if any(s in title.lower() for s in controversial_signals):
        return "controversial"
    return "neutral"


def build_system_prompt(profile_dna: dict) -> str:
    voice_markers = profile_dna.get("voice_markers", [])
    hooks = profile_dna.get("best_hooks", [])
    avg_length = profile_dna.get("avg_post_length", 180)
    pillars = profile_dna.get("peak_engagement_pillars", [])

    return f"""You write social media posts for a specific person. Match their voice exactly.

Voice characteristics:
- Natural lowercase where they naturally write lowercase
- No hashtags ever
- No corporate buzzwords (leverage, synergy, utilize, etc.)
- Average post length: ~{avg_length} characters
- Content pillars they cover: {', '.join(pillars) if pillars else 'tech, software, AI'}
- Voice markers from their writing: {', '.join(voice_markers[:5]) if voice_markers else 'direct, opinionated, practical'}
- High-performing hooks they use: {', '.join(hooks[:3]) if hooks else 'numbered lists, questions, bold claims'}

Write as if you ARE this person. Do not sound like a content creator or marketer.
Do not add any labels, headers, or "Twitter:" / "LinkedIn:" prefixes in the drafts themselves."""


def write_draft(topic: dict, format_name: str, profile_dna: dict,
                platform: str = "twitter") -> str:
    format_desc = FORMATS.get(format_name, FORMATS["short_take"])
    char_limit = 280 if platform == "twitter" else 1300

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system=build_system_prompt(profile_dna),
        messages=[{
            "role": "user",
            "content": (
                f"Write a {platform} post about this topic using the '{format_name}' format.\n\n"
                f"Format description: {format_desc}\n\n"
                f"Topic: {topic['title']}\n"
                f"Source: {topic.get('source', '')}\n\n"
                f"Keep it under {char_limit} characters. No hashtags. Sound human."
            )
        }]
    )
    return response.content[0].text.strip()


def voice_check(draft: str, profile_dna: dict) -> tuple[bool, list[str]]:
    issues = []
    max_uppercase = profile_dna.get("max_uppercase_ratio", 0.08)

    uppercase_ratio = sum(1 for c in draft if c.isupper()) / max(len(draft), 1)
    if uppercase_ratio > max_uppercase:
        issues.append(f"Too many capitals ({uppercase_ratio:.0%}). Write in your natural case pattern.")

    if "#" in draft:
        issues.append("Remove hashtags — not part of your voice.")

    found_corp = [w for w in CORPORATE_WORDS if w.lower() in draft.lower()]
    if found_corp:
        issues.append(f"Corporate language detected: {found_corp}. Rewrite naturally.")

    ai_tells = ["I'd be happy to", "certainly", "absolutely", "of course",
                "it's worth noting", "in conclusion", "to summarize"]
    found_tells = [t for t in ai_tells if t.lower() in draft.lower()]
    if found_tells:
        issues.append(f"AI-tell phrases: {found_tells}. Remove them.")

    return len(issues) == 0, issues


def rewrite_draft(draft: str, issues: list[str], profile_dna: dict,
                  platform: str = "twitter") -> str:
    issues_str = "\n".join(f"- {i}" for i in issues)
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system=build_system_prompt(profile_dna),
        messages=[{
            "role": "user",
            "content": (
                f"Rewrite this {platform} post to fix these issues:\n{issues_str}\n\n"
                f"Original draft:\n{draft}\n\n"
                "Keep the same topic and format. No hashtags. Sound human."
            )
        }]
    )
    return response.content[0].text.strip()


def generate_post(topic: dict, profile_dna: dict,
                  platform: str = "twitter", max_rewrites: int = 3) -> str:
    """Generate a post that passes voice check. Rewrites up to max_rewrites times."""
    format_name = select_format(topic, profile_dna)
    draft = write_draft(topic, format_name, profile_dna, platform)

    for _ in range(max_rewrites):
        passed, issues = voice_check(draft, profile_dna)
        if passed:
            return draft
        draft = rewrite_draft(draft, issues, profile_dna, platform)

    return draft  # return best attempt even if not perfect


def generate_both_platforms(topic: dict, profile_dna: dict) -> tuple[str, str]:
    """Generate Twitter and LinkedIn versions in one call."""
    twitter_draft = generate_post(topic, profile_dna, "twitter")
    linkedin_draft = generate_post(topic, profile_dna, "linkedin")
    return twitter_draft, linkedin_draft
```

## Integrating into the Pipeline

```python
# In your main pipeline after scoring:
from ai.ranker import get_top_n
from ai.content_writer import generate_both_platforms
from ai.profile_analyzer import load_dna
import sqlite3

def write_drafts_for_top_topics():
    dna = load_dna()
    conn = sqlite3.connect("data/content_engine.db")
    topics = get_top_n(10)
    for topic in topics:
        twitter, linkedin = generate_both_platforms(topic, dna)
        conn.execute("""
            UPDATE topics SET draft=?, linkedin_draft=?
            WHERE id=?
        """, (twitter, linkedin, topic["id"]))
    conn.commit()
    conn.close()
```

## Gotchas

- **Voice guardian can loop.** Set `max_rewrites=3` as a hard cap — sometimes a topic just doesn't fit your voice cleanly. Surface the best attempt anyway.
- **claude-opus-4-6 is slower and costs more.** For high-volume draft generation, use `claude-haiku-4-5-20251001` for first drafts, `claude-opus-4-6` only for rewrites that fail voice check.
- **LinkedIn posts need ~5x the length of Twitter.** The `char_limit` parameter handles this — pass `"linkedin"` for platform.
- **Profile DNA must exist before calling `generate_post`.** If `profile_dna` is empty `{}`, the system prompt is generic and output quality drops significantly.
