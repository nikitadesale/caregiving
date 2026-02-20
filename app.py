import re
from datetime import datetime
import streamlit as st

# ----------------------------
# Safety + non-diagnostic guardrails
# ----------------------------
APP_TITLE = "Caregiver Support (Demo • Non-Diagnostic)"
DISCLAIMER = (
    "This demo app is **non-diagnostic** and **not medical advice**. "
    "It does not provide a diagnosis, treatment plan, or medication guidance. "
    "If you think someone may be in immediate danger, call your local emergency number."
)

CRISIS_NOTE = (
    "If someone might harm themselves or others, or you feel unsafe:\n"
    "- **US/Canada:** Call/text **988** (Suicide & Crisis Lifeline) or call **911**\n"
    "- **UK/Ireland:** Samaritans **116 123**\n"
    "- **Australia:** Lifeline **13 11 14**\n"
    "- Elsewhere: contact your local emergency number or local crisis line."
)

# ----------------------------
# Rule-based (regex + keywords) helpers
# ----------------------------
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())

def keyword_hit(text: str, patterns):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

def risk_flags(user_text: str):
    """
    Very simple keyword/regex checks for safety signals.
    Returns a dict of flags; does NOT diagnose.
    """
    t = normalize(user_text)

    crisis_patterns = [
        r"\bsuicid(al|e)\b",
        r"\bkill myself\b",
        r"\bend my life\b",
        r"\bself[- ]?harm\b",
        r"\bhurt myself\b",
        r"\boverdose\b",
        r"\bno reason to live\b",
        r"\bwant to die\b",
        r"\bkill (him|her|them|someone)\b",
        r"\bhurt (him|her|them|someone)\b",
        r"\bweapon\b",
    ]

    urgent_patterns = [
        r"\bchest pain\b",
        r"\bcan'?t breathe\b",
        r"\bnot breathing\b",
        r"\bunconscious\b",
        r"\bfainted\b",
        r"\bseizure\b",
        r"\bstroke\b",
        r"\bblue lips\b",
        r"\bsevere bleeding\b",
    ]

    burnout_patterns = [
        r"\boverwhelmed\b",
        r"\bburnt? out\b",
        r"\bexhausted\b",
        r"\bno sleep\b",
        r"\bcan'?t cope\b",
        r"\bon edge\b",
        r"\banxious\b",
        r"\bpanic\b",
        r"\bdepressed\b",
        r"\bhopeless\b",
    ]

    conflict_patterns = [
        r"\barguments?\b",
        r"\bfighting\b",
        r"\bshouting\b",
        r"\bthreat(en|s)\b",
        r"\bunsafe\b",
        r"\babuse\b",
    ]

    wandering_patterns = [
        r"\bwand(er|ering|ed)\b",
        r"\blost\b",
        r"\bleft the house\b",
        r"\beloped\b",
    ]

    falls_patterns = [
        r"\bfell\b",
        r"\bfall\b",
        r"\bslipped\b",
        r"\bhead hit\b",
    ]

    return {
        "crisis": keyword_hit(t, crisis_patterns),
        "urgent_medical": keyword_hit(t, urgent_patterns),
        "burnout": keyword_hit(t, burnout_patterns),
        "conflict_safety": keyword_hit(t, conflict_patterns),
        "wandering": keyword_hit(t, wandering_patterns),
        "falls": keyword_hit(t, falls_patterns),
    }

def caregiving_suggestions(user_text: str):
    """
    Pure keyword-based suggestions. Non-diagnostic and non-medication.
    Returns list of structured suggestions + resource hints.
    """
    t = normalize(user_text)

    buckets = []

    # Routine / daily care
    if keyword_hit(t, [r"\bmeds?\b", r"\bmedication\b", r"\bpills?\b"]):
        buckets.append({
            "title": "Medication reminders (non-medical)",
            "items": [
                "Use a **pill organizer** or reminder alarms (no dosing advice).",
                "Keep an **up-to-date medication list** (name + schedule) to share with a clinician if needed.",
                "If there are concerns or side effects, **contact a licensed clinician/pharmacist**."
            ]
        })

    # Sleep / rest
    if keyword_hit(t, [r"\bsleep\b", r"\binsomnia\b", r"\bup all night\b", r"\bno sleep\b"]):
        buckets.append({
            "title": "Sleep support (practical)",
            "items": [
                "Try a simple bedtime routine (dim lights, reduce noise, consistent timing).",
                "If caregiving allows: schedule a **nap window** or ask someone to cover for 30–60 minutes.",
                "Track what disrupts sleep (time, triggers) to discuss with a clinician if needed."
            ]
        })

    # Nutrition / hydration
    if keyword_hit(t, [r"\bnot eating\b", r"\bappetite\b", r"\bdehydrated\b", r"\bdrinking\b"]):
        buckets.append({
            "title": "Nutrition & hydration (non-diagnostic)",
            "items": [
                "Offer small, frequent snacks if full meals are hard.",
                "Keep water visible and offer sips regularly if safe to do so.",
                "If there are swallowing concerns, weight loss, or dehydration signs: **seek licensed medical help**."
            ]
        })

    # Falls / mobility
    if keyword_hit(t, [r"\bfell\b", r"\bfall\b", r"\bunsteady\b", r"\bwalker\b"]):
        buckets.append({
            "title": "Fall-prevention basics",
            "items": [
                "Clear walkways, remove loose rugs, improve lighting.",
                "Use stable footwear and consider grab bars in bathroom areas.",
                "After a fall or head hit: consider **urgent medical evaluation**."
            ]
        })

    # Confusion / memory keywords (still non-diagnostic)
    if keyword_hit(t, [r"\bconfus(ed|ion)\b", r"\bforget(ful|ting)\b", r"\bmemory\b", r"\bdisoriented\b"]):
        buckets.append({
            "title": "Confusion/memory concerns (non-diagnostic)",
            "items": [
                "Use orientation cues: calendar, clock, simple signage, consistent routines.",
                "Keep notes of patterns (time of day, triggers) for a clinician if you choose.",
                "If confusion is sudden or severe, consider **urgent evaluation**."
            ]
        })

    # Caregiver stress
    if keyword_hit(t, [r"\boverwhelmed\b", r"\bexhausted\b", r"\bburnt? out\b", r"\bstressed\b", r"\banxious\b"]):
        buckets.append({
            "title": "Caregiver stress reset (10-minute options)",
            "items": [
                "Pick one: hydration, quick snack, 10 slow breaths, short walk, or text a friend.",
                "Ask for a specific, small help task (e.g., groceries, 1-hour cover, laundry).",
                "Consider caregiver support groups (local, online) or respite services."
            ]
        })

    # If nothing matched
    if not buckets:
        buckets.append({
            "title": "General support",
            "items": [
                "Write down today’s top 1–2 challenges and what helped (even slightly).",
                "Identify one person or service you can contact for practical support.",
                "If you’re worried about safety or health changes, contact a licensed professional."
            ]
        })

    return buckets

def format_care_note(caregiver: str, patient: str, date_str: str, mood: str, concerns: str, what_helped: str, questions: str):
    """
    Produces a structured note the user can copy/paste.
    """
    ts = date_str or datetime.now().strftime("%Y-%m-%d")
    return f"""CARE NOTE (Non-Diagnostic) — {ts}

Caregiver: {caregiver or "[Name]"}
Care Recipient: {patient or "[Name]"}

What happened (objective):
- {concerns.strip() if concerns.strip() else "[Add objective observations, times, and context]"}

Caregiver stress level (self-rated):
- {mood}

What helped / actions taken (non-medical):
- {what_helped.strip() if what_helped.strip() else "[Add practical steps you took]"}

Questions for a licensed professional (optional):
- {questions.strip() if questions.strip() else "[Add questions for clinician/social worker, if any]"}

Safety note:
- If symptoms are severe, sudden, or there are safety concerns, contact local emergency services or a licensed professional.
"""

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="💛", layout="centered")
st.title("💛 " + APP_TITLE)
st.markdown(DISCLAIMER)
st.divider()

tab1, tab2, tab3 = st.tabs(["📝 Care Note Builder", "🧭 Support Suggestions", "✅ Quick Check-in"])

with tab1:
    st.subheader("📝 Care Note Builder (copy/paste)")
    st.caption("Creates a structured note you can share with family, a care team, or keep for your records. No diagnosis, no medication advice.")

    col1, col2 = st.columns(2)
    with col1:
        caregiver = st.text_input("Caregiver name (optional)")
        date_str = st.text_input("Date (YYYY-MM-DD, optional)")
    with col2:
        patient = st.text_input("Care recipient name (optional)")
        mood = st.select_slider("Your stress level (self-rated)", options=["Low", "Medium", "High", "Very High"], value="Medium")

    concerns = st.text_area("What happened today? (objective details: times, behaviors, triggers)", height=120)
    what_helped = st.text_area("What helped / what you tried (non-medical actions)", height=90)
    questions = st.text_area("Questions for a licensed professional (optional)", height=80)

    if st.button("Generate Care Note"):
        note = format_care_note(caregiver, patient, date_str, mood, concerns, what_helped, questions)
        st.success("Generated. Copy/paste below:")
        st.code(note, language="markdown")

with tab2:
    st.subheader("🧭 Support Suggestions (rule-based)")
    st.caption("Enter a short description. The app uses only keywords/regex to show practical, non-diagnostic suggestions.")

    user_text = st.text_area("Describe the situation (no private info needed)", height=120)

    if st.button("Get Suggestions"):
        flags = risk_flags(user_text)

        # Safety banners (non-diagnostic)
        if flags["crisis"]:
            st.error("Potential self-harm/violence language detected. Please seek immediate help.")
            st.markdown(CRISIS_NOTE)

        if flags["urgent_medical"]:
            st.warning("Possible urgent medical keywords detected. Consider contacting local emergency services or a licensed clinician.")

        if flags["conflict_safety"]:
            st.warning("Safety/conflict keywords detected. Prioritize immediate safety and consider local support services.")

        if flags["wandering"]:
            st.info("Wandering/lost keywords detected. Consider safety steps (door alarms, ID info, supervision) and local guidance.")

        if flags["falls"]:
            st.info("Falls keywords detected. Consider fall-safety steps and seek licensed evaluation if there’s injury/head impact.")

        st.divider()

        buckets = caregiving_suggestions(user_text)
        for b in buckets:
            with st.expander(b["title"], expanded=True):
                for item in b["items"]:
                    st.write(f"- {item}")

        st.divider()
        st.caption("Reminder: This tool is informational only and does not diagnose or recommend medication changes.")

with tab3:
    st.subheader("✅ Quick Check-in (caregiver-focused)")
    st.caption("A lightweight check-in that suggests next steps using keywords only.")

    feeling = st.text_input("In one sentence: how are you doing right now?")
    top_need = st.selectbox(
        "What do you need most in the next 24 hours?",
        ["Rest", "Help from someone else", "A plan for tomorrow", "Emotional support", "Safer environment", "Not sure"]
    )

    if st.button("Show Next Steps"):
        combined = f"{feeling} {top_need}"
        flags = risk_flags(combined)

        if flags["crisis"]:
            st.error("If you might harm yourself or someone else, get immediate help.")
            st.markdown(CRISIS_NOTE)

        st.write("**Suggested next steps (non-medical):**")
        steps = []

        if top_need == "Rest":
            steps += [
                "Block a 20–60 minute rest window (ask someone to cover if possible).",
                "Do one small reset: water + snack + 10 slow breaths.",
            ]
        elif top_need == "Help from someone else":
            steps += [
                "Send a specific ask: “Can you cover from 3–4pm?” or “Can you pick up groceries?”",
                "If available, explore respite options (community programs, local agencies).",
            ]
        elif top_need == "A plan for tomorrow":
            steps += [
                "List 3 must-dos and 1 nice-to-have. Drop the rest.",
                "Prepare one thing tonight that reduces friction tomorrow (med list, bag, meals).",
            ]
        elif top_need == "Emotional support":
            steps += [
                "Text/call one supportive person with a simple message: “Can you check in with me today?”",
                "Consider a caregiver support group (online or local).",
            ]
        elif top_need == "Safer environment":
            steps += [
                "Do a 5-minute safety sweep: clear walkways, improve lighting, secure tripping hazards.",
                "If you feel unsafe, contact local support services or emergency services.",
            ]
        else:
            steps += [
                "Pick the smallest next action: drink water, sit down, write 2 sentences about what’s hardest.",
                "If you’re concerned about safety or sudden changes, contact a licensed professional.",
            ]

        for s in steps:
            st.write(f"- {s}")

st.divider()
st.caption("Built for a workshop demo: no accounts, no APIs, simple deploy.")
