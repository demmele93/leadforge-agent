# OUTREACH.md — paid-plan outreach module (gated)

Outreach (sending email/SMS via Bella-style mailbox or the user's own) is DISABLED in the
base LeadForge product. It is unlocked only on a paid plan and with explicit user authorization.

## Why gated
- Compliance: sending requires the user's own mailbox auth (Composio Outlook/SMTP). Keys do
  not travel with the profile.
- Policy: per the owner's standing rule, no outreach without explicit authorization, and no
  spend without assigned capital.

## Plan tiers (hosted product)
- FREE / self-hosted: enrichment + brand dashboard + daily report. No sending.
- PAID: unlocks OPT-IN outreach engine — Composio Outlook send with required is_html flag,
  signature templating, 3-touch cap, opt-out honoring, daily cap enforcement.

## Opt-in flow (what the skill does when outreach is enabled)
1. Confirm user has authorized a sending mailbox.
2. Require an approved HTML signature file (signature.html).
3. Every outbound email uses is_html:true and the exact signature.
4. Honor STOP/unsubscribe; cap at daily_cap; max 3 touches per lead.
5. Never send to a contact with no verified email.

## This profile ships
- OUTREACH.md (this spec) only. The send code is provided server-side in the hosted product,
  not bundled in this portable profile, to keep the profile clean and compliance-safe.
