# Confluence Content Body Formats

## Format Overview

Confluence supports several body representations. The `representation` field tells the API which format you're sending or requesting.

| Representation | Direction | Description |
|---|---|---|
| `storage` | Read/Write | Confluence's internal XHTML-based format. **Use this for most API operations.** |
| `atlas_doc_format` | Read/Write | Atlassian Document Format (ADF) — JSON-based, same format used by Jira descriptions |
| `wiki` | Write only (v1) | Legacy wiki markup input format. Converted to storage on save. |
| `view` | Read only | Rendered HTML output as seen in browser |
| `export_view` | Read only | HTML export format (slightly different from view) |
| `styled_view` | Read only | HTML with inline CSS |
| `editor` | Read only | Internal editor representation (not stable for external use) |
| `anonymous_export_view` | Read only | Export view for unauthenticated rendering |

---

## Storage Format (XHTML)

The storage format is an XHTML subset with Confluence-specific extensions via the `ac:` namespace. This is what you'll use when writing or reading page content via the API.

### Basic HTML Elements

Standard HTML tags work in storage format:

```xml
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<p>A paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
<ul>
  <li>Item one</li>
  <li>Item two</li>
</ul>
<ol>
  <li>First</li>
  <li>Second</li>
</ol>
<table>
  <tbody>
    <tr>
      <th>Column A</th>
      <th>Column B</th>
    </tr>
    <tr>
      <td>Value 1</td>
      <td>Value 2</td>
    </tr>
  </tbody>
</table>
<a href="https://example.com">External link</a>
<br />
<hr />
```

### Links to Other Confluence Pages

Use the `ac:link` tag to create internal links:

```xml
<!-- Link to a page by page ID -->
<ac:link>
  <ri:page ri:content-title="Target Page Title" ri:space-key="ENG" />
  <ac:plain-text-link-body><![CDATA[Click here]]></ac:plain-text-link-body>
</ac:link>

<!-- Anchor link within the same page -->
<ac:link ac:anchor="my-anchor" />
```

### Images

```xml
<!-- Embedded attachment (image attached to the page) -->
<ac:image>
  <ri:attachment ri:filename="diagram.png" />
</ac:image>

<!-- External image -->
<ac:image ac:width="400">
  <ri:url ri:value="https://example.com/image.png" />
</ac:image>
```

### Macros

Macros are the primary way to embed dynamic content in Confluence pages. They use the `ac:structured-macro` tag:

#### Code Block Macro

```xml
<ac:structured-macro ac:name="code" ac:schema-version="1">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:parameter ac:name="theme">Confluence</ac:parameter>
  <ac:parameter ac:name="linenumbers">true</ac:parameter>
  <ac:parameter ac:name="title">Example Code</ac:parameter>
  <ac:plain-text-body><![CDATA[
def hello(name):
    print(f"Hello, {name}!")

hello("World")
  ]]></ac:plain-text-body>
</ac:structured-macro>
```

Code language options: `python`, `javascript`, `java`, `sql`, `bash`, `yaml`, `json`, `xml`, `html`, `css`, `go`, `ruby`, `php`, `none` (plain text)

#### Note / Info / Warning / Tip Panels

```xml
<ac:structured-macro ac:name="note">
  <ac:rich-text-body>
    <p>This is a note panel.</p>
  </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="info">
  <ac:parameter ac:name="title">Optional custom title</ac:parameter>
  <ac:rich-text-body><p>Info panel content.</p></ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="warning">
  <ac:rich-text-body><p>Warning content.</p></ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="tip">
  <ac:rich-text-body><p>Tip content.</p></ac:rich-text-body>
</ac:structured-macro>
```

#### Table of Contents

```xml
<ac:structured-macro ac:name="toc">
  <ac:parameter ac:name="minLevel">1</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="style">none</ac:parameter>
</ac:structured-macro>
```

#### Page Include (Embed Another Page)

```xml
<ac:structured-macro ac:name="include">
  <ri:page ri:content-title="Page To Include" ri:space-key="ENG" />
</ac:structured-macro>
```

#### Children Pages Macro

```xml
<ac:structured-macro ac:name="children">
  <ac:parameter ac:name="sort">title</ac:parameter>
  <ac:parameter ac:name="depth">2</ac:parameter>
</ac:structured-macro>
```

#### Jira Issues Macro

```xml
<ac:structured-macro ac:name="jira">
  <ac:parameter ac:name="server">Jira</ac:parameter>
  <ac:parameter ac:name="jqlQuery">project = ENG AND status = "In Progress"</ac:parameter>
  <ac:parameter ac:name="columns">key,summary,status,assignee</ac:parameter>
</ac:structured-macro>
```

#### Status Macro (colored badge)

```xml
<ac:structured-macro ac:name="status">
  <ac:parameter ac:name="colour">Green</ac:parameter>
  <ac:parameter ac:name="title">Done</ac:parameter>
</ac:structured-macro>
```
Colour options: `Green`, `Yellow`, `Red`, `Blue`, `Grey`, `Purple`

#### Expand (collapsible section)

```xml
<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">Click to expand</ac:parameter>
  <ac:rich-text-body>
    <p>Hidden content revealed on click.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

---

## Atlassian Document Format (ADF)

ADF is a JSON-based format used in newer API endpoints. It's the same format used in Jira description fields.

### Reading ADF from a page

```bash
GET /rest/api/content/12345678?expand=body.atlas_doc_format
# v2:
GET /wiki/api/v2/pages/12345678?body-format=atlas_doc_format
```

### ADF Structure

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Hello, " },
        { "type": "text", "text": "world!", "marks": [{ "type": "strong" }] }
      ]
    },
    {
      "type": "heading",
      "attrs": { "level": 2 },
      "content": [{ "type": "text", "text": "Section Title" }]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            { "type": "paragraph", "content": [{ "type": "text", "text": "Item one" }] }
          ]
        }
      ]
    },
    {
      "type": "codeBlock",
      "attrs": { "language": "python" },
      "content": [{ "type": "text", "text": "print('hello')" }]
    }
  ]
}
```

### ADF Node Types

| Node type | Description |
|---|---|
| `doc` | Root document node |
| `paragraph` | Paragraph block |
| `heading` | Heading (attrs: `level` 1–6) |
| `bulletList` / `orderedList` | Lists |
| `listItem` | List item (child of list) |
| `codeBlock` | Code block (attrs: `language`) |
| `blockquote` | Blockquote |
| `rule` | Horizontal rule |
| `table` / `tableRow` / `tableCell` / `tableHeader` | Tables |
| `text` | Inline text node |
| `hardBreak` | Line break |
| `mention` | User mention |
| `emoji` | Emoji |
| `inlineCard` | Inline smart card (URL preview) |
| `media` / `mediaGroup` | Embedded media/images |

### ADF Text Marks

```json
{ "type": "text", "text": "Bold and italic", "marks": [
  { "type": "strong" },
  { "type": "em" }
]}
```

Mark types: `strong` (bold), `em` (italic), `underline`, `strike`, `code`, `link` (attrs: `href`), `subsup` (attrs: `type`: `sub`|`sup`), `textColor` (attrs: `color`)

---

## Wiki Markup (Legacy Input)

Wiki markup is a legacy input-only format supported in v1. Confluence converts it to storage format on save.

```bash
POST /rest/api/content
{
  "type": "page",
  "title": "My Page",
  "space": { "key": "ENG" },
  "body": {
    "wiki": {
      "value": "h1. My Heading\n\nSome *bold* and _italic_ text.\n\n{code:language=python}\nprint('hello')\n{code}",
      "representation": "wiki"
    }
  }
}
```

Wiki markup syntax reference:
```
h1. Heading 1          *bold*           _italic_
h2. Heading 2          +underline+      -strikethrough-
h3. Heading 3          {{monospace}}    ??citation??

[link text|URL]        [page title]     [page title|space:page title]

||Header 1||Header 2||    # table header row
|Value 1|Value 2|         # table data row

* Bullet item          # Numbered item
** Nested bullet        ## Nested number

{code:language=python}
code here
{code}

{note}note text{note}
{info}info text{info}
{warning}warning text{warning}
{tip}tip text{tip}
```

---

## Choosing a Format

```
What are you trying to do?
├── Write/update a page via API → storage format (XHTML)
│   ├── Simple content (headings, paragraphs, lists, tables) → basic HTML tags
│   ├── Code blocks, panels, TOC → ac:structured-macro
│   └── Links to other pages → ac:link with ri:page
├── Read a page body for parsing or display → body.storage (expand param)
├── Feed content to another Atlassian tool (Jira, etc.) → ADF (atlas_doc_format)
├── Legacy/quick scripting where exact output isn't critical → wiki markup (v1 only)
└── Show the page as users see it → body.view (read-only, contains rendered HTML)
```

---

## Gotchas

- **Storage format is NOT plain HTML** — it uses the `ac:` and `ri:` XML namespaces; standard HTML without these will work for basic content but macros and internal links require the namespace
- **CDATA is required for macro body content** — always wrap content inside `ac:plain-text-body` in `<![CDATA[...]]>` to prevent XML parsing issues
- **Wiki markup is write-only** — you cannot read storage format back as wiki markup; conversion is one-way
- **ADF version field** — always include `"version": 1` at the doc root; omitting it may cause parse failures
- **Validation** — Confluence validates storage format on write; malformed XML returns a 400 error with a parse error message
- **Macro parameters** — find the exact parameter names by creating a page in the Confluence UI, then calling `GET /content/{id}?expand=body.storage` to inspect the generated storage format
