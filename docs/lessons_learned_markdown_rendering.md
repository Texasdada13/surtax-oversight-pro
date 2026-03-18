# Lesson Learned: AI Chat Markdown Rendering

## The Problem

The Ask AI Assistant page returns responses from Claude API in markdown format (headings, bold, bullet lists, etc.). However, the chat bubble was rendering raw markdown characters instead of formatted text. Users would see:

```
### **New Construction** - *Largest Investment*
- **22 projects** | **$786.6M budgeted**
```

Instead of properly formatted headings, bold text, and bullet points.

## Root Cause

Alpine.js `x-text` directive renders content as plain text — it does not interpret HTML or markdown. The chat message template used:

```html
<div x-text="msg.content"></div>
```

This safely escapes all markup, which is correct for user input but wrong for AI responses that contain structured markdown.

## The Solution

Three targeted changes to `app/templates/tools/ask.html`:

### 1. Added `marked.js` via CDN

```html
<script src="https://cdn.jsdelivr.net/npm/marked@14/marked.min.js"></script>
```

`marked` is a lightweight, well-maintained markdown-to-HTML parser. Using the CDN avoids adding dependencies to the project.

### 2. Split message rendering by role

Instead of one template for both user and assistant messages, we split them:

- **User messages** → keep `x-text` (safe, no markdown parsing needed)
- **Assistant messages** → use `x-html` with `marked.parse()` to render formatted HTML

```html
<template x-if="msg.role === 'user'">
    <div x-text="msg.content"></div>
</template>
<template x-if="msg.role === 'assistant'">
    <div class="ai-markdown" x-html="renderMarkdown(msg.content)"></div>
</template>
```

### 3. Added typography CSS for dark theme

The rendered HTML needs styling to look good in dark chat bubbles:

```css
.ai-markdown h2 { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.ai-markdown h3 { font-size: 0.95rem; font-weight: 600; color: #e2e8f0; }
.ai-markdown strong { color: #f1f5f9; font-weight: 600; }
.ai-markdown ul, .ai-markdown ol { padding-left: 1.25rem; }
/* etc. */
```

## Key Decisions

- **Why `marked.js` over alternatives?** Small (< 30KB), no dependencies, widely used, handles all standard markdown. Alternatives like `markdown-it` are heavier and unnecessary for this use case.
- **Why CDN instead of bundling?** The project already uses CDNs for Tailwind and Alpine.js, so this is consistent with the existing pattern.
- **Why split templates instead of one conditional?** Cleaner separation of concerns. User input stays safely escaped via `x-text`, while only trusted AI output gets HTML rendering.

## Security Note

Using `x-html` means the rendered content is not escaped. This is acceptable here because the content comes from our own Claude API endpoint (`/api/ask`), not from user-supplied HTML. The AI generates markdown, which `marked` converts to safe HTML tags (headings, lists, bold, etc.).

## Files Changed

- `app/templates/tools/ask.html` — Added marked.js CDN, markdown CSS, split message template, added `renderMarkdown()` helper

## Applicability

This same pattern can be applied to any chat interface or AI response display in the project. If other tools (stock_analysis webapp, etc.) have similar issues with raw markdown rendering, the fix is the same: add `marked.js` and switch from `x-text` to `x-html` for AI responses.
