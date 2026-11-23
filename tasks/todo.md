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

## Review items 08-26 (2026-11-23, branch review-soon-and-nice, PR #1)
- [x] 08 About after services; hero portrait with name, title, city, languages
- [x] 10 Contact block with e-mail and address; phone slot (empty); response-time line
- [x] 11 "Warum" with four facts from existing copy
- [x] 12/14 Field border 3.48:1 (earlier fix was 1.96:1); tap targets 44px, mobile text 16px
- [x] 13/15 Compact mobile header, CTA in first screen at 390x740; breakpoint 1000px
- [x] 19 Privacy policy: confirmation e-mail, confidentiality note (DE + EN drafts)
- [x] 20 English Impressum and privacy policy; language-aware back links
- [x] 21 OG images and icons from the site fonts (build_og.py, build_icons.py)
- [x] 22 Two-column layouts on wide screens
- [x] 23 Tagline names the audiences; 925 hint under the stamp
- [x] 25 Legal pages generated from one template with site header and footer
- [x] 26 Shared site.css / legal.css, CSP style-src 'self', portrait 440x650, meta descriptions <= 155
- [x] Screenshot pass on the merged result (DE/EN start page, legal pages; 390 and 1440)
- [ ] 27 SPF/DKIM/DMARC and live form test: only after the Hetzner deploy

## Waiting for Max (not mine to decide)
- Response-time promise, new "Warum" copy, tagline without Angestellte/Beamte, phone number, condensed favicon digits
- The eight TODO(Max) points printed by every build (`build_site.py --final` fails while any remain): ODR paragraph, log retention, mailbox provider, rate-limit files, consent vs. Art. 6 basis, "call me" without a phone number, Stand date, "German version is authoritative" line
- Findings not changed: second contact channel and USt-IdNr. in the Impressum, Plausible location wording, Art. 13 GDPR gaps, insurance scope
- Plausible DPA
