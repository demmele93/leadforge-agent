---
name: lead-enrich-dashboard
description: "Use when the user wants to spin up a lead-enrichment + dashboard agent for any brand. The skill 'grills' the user with scoping questions, scaffolds a brand-themed dashboard and enrichment pipeline, and begins finding + enriching business leads. Trigger: user says 'grill me', 'set up leads', 'build a lead dashboard', 'find businesses for <brand>', or wants a portable lead-enrichment agent."
---

# LeadForge — the "grill me" lead-enrichment + dashboard agent

You are scaffolding a LeadForge instance: a portable, brand-agnostic agent that discovers
named businesses in a target geography, enriches them with verified contacts (never guessed),
and renders a brand-themed Excel-style dashboard. One row per CONTACT, grouped by business.

## When this skill loads, DO THIS (the grill flow)

You MUST run the user through the grill before scaffolding. Be conversational, ask the
load-bearing questions, and let the user answer freely (don't force multiple-choice where an
open answer is better). Use the recommendations below as defaults when the user says "use your
recommendation" or stays silent.

### Step 1 — Website first (per user decision)
Ask: "Do you have a website for this brand? If yes, give me the URL and I'll base the brand
(theme, name) on it and ask only what's missing. If no, I'll ask you directly."

- If they give a URL: fetch it (web_extract), derive `brand.name`, `brand.color_primary`
  (dominant color), `brand.logo_url` if present, and `brand.website`. Then skip the brand
  questions you already answered from the site.
- If no URL: ask brand display name + primary color (hex) + optional logo URL.

### Step 2 — Targeting questions (ask all that the website didn't cover)
1. "What geography should I hunt in?" (default recommendation: a set of states/regions;
   for the original build we used WV VA KY TN NC OH GA). Accept city/state/region.
2. "Which industry verticals?" (default: any local B2B; allow specific like roofing, dental, HVAC).
3. "What pain signals should I look for?" (default: new openings, outage complaints,
   expansions, hiring, relocations). These are the discovery triggers.
4. "Targeted leads per day?" (default recommendation: 40; user asked for 'a couple dedicated
   like we have now' early, then scaled — confirm the number).
5. "Compliance boundaries?" — confirm: no guessed emails/phones/names, opt-out honored,
   public sources only, personal cell ONLY when explicitly published (multi-source logged).

### Step 3 — Scaffold the instance
1. Copy `config/config.example.json` to `config/config.json` and fill from Step 1–2.
2. Write `references/RESEARCH-CONTRACT.md` is already present — keep it; it encodes the rules.
3. Ensure `leads/` exists with an empty `queue.jsonl` (or seed from a prior run).
4. Start the dashboard: `python3 dashboard/server.py` (reads brand from config.json).
   Tell the user the local URL (default http://127.0.0.1:8787).

### Step 4 — Begin enrichment (the user explicitly wanted it to START finding leads)
Run, in order, from the profile root:
```
python3 scripts/daily_enrich.py
python3 scripts/name_harvest.py
python3 scripts/build_xlsx.py
python3 scripts/report.py
```
Then report: businesses found, contacts, how many have verified names/emails/cells, and the
dashboard URL. Do NOT send outreach (outreach is opt-in / paid only — see OUTREACH.md).

### Step 5 — Set up the daily cadence
Register the daily cron using `cron/leadforge-daily.cron` (import it via the cronjob tool:
create a job with that schedule + prompt + workdir = this profile). The prompt already
enforces RESEARCH-CONTRACT.md and the weekly "modify?" prompt.

## Dashboard behavior the user specified
- Business = MAIN row (general website contact as primary).
- A dropdown/expand per business shows all contacts (owner, GM, marketing, ops) — even if only
  one — for VERTICAL OUTREACH planning.
- Columns: Business, Vertical, Town, State, Main Contact (name+title), Business Phone, Main
  Email, Personal Cell, Pain, Stage, Score, # Contacts.
- Clicking a business expands its contacts.
- Blank/unverified fields render "—" (NEVER a guessed value).
- Brand colors/logo from config.json theme the whole UI.

## Deeper enrichment (user rule)
- If the user says "enrich" on a specific lead, OR the lead scores SUPER HOT (>=85), run an
  extra multi-source pass via `name_harvest.py` to hunt personal cell + confirm titles/names.
- Always cross-check personal-cell claims across MULTIPLE sources and log them in `sources`.

## Reporting & modify (user rule)
- Daily report printed each run (scripts/report.py).
- Weekly (Sundays): surface a "Would you like to modify targeting?" prompt. User can modify at
  ANY time by editing config.json or telling you.

## Hard rules (enforced in every run, autonomous or not)
- No fabricated contacts (email/phone/name). Guessed patterns forbidden.
- Personal cell ONLY when explicitly published on a public source; multi-source logged.
- Outreach disabled unless config.outreach.enabled AND explicit user authorization.
- Opt-outs honored immediately; 3-touch cap; daily cap from config.
- Respect the target geography/verticals exactly.

## Portability / export
This profile is self-contained under `~/.hermes/profiles/leadforge/`. To move it to another
machine: `tar czf leadforge.tar.gz -C ~/.hermes/profiles leadforge` then extract on target.
Secrets/keys are NOT bundled — the target re-auths their own mailbox for outreach.

## Files you have available in this profile
- README.md, OUTREACH.md, references/RESEARCH-CONTRACT.md, references/FIELD-SCHEMA.md
- config/config.example.json, cron/leadforge-daily.cron
- scripts/daily_enrich.py, name_harvest.py, build_xlsx.py, report.py
- dashboard/server.py, dashboard/index.html
- memories/ (product notes only)
