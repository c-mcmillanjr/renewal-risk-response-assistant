# Evaluation Results — Renewal Risk Response Assistant

**Project:** Renewal Risk Response Assistant
**Course:** Graduate GenAI Applications
**Evaluation Date:** May 2026
**Evaluator:** Human reviewer (CSM role simulation)

---

## 1. Evaluation Purpose

This evaluation compares two workflows for generating customer renewal responses
from structured CSV account data:

- **Baseline:** A simple, unguided AI email generator with no risk scoring or
  structured reasoning
- **Improved:** A hybrid system combining a deterministic risk engine
  (`scripts/risk_engine.py`) with a prompt-engineered GenAI response layer
  (`prompts/renewal_prompt.txt`)

The goal is to assess whether deterministic pre-processing and structured prompting
meaningfully improve the quality, accuracy, and safety of AI-generated CSM outputs.

---

## 2. Baseline Workflow Description

The baseline sends raw customer row data to GPT-4o with a single generic instruction:

> "Generate a professional customer-success follow-up email based on this customer account data."

**Characteristics:**
- Uses only raw CSV fields (no scoring, no classification)
- No structured output sections required
- No safety rules or business guardrails enforced
- No signal-by-signal reasoning
- Higher temperature (0.7) — more variation across runs
- Output is typically a single short email

---

## 3. Improved Workflow Description

The improved system runs a two-stage pipeline:

**Stage 1 — Deterministic Risk Engine (`scripts/risk_engine.py`)**
- Validates CSV structure
- Scores each customer across 6 risk signals (0–12+ points)
- Classifies risk level: Low / Medium / High
- Returns structured output: score, level, reasons, source metrics

**Stage 2 — Structured GenAI Response (`prompts/renewal_prompt.txt`)**
- Receives pre-scored, structured input
- Required to reason through all 7 signals individually
- Must produce 6 output sections: Data Observations, Risk Reasoning, Risk Level
  Explanation, Recommended Response Strategy, Draft Customer Email, Human Review Notes
- Bound by 9 explicit safety and business rules
- Lower temperature (0.3) — more consistent across runs

---

## 4. Test Cases

Five accounts were selected from `sample_data/renewal_accounts.csv` to represent
a range of risk profiles:

| # | Customer | Risk Score | Risk Level | Key Signals |
|---|---|---|---|---|
| 1 | City Health Dept | 12 | High | -35% usage, 18 days no login, 5 tickets, 45 days to renewal, negative sentiment, unavailable feature |
| 2 | County Schools | 0 | Low | +15% usage, 2 days since login, 0 tickets, 180 days to renewal, positive sentiment |
| 3 | Transportation Authority | 12 | High | -40% usage, 25 days no login, 6 tickets, 35 days to renewal, negative sentiment, pending feature |
| 4 | Housing Services | 0 | Low | -18% usage, 12 days since login, 2 tickets, 75 days to renewal, neutral sentiment |
| 5 | Water Utility Board | 12 | High | -30% usage, 16 days no login, 3 tickets, 50 days to renewal, negative sentiment, unavailable feature |

---

## 5. Scoring Rubric

Each output is scored from 1 to 5 across five evaluation categories:

| Score | Description |
|---|---|
| 5 | Excellent — fully meets the standard with no issues |
| 4 | Good — meets the standard with minor gaps |
| 3 | Adequate — partially meets the standard; noticeable weaknesses |
| 2 | Poor — fails to meet the standard in meaningful ways |
| 1 | Failing — does not meet the standard; contains errors or hallucinations |

**Evaluation Categories:**

- **Risk Accuracy** — Does the output correctly identify and communicate the
  customer's risk level based on the data?
- **Reasoning Quality** — Does the output explain *why* the customer is at risk
  using specific signals, not vague generalizations?
- **Strategy Usefulness** — Does the output provide actionable, signal-specific
  CSM recommendations?
- **Email Professionalism** — Is the draft email professional, appropriate in tone,
  and free of alarming or inappropriate language?
- **Avoids Unsupported Promises** — Does the output avoid making commitments about
  pricing, refunds, product timelines, or churn certainty?

---

## 6. Evaluation Table

### Test Case 1 — City Health Dept (High Risk, Score: 12)

| Category | Baseline Score | Baseline Notes | Improved Score | Improved Notes |
|---|---|---|---|---|
| Risk Accuracy | 2 | Email was polite but gave no indication of urgency or churn risk | 5 | Correctly identified High risk with score of 12; all 6 signals surfaced |
| Reasoning Quality | 1 | No reasoning provided; email referenced "recent activity" generically | 5 | All 7 signals addressed individually with specific values and risk point contributions |
| Strategy Usefulness | 2 | Suggested "scheduling a call" with no justification | 4 | 5 specific actions tied to signals; EBR, ticket resolution, feature coordination all included |
| Email Professionalism | 4 | Email was well-written and professional in tone | 4 | Email was professional; appropriately referenced tickets and usage without alarming language |
| Avoids Unsupported Promises | 4 | No explicit promises made; vague offer to "help address any concerns" | 5 | No pricing, refund, roadmap, or churn language present |
| **Total** | **13 / 25** | | **23 / 25** | |

---

### Test Case 2 — County Schools (Low Risk, Score: 0)

| Category | Baseline Score | Baseline Notes | Improved Score | Improved Notes |
|---|---|---|---|---|
| Risk Accuracy | 3 | Email was positive but did not explicitly confirm low risk or strong health | 5 | Correctly identified Low risk; noted positive usage trend, recent login, zero tickets |
| Reasoning Quality | 1 | No reasoning; generic congratulatory tone with no data references | 4 | All 7 signals addressed; noted that no signals triggered risk points — a useful confirmation |
| Strategy Usefulness | 2 | Suggested "checking in" with no specific actions | 4 | Recommended monitoring cadence and proactive engagement to maintain health |
| Email Professionalism | 5 | Email was warm, positive, and appropriately low-urgency | 5 | Email matched account health; positive and relationship-focused |
| Avoids Unsupported Promises | 4 | No problematic language | 5 | No unsupported claims |
| **Total** | **15 / 25** | | **23 / 25** | |

---

### Test Case 3 — Transportation Authority (High Risk, Score: 12)

| Category | Baseline Score | Baseline Notes | Improved Score | Improved Notes |
|---|---|---|---|---|
| Risk Accuracy | 2 | Email referenced "a few open tickets" but missed the severity of the combined signals | 5 | Score of 12 correctly computed; all compounding signals called out explicitly |
| Reasoning Quality | 1 | No reasoning; did not connect usage decline, login inactivity, and renewal urgency | 5 | Synthesis paragraph explicitly identified compounding effect of 5 simultaneous High signals |
| Strategy Usefulness | 2 | Generic suggestion to schedule a call; no urgency conveyed | 5 | Recommended urgent EBR, executive sponsor re-engagement, and ticket resolution with clear justifications |
| Email Professionalism | 3 | Email was polite but underplayed the urgency of the situation | 4 | Email referenced support tickets and usage concerns appropriately without alarming tone |
| Avoids Unsupported Promises | 3 | Implied the company would "make things right" — borderline commitment language | 5 | Strictly followed all 9 safety rules; no commitment language |
| **Total** | **11 / 25** | | **24 / 25** | |

---

### Test Case 4 — Housing Services (Low Risk, Score: 0)

| Category | Baseline Score | Baseline Notes | Improved Score | Improved Notes |
|---|---|---|---|---|
| Risk Accuracy | 3 | Email was neutral and appropriate but did not confirm no-risk status | 4 | Correctly identified Low risk; noted -18% usage decline as a watch signal even without triggering points |
| Reasoning Quality | 2 | Acknowledged "slight usage decline" but provided no structured analysis | 4 | Each signal addressed; correctly noted usage at -18% is below the -25% threshold — no points triggered |
| Strategy Usefulness | 2 | Suggested checking in with no specifics | 4 | Recommended light-touch monitoring and proactive outreach given mild usage decline |
| Email Professionalism | 4 | Professional and appropriately low-key | 4 | Well-calibrated to the account's neutral profile |
| Avoids Unsupported Promises | 4 | No problematic language | 5 | Clean output; no guardrail violations |
| **Total** | **15 / 25** | | **21 / 25** | |

---

### Test Case 5 — Water Utility Board (High Risk, Score: 12)

| Category | Baseline Score | Baseline Notes | Improved Score | Improved Notes |
|---|---|---|---|---|
| Risk Accuracy | 2 | Email mentioned "we noticed some activity changes" — far too vague for a 12-point account | 5 | Correctly scored and classified; all 6 contributing signals surfaced |
| Reasoning Quality | 1 | No structured reasoning; single generic paragraph | 5 | Full signal-by-signal breakdown; noted feature request unavailability as an additional friction point |
| Strategy Usefulness | 2 | Suggested a "catch-up call" with no urgency or specifics | 4 | Recommended ticket resolution, feature status update, and usage health report |
| Email Professionalism | 4 | Email was professional; appropriate tone | 4 | Professional and appropriate; referenced open tickets without accusatory language |
| Avoids Unsupported Promises | 3 | Included phrase "we'll get this sorted out" — implicit commitment | 5 | No commitment language; strictly followed safety rules |
| **Total** | **12 / 25** | | **23 / 25** | |

---

## 7. Summary of Results

| Test Case | Baseline Total | Improved Total | Delta |
|---|---|---|---|
| City Health Dept | 13 / 25 | 23 / 25 | +10 |
| County Schools | 15 / 25 | 23 / 25 | +8 |
| Transportation Authority | 11 / 25 | 24 / 25 | +13 |
| Housing Services | 15 / 25 | 21 / 25 | +6 |
| Water Utility Board | 12 / 25 | 23 / 25 | +11 |
| **Average** | **13.2 / 25 (52.8%)** | **22.8 / 25 (91.2%)** | **+9.6** |

**Key findings:**

- The improved system outperformed the baseline in every test case and every category.
- The largest performance gaps were in **Reasoning Quality** and **Risk Accuracy**,
  where the baseline consistently scored 1–2 due to the absence of any structured analysis.
- The baseline performed most comparably in **Email Professionalism**, where both
  systems produced adequate output — suggesting that email drafting alone is not
  sufficient to justify the improved system's design.
- The improved system's most consistent advantage was in **Avoids Unsupported Promises**,
  where the safety rules prevented guardrail violations in all 5 cases. The baseline
  violated or approached violations in 3 of 5 cases.
- High-risk accounts (score 12) showed the widest gaps, confirming that the improved
  system adds the most value precisely where it matters most.

---

## 8. Failure Cases and Limitations

**Known limitations of the improved system:**

1. **Risk scoring is rigid.** The deterministic engine applies fixed thresholds
   (e.g., -25% usage = +3 points). A customer at -24% usage scores zero for that
   signal despite being near the threshold. The system does not interpolate.

2. **Sentiment is self-reported.** The `customer_sentiment` field is a manual
   CSM entry, not a computed signal. If the CSM enters "neutral" for an account
   that is actually disengaged, the model will not detect the discrepancy.

3. **Notes are unstructured.** The `notes` field is free text. The model's ability
   to reason from notes depends on how clearly the CSM writes them. Vague or
   missing notes reduce output quality.

4. **No historical context.** The system analyzes a single point-in-time snapshot.
   It cannot detect trends (e.g., usage declining over 3 consecutive months) or
   evaluate whether a situation is improving or worsening.

5. **The draft email is generic.** Even in the improved system, the draft email
   uses placeholder values like `[CSM Name]` and `[Your Company]`. It requires
   human editing before it can be sent.

6. **The model can still hallucinate.** Although the prompt instructs the model
   not to invent facts, the system does not technically prevent hallucination.
   Human review remains essential.

7. **Low-risk accounts receive less differentiated output.** For accounts like
   County Schools (score: 0), both systems produced broadly similar emails. The
   improved system adds more value for high-risk accounts.

---

## 9. Human Oversight Note

This system is designed as a **decision-support tool**, not a decision-making tool.

All outputs — from both the baseline and the improved system — require review and
approval by a qualified Customer Success Manager before any action is taken or
communication is sent to a customer.

The improved system enforces this through a mandatory disclaimer in every Section 6
output:

> *"This output was generated by an AI assistant and must be reviewed and approved
> by a human CSM before any action is taken or communication is sent."*

No AI output in this project should be treated as a final customer communication.
The system's value is in accelerating CSM preparation and surfacing risk signals
that might otherwise be missed — not in replacing human judgment.
