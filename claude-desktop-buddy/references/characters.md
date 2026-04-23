# Custom Character Packs

Design and push custom animated characters to any Claude Desktop Buddy device.

## Overview

A character pack is a flat folder of GIF files + a `manifest.json`. Drag the folder onto the
Hardware Buddy window in Claude Desktop, or flash over USB with `tools/flash_character.py`.

Max folder size: **1.8MB** total (all files combined).

## Manifest Format

```json
{
  "name": "bufo",
  "colors": {
    "body": "#6B8E23",
    "bg": "#000000",
    "text": "#FFFFFF",
    "textDim": "#808080",
    "ink": "#000000"
  },
  "states": {
    "sleep": "sleep.gif",
    "idle": ["idle_0.gif", "idle_1.gif", "idle_2.gif"],
    "busy": "busy.gif",
    "attention": "attention.gif",
    "celebrate": "celebrate.gif",
    "dizzy": "dizzy.gif",
    "heart": "heart.gif"
  }
}
```

### Required fields

| Field | Notes |
|-------|-------|
| `name` | Pack identifier; overrides folder name in the push protocol |
| `states.sleep` | Single GIF filename |
| `states.idle` | Single filename **or** array of filenames (rotated randomly for variety) |
| `states.busy` | Single GIF filename |
| `states.attention` | Single GIF filename |
| `states.celebrate` | Single GIF filename |
| `states.dizzy` | Single GIF filename |
| `states.heart` | Single GIF filename |

### Optional color fields

Colors are used by the display renderer as palette hints. All are hex strings.

| Key | Purpose |
|-----|---------|
| `body` | Primary character color |
| `bg` | Background color |
| `text` | Primary text color |
| `textDim` | Secondary/dimmed text color |
| `ink` | Stroke/outline color |

## GIF Specifications

- **Width: exactly 96px** (other widths are not rendered correctly)
- Height: flexible, but keep proportional to 96px width for the 135×240 display
- Color depth: 64 colors recommended after compression
- Animated GIFs supported; loop count is ignored (firmware loops all GIFs)

## Compression

Use `gifsicle` to compress before pushing:

```bash
gifsicle --lossy=80 -O3 --colors 64 input.gif -o output.gif

# Batch compress all GIFs in a folder:
for f in *.gif; do gifsicle --lossy=80 -O3 --colors 64 "$f" -o "$f"; done
```

Use `tools/prep_character.py` from the repo for batch preparation:
```bash
python3 tools/prep_character.py <your-character-folder>
```

## Pushing a Character Pack

**Via BLE drop (Claude Desktop UI):**
1. Open Claude Desktop → Developer → Open Hardware Buddy…
2. Drag the character folder onto the drop target area in the window
3. Desktop streams files over BLE (sequential, waits for each ack)
4. Device stores to LittleFS; confirms when complete

**Via USB (faster, for development):**
```bash
python3 tools/flash_character.py characters/bufo
# Replace 'characters/bufo' with your folder path
```

## Designing States

| State | Design notes |
|-------|-------------|
| `sleep` | Gentle, slow — closed eyes or minimal movement. Plays when bridge is disconnected. |
| `idle` | Subtle life — occasional blink, glance, fidget. Use multiple idle GIFs for variety. |
| `busy` | Energetic, frantic — conveys "working hard." Plays when `running > 0`. |
| `attention` | Urgent, alert — the user needs to act. Plays when `waiting > 0`. |
| `celebrate` | Joyful, exuberant — triggered every 50K tokens. Can be big and flashy. |
| `dizzy` | Disoriented — triggered by device shake. Should feel reactive and silly. |
| `heart` | Warm, appreciative — triggered when user approves within 5 seconds of prompt. |

## Example: bufo pack structure

```
characters/bufo/
├── manifest.json
├── sleep.gif
├── idle_0.gif  through  idle_8.gif   (9 idle variants)
├── busy.gif
├── attention.gif
├── celebrate.gif
├── dizzy.gif
└── heart.gif
```

The bufo character set (`bufo.zone`) is MIT-licensed separately from the firmware.
It ships with the repo as the default example and is pre-installed on reference hardware.

## Built-in ASCII Characters (no GIF needed)

18 built-in ASCII species are available without installing any files. Cycle through them
from the device menu. Each has all 7 animation states drawn with TFT primitives.

Species list: axolotl, blob, cactus, capybara, cat, chonk, dragon, duck, ghost, goose,
mushroom, octopus, owl, penguin, rabbit, robot, snail, turtle.
