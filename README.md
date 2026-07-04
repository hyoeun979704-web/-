# 청첩장 (Wedding Invitation)

A mobile-first, single-page Korean wedding invitation (청첩장) — static HTML/CSS/JS,
no build step, deployable to any static host (GitHub Pages, Netlify, Vercel, S3…).

## ⚠️ Template notice

This is a **template implementation**, created because the original Claude Design
source (`청첩장_배포.dc.html`) could not be imported in the current environment —
the `claude_design` MCP requires interactive `/design-login`, which isn't
available in a Claude Code **web** session.

All names, dates, venue, phone numbers, account numbers, and photos are
**placeholders** (marked with `data-placeholder` attributes in `index.html` and a
`WEDDING` config object in `js/main.js`). To finish:

1. Send the real design via **"Send to Claude Code Web"** from Claude Design, or
   paste the `청첩장_배포.dc.html` source, and the template can be replaced/reconciled.
2. Or edit the placeholders directly (see **Customizing** below).

## Structure

```
index.html      # markup + sections
css/style.css   # styling (soft romantic palette, mobile-first)
js/main.js      # calendar, D-day, gallery lightbox, copy, RSVP, guestbook
assets/         # photos (og-image.jpg, gallery images) — add your own
```

## Sections

Hero · 인사말(greeting) · 예식 안내 + 캘린더/D-Day · 갤러리 · 오시는 길(location) ·
마음 전하실 곳(accounts) · 참석 의사(RSVP) · 방명록(guestbook) · 공유(share).

## Customizing

- **Names / family / venue / phone**: edit the `data-placeholder` spans and
  `tel:` / text content in `index.html`.
- **Wedding date**: update the `WEDDING` object at the top of `js/main.js`
  (drives the calendar highlight and D-day countdown) and the display strings
  in `index.html`.
- **Photos**: drop images into `assets/` and replace the gradient placeholders
  (hero `.hero__photo` background in CSS; gallery tiles generated in `main.js`).
- **RSVP & guestbook** currently persist to `localStorage` for demo purposes.
  For real submissions, wire the form handlers in `main.js` to a backend
  (e.g. a Google Form, Supabase table, or serverless endpoint).

## Local preview

Any static server works, e.g.:

```
python3 -m http.server 8000
# then open http://localhost:8000
```
