# 925law fixes (from tasks/review-2026-11-03.md)

Scope: developer items only. Lawyer / wording decisions stay open (see bottom).

## Before launch
- [x] Commit untouched handover as baseline
- [x] Strip C2PA metadata from PNG/WebP/SVG (review item 4)
- [x] kontakt.php hardening (items 2, 7, 9, 17, 18): no message echo, caps, consent, rate limit, honeypot rename, language-aware 303 redirects, no @, log failures, drop Google @import
- [x] .htaccess with HTTPS redirect, headers, CSP (hashes generated at build), deny sources (item 3)
- [x] Source + generator repair (item 1): no Google Fonts, fonts.css + Plausible from generator, relative paths, EN alt/lang/og-image, aria-label + honeypot label translated, JSON-LD per language, html5 formatter, build assertions
- [x] Regenerate and diff against shipped site; only intended changes

## Soon after
- [x] Mobile: hero content-sized on phones, 100svh, tap targets, font bumps, no scroll-snap, headline clamp (items 13-16)
- [x] Form: visible field borders, aria-live status instead of alert(), double-submit guard, ?error=1 handled (items 7, 12)
- [x] Kicker line with name / title / city / languages (item 8, additive only)
- [x] Footer landmark + skip link, `<main>` on legal pages
- [x] Portrait width/height/lazy
- [x] Housekeeping: delete DEPLOY.txt, drop unused Plex 500 font, add OFL licences, dead CSS, unused i18n keys, fetch_fonts.py path + checksums (item 26)
- [x] README for the repo

## Delivery
- [x] GitHub repo pushed (made public on 2026-11-04 because Pages needs a paid plan for private repos)
- [x] GitHub Pages workflow (static preview; form disabled on github.io, Plausible stripped, kontakt.php excluded, base path rewritten)
- [x] Verify preview URL renders at phone + desktop: https://dominik1999.github.io/max-homepage/

## Left open on purpose (not mine to decide)
- Section reorder (About up), "Warum" copy, phone number / address on page, "für Persönlichkeiten" wording, meta description length, OG image + favicon redesign
- Impressum ODR paragraph, insurance scope, consent vs. Art. 6 basis, privacy policy additions, English legal pages, Plausible DPA
