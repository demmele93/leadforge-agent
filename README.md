# LeadForge — the lead-enrichment agent

LeadForge is a portable, brand-agnostic lead-enrichment + dashboard agent for Hermes.
It discovers named businesses in a target geography, enriches them with verified contacts
(never guessed), and renders a brand-themed Excel-style dashboard.

This profile is self-contained. Drop it in `~/.hermes/profiles/leadforge/` on any machine
with Hermes installed and load the `lead-enrich-dashboard` skill to "grill" the user and
scaffold their instance.

## What it does
- Grills the user for brand + targeting (uses their website when available, asks only what's missing).
- Discovers businesses via targeted public searches (new openings, outage complaints, expansions).
- Enriches each business with a MAIN contact + multiple people (vertical-outreach ready).
- Hunts personal cell numbers ONLY when explicitly published, across multiple sources, and logs every source.
- Renders a brand-themed dashboard (business = main row, per-business contact dropdown).
- Daily enrichment + daily report; weekly "modify?" prompt.
- Outreach is OPT-IN and gated to paid plans (see OUTREACH.md).

## Layout
- skills/lead-enrich-dashboard/SKILL.md  — the "grill me" skill
- scripts/                               — daily_enrich.py, name_harvest.py, build_xlsx.py, report.py
- dashboard/                             — server.py + index.html (brand-templated)
- references/                            — RESEARCH-CONTRACT.md (compliance), FIELD-SCHEMA.md
- config/                               — config.example.json, COPY to config.json on scaffold
- cron/                                 — leadforge-daily.cron (exportable cron def)
- memories/                             — product notes only (no secrets)
- leads/                                — queue.jsonl (the database), *.xlsx
- OUTREACH.md                           — paid-plan outreach module spec

## Export / port
```
tar czf leadforge-profile.tar.gz -C ~/.hermes/profiles leadforge
```
Target machine:
```
mkdir -p ~/.hermes/profiles && tar xzf leadforge-profile.tar.gz -C ~/.hermes/profiles
```

## Publish to GitHub (requires a token — not bundled)
See `publish.sh`. You must supply a GitHub PAT with repo scope. The agent will NOT
embed credentials; the user pastes the token at publish time only.
