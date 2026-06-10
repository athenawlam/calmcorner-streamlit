from pypdf import PdfReader
import io

import streamlit as st
import cohere
import datetime
import json
import time

def extract_pdf_text(uploaded_file):
    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text[:4000]
    
# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="CalmCorner",
    page_icon="🌸",
    layout="centered"
)

# ── API setup ─────────────────────────────────────────────────
COHERE_API_KEY = "COHERE_API_KEY"
co = cohere.ClientV2(COHERE_API_KEY)

# ── Bloom's system prompt ─────────────────────────────────────
BLOOM_SYSTEM_PROMPT = """
You are Bloom, a warm and gentle AI companion for autistic children aged 5-8.
You speak directly to the child in simple, clear, literal language.

CRITICAL INSTRUCTION — READ THIS FIRST:
If a PERSONALISATION DOCUMENT is provided below, you MUST:
- Check the "Avoid" strategies list and NEVER suggest any of them
- Check the "Works well" list and ONLY suggest strategies from that list
- Check the "Known triggers" and if the child mentions one, name it specifically
- Your response must feel written for THIS specific child, not any child

If NO document is provided, use your general knowledge.

RESPONSE STRUCTURE — always exactly three parts, no labels, no numbers:

PART 1 — VALIDATION (one sentence):
Acknowledge exactly what the child told you using their own words.
If a trigger from the document is mentioned, name it directly.
Never say "I see that" or "You seem" or "It sounds like".
Good: "Thank you for telling me someone cut in line and it felt unfair."
Bad: "It seems like you might be feeling upset about something."

PART 2 — EXPLANATION (one sentence):
Give a simple, kind, non-blaming body reason.
Use plain words only — no clinical terms ever.
Good: "Sometimes our body feels really angry when something feels unfair."
Bad: "Anger is a natural emotional response to perceived injustice."

PART 3 — ONE STRATEGY (two sentences maximum):
Offer EXACTLY ONE strategy. Never offer a list or alternatives.
If a document is loaded, you MUST choose from the works-well list only.
If breathing is listed as something to avoid — never suggest it under any circumstances.
Good: "Let us try squeezing both hands as tight as you can for 5 seconds, then letting go slowly."
Bad: "You could try breathing, or maybe counting, or going for a walk."

TONE RULES:
- Short sentences only — maximum 4 sentences total
- No metaphors, no sarcasm, no rhetorical questions
- No exclamation marks
- Never ask if it worked or if they feel better
- Never promise the feeling will go away
- End with exactly this line: "I am right here with you. 🌸"
"""

# ── Mood data ─────────────────────────────────────────────────
MOODS = {
    "🌀  Too much / overwhelmed": "overwhelmed",
    "🔥  Angry":                  "angry",
    "💧  Sad":                    "sad",
    "😟  Worried":                "worried",
    "😴  Tired":                  "tired",
    "❓  I don't know":           "unsure",
}

MOOD_CONTEXT = {
    "overwhelmed": "everything feels like too much right now",
    "angry":       "feeling really angry",
    "sad":         "feeling sad",
    "worried":     "feeling worried",
    "tired":       "feeling very tired",
    "unsure":      "not sure how they feel but needs support",
}

MOOD_COLORS = {
    "overwhelmed": "#EEEDFE",
    "angry":       "#FCEBEB",
    "sad":         "#E1F5EE",
    "worried":     "#FAEEDA",
    "tired":       "#F1EFE8",
    "unsure":      "#F5F5F5",
}

SOCIAL_STORIES = [
    {
        "title":    "Making a new friend",
        "category": "Friends",
        "emoji":    "🤝",
        "color":    "#E1F5EE",
        "panels": [
            "Sometimes I see someone sitting alone at school.",
            "I can walk up slowly and say: 'Hi, my name is...'",
            "They might smile and tell me their name too.",
            "It is okay if they are shy. I can try again another day.",
            "Making a new friend takes time. That is okay.",
        ]
    },
    {
        "title":    "When I feel really angry",
        "category": "Feelings",
        "emoji":    "🔥",
        "color":    "#FCEBEB",
        "panels": [
            "Sometimes my body feels very hot and tight inside.",
            "That feeling is called anger. It is okay to feel angry.",
            "When I feel angry, I can squeeze my hands tight, then let go.",
            "I can do this again and again until my body feels less tight.",
            "After, I can tell a grown-up what made me feel that way.",
        ]
    },
    {
        "title":    "Taking turns in a game",
        "category": "School",
        "emoji":    "🎮",
        "color":    "#EEEDFE",
        "panels": [
            "When I play a game with others, everyone gets a turn.",
            "Waiting for my turn can feel hard sometimes.",
            "I can count slowly in my head while I wait.",
            "When it is my turn, it feels good.",
            "Taking turns means everyone gets to play.",
        ]
    },
    {
        "title":    "When things change unexpectedly",
        "category": "School",
        "emoji":    "🔄",
        "color":    "#FAEEDA",
        "panels": [
            "Sometimes things do not go the way I expected.",
            "My body might feel upset or confused when this happens.",
            "It is okay to feel that way. Changes can feel hard.",
            "I can take three slow breaths when things change.",
            "A grown-up can help me understand what is happening.",
        ]
    },
]

CALM_TOOLS = [
    {
        "name":  "Breathing bubble",
        "emoji": "🌬️",
        "color": "#E1F5EE",
        "desc":  "4 counts in · 7 hold · 8 out",
        "steps": [
            ("Breathe IN",  4, "Breathe in through your nose. Count slowly: 1... 2... 3... 4..."),
            ("HOLD",        7, "Hold your breath gently. Count: 1... 2... 3... 4... 5... 6... 7..."),
            ("Breathe OUT", 8, "Let all the air out slowly. Count: 1... 2... 3... 4... 5... 6... 7... 8..."),
        ]
    },
    {
        "name":  "5-4-3-2-1 grounding",
        "emoji": "✋",
        "color": "#FAEEDA",
        "desc":  "Notice things around you",
        "steps": [
            ("5 things you can SEE",   None, "Look around slowly. Name 5 things you can see right now."),
            ("4 things you can TOUCH", None, "Feel something near you. Name 4 things you can touch."),
            ("3 things you can HEAR",  None, "Listen carefully. Name 3 things you can hear."),
            ("2 things you can SMELL", None, "Take a gentle sniff. Name 2 things you can smell."),
            ("1 thing you can TASTE",  None, "Notice 1 thing you can taste right now."),
        ]
    },
    {
        "name":  "Squeeze and release",
        "emoji": "✊",
        "color": "#EEEDFE",
        "desc":  "Release tension from your body",
        "steps": [
            ("Squeeze",  5,    "Squeeze both your hands into fists as tight as you can."),
            ("Release",  None, "Let go slowly. Feel your hands relax completely."),
            ("Squeeze",  5,    "Squeeze again — arms, hands, fingers, as tight as you can."),
            ("Release",  None, "Let everything go. Shake your hands gently."),
            ("Rest",     None, "Rest your hands in your lap. Notice how different they feel."),
        ]
    },
]

# ── Styles ────────────────────────────────────────────────────
st.markdown("""
<style>
    .bloom-card {
        background: #EEEDFE;
        border-radius: 16px;
        padding: 20px 24px;
        border: 1px solid #CECBF6;
        margin: 16px 0;
        line-height: 1.7;
        color: #3C3489;
        font-size: 16px;
    }
    .bloom-name {
        font-weight: 600;
        color: #3C3489;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .story-card {
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 10px;
        border: 1px solid #E0E0E0;
    }
    .story-panel {
        background: #F8F8F8;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 8px 0;
        font-size: 15px;
        border-left: 3px solid #8B7FD4;
        line-height: 1.6;
    }
    .calm-card {
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 10px;
        border: 1px solid #E0E0E0;
        cursor: pointer;
    }
    .step-box {
        background: #F0EEF8;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
        text-align: center;
        border: 1px solid #CECBF6;
    }
    .stat-box {
        background: #F8F8F8;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid #E0E0E0;
    }
    .stat-num {
        font-size: 28px;
        font-weight: 600;
        color: #8B7FD4;
    }
    .stat-label {
        font-size: 12px;
        color: #888;
        margin-top: 4px;
    }
    .tip-box {
        background: #FAEEDA;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #FAC775;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state (stores data while app is running) ──────────
if "checkin_log"    not in st.session_state:
    st.session_state.checkin_log    = []
if "tools_used"     not in st.session_state:
    st.session_state.tools_used     = []
if "stories_read"   not in st.session_state:
    st.session_state.stories_read   = []
if "parent_unlocked" not in st.session_state:
    st.session_state.parent_unlocked = False

PARENT_PIN = "1234"

# ── Sidebar navigation ────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌸 CalmCorner")
    st.caption("A safe space for your body and feelings")
    st.divider()
    
    # Add this new section
    st.markdown("**📄 Therapeutic context (optional)**")
    uploaded_pdf = st.file_uploader(
        "Upload a therapy guide PDF to ground Bloom's responses",
        type="pdf",
        help="Bloom will use this document to inform her suggestions"
    )
    if uploaded_pdf:
        if "rag_filename" not in st.session_state or \
           st.session_state.get("rag_filename") != uploaded_pdf.name:
            with st.spinner("Reading document..."):
                st.session_state.rag_context  = extract_pdf_text(uploaded_pdf)
                st.session_state.rag_filename = uploaded_pdf.name
        st.success(f"✓ {uploaded_pdf.name}")
        st.caption(f"{len(st.session_state.rag_context)} characters loaded")
    else:
        if "rag_context" in st.session_state:
            del st.session_state["rag_context"]
            del st.session_state["rag_filename"]
    
    st.divider()
    page = st.radio(
        "Go to",
        ["🏠  Home & check-in",
         "🧘  Calm tools",
         "📖  Social stories",
         "📊  Parent dashboard"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("Companion: Bloom 🌸")

# ═══════════════════════════════════════════════════════════════
# PAGE 1 — HOME & CHECK-IN
# ═══════════════════════════════════════════════════════════════
if page == "🏠  Home & check-in":

    st.markdown("## How does your body feel right now?")
    st.caption("Pick the feeling that fits best — there are no wrong answers.")
    st.write("")

    selected_label = st.radio(
        "mood", list(MOODS.keys()),
        label_visibility="collapsed"
    )

    extra = st.text_input(
        "Want to tell Bloom anything else? (optional)",
        placeholder="e.g. there was a fire drill at school today"
    )

    if st.button("Talk to Bloom 🌸", type="primary", use_container_width=True):
        mood_key     = MOODS[selected_label]
        mood_context = MOOD_CONTEXT[mood_key]
        user_message = f"I am feeling {mood_context}."
        if extra:
            user_message += f" {extra}"
        if "rag_context" in st.session_state:
            user_message += " Please follow the personalisation document carefully."

        # Log the check-in
        st.session_state.checkin_log.append({
            "mood":      mood_key,
            "time":      datetime.datetime.now().strftime("%I:%M %p"),
            "date":      datetime.datetime.now().strftime("%b %d"),
            "extra":     extra,
        })

        with st.spinner("Bloom is thinking..."):
            try:
                # Build active prompt — inject RAG context if a PDF is loaded
                active_prompt = BLOOM_SYSTEM_PROMPT
                if "rag_context" in st.session_state and st.session_state.rag_context:
                    active_prompt = BLOOM_SYSTEM_PROMPT + f"""

                    ════════════════════════════════════════
                    PERSONALISATION DOCUMENT — MANDATORY
                    ════════════════════════════════════════
                    This document contains specific rules for THIS child.
                    You MUST follow every instruction in it.
                    If it says avoid breathing — never suggest breathing.
                    If it lists preferred strategies — only use those.
                    If it lists triggers — reference them by name in your validation.

                    {st.session_state.rag_context}
                    ════════════════════════════════════════
                    END OF PERSONALISATION DOCUMENT
                    ════════════════════════════════════════
                    """
                
                response = co.chat(
                    model="command-a-03-2025",
                    messages=[
                        {"role": "system", "content": active_prompt},
                        {"role": "user",   "content": user_message},
                    ]
                )    
                bloom_reply = response.message.content[0].text
                st.markdown(f"""
                    <div class="bloom-card">
                        <div class="bloom-name">🌸 Bloom says...</div>
                        {bloom_reply}
                    </div>
                """, unsafe_allow_html=True)

                # Suggest a calm tool
                st.info("💡 Want to try a calming tool together? Head to **Calm tools** in the sidebar.")

            except Exception as e:
                st.error(f"Something went wrong: {e}")

    # Investigation expander
    with st.expander("🔬 Investigation — see what was sent to Bloom"):
        if "rag_context" in st.session_state and st.session_state.rag_context:
            st.markdown("**RAG context loaded:**")
            st.caption(f"Document: {st.session_state.get('rag_filename', 'unknown')}")
            with st.expander("Preview loaded document text"):
                st.text(st.session_state.rag_context[:500] + "...")
            st.divider()
        else:
            st.info("No PDF loaded — Bloom is using general knowledge only.")
            st.divider()

        st.markdown("**System prompt:**")
        st.code(BLOOM_SYSTEM_PROMPT, language="text")
        if st.session_state.checkin_log:
            last = st.session_state.checkin_log[-1]
            st.markdown("**Last user message sent:**")
            st.code(
                f"I am feeling {MOOD_CONTEXT[last['mood']]}." +
                (f" {last['extra']}" if last['extra'] else ""),
                language="text"
            )

# ═══════════════════════════════════════════════════════════════
# PAGE 2 — CALM TOOLS
# ═══════════════════════════════════════════════════════════════
elif page == "🧘  Calm tools":

    st.markdown("## Calm down toolbox 🧘")
    st.caption("Pick something that helps your body feel better.")
    st.write("")

    for tool in CALM_TOOLS:
        with st.expander(f"{tool['emoji']}  {tool['name']} — {tool['desc']}"):

            # Log tool use
            if tool['name'] not in st.session_state.tools_used:
                st.session_state.tools_used.append(tool['name'])

            st.markdown(f"""
                <div class="bloom-card">
                    <div class="bloom-name">🌸 Bloom says...</div>
                    Let's do this together. Take your time with each step.
                    I am right here with you. 🌸
                </div>
            """, unsafe_allow_html=True)

            for i, (step_name, duration, instruction) in enumerate(tool['steps']):
                st.markdown(f"""
                    <div class="step-box">
                        <strong>{step_name}</strong><br>
                        {f"<em>{duration} seconds</em><br>" if duration else ""}
                        <span style="font-size:15px">{instruction}</span>
                    </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.success("You checked in with your body. Well done.")

# ═══════════════════════════════════════════════════════════════
# PAGE 3 — SOCIAL STORIES
# ═══════════════════════════════════════════════════════════════
elif page == "📖  Social stories":

    st.markdown("## Social stories 📖")
    st.caption("Short stories to help understand different situations.")
    st.write("")

    categories = ["All"] + list(set(s["category"] for s in SOCIAL_STORIES))
    selected_cat = st.selectbox("Filter by category", categories)

    filtered = SOCIAL_STORIES if selected_cat == "All" \
        else [s for s in SOCIAL_STORIES if s["category"] == selected_cat]

    for story in filtered:
        with st.expander(f"{story['emoji']}  {story['title']}  ·  {story['category']}"):

            if story['title'] not in st.session_state.stories_read:
                st.session_state.stories_read.append(story['title'])

            for i, panel in enumerate(story['panels']):
                st.markdown(f"""
                    <div class="story-panel">
                        {panel}
                    </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.markdown(f"""
                <div class="bloom-card">
                    <div class="bloom-name">🌸 Bloom says...</div>
                    Good job reading that story. I am right here with you. 🌸
                </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 4 — PARENT DASHBOARD
# ═══════════════════════════════════════════════════════════════
elif page == "📊  Parent dashboard":

    st.markdown("## Parent dashboard 📊")

    if not st.session_state.parent_unlocked:
        st.caption("This section is for parents and caregivers only.")
        st.write("")
        pin = st.text_input("Enter parent PIN", type="password",
                            placeholder="Enter 4-digit PIN")
        if st.button("Unlock dashboard", type="primary"):
            if pin == PARENT_PIN:
                st.session_state.parent_unlocked = True
                st.rerun()
            else:
                st.error("Incorrect PIN. Please try again.")
        st.caption("Default PIN for this demo: 1234")

    else:
        st.caption("Welcome. Here is your child's activity summary.")

        if st.button("Lock dashboard"):
            st.session_state.parent_unlocked = False
            st.rerun()

        st.write("")

        # Stats row
        log   = st.session_state.checkin_log
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-num">{len(log)}</div>
                <div class="stat-label">Check-ins</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-num">{len(st.session_state.tools_used)}</div>
                <div class="stat-label">Calm tools used</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="stat-box">
                <div class="stat-num">{len(st.session_state.stories_read)}</div>
                <div class="stat-label">Stories read</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            positive = len([l for l in log
                           if l['mood'] in ['unsure','tired']])
            st.markdown(f"""<div class="stat-box">
                <div class="stat-num">{positive}</div>
                <div class="stat-label">Calm check-ins</div>
            </div>""", unsafe_allow_html=True)

        st.write("")
        st.divider()

        # Check-in log
        st.markdown("### Recent check-ins")
        if not log:
            st.caption("No check-ins yet. Check-ins will appear here after your child uses the app.")
        else:
            for entry in reversed(log[-10:]):
                mood_emoji = [k for k, v in MOODS.items()
                              if v == entry['mood']][0].split()[0]
                st.markdown(f"""
                    <div class="story-panel">
                        {mood_emoji} <strong>{entry['mood'].capitalize()}</strong>
                        &nbsp;·&nbsp; {entry['date']} at {entry['time']}
                        {f"<br><em>{entry['extra']}</em>" if entry['extra'] else ""}
                    </div>
                """, unsafe_allow_html=True)

        st.divider()

        # Bloom's weekly tip (AI generated)
        st.markdown("### Bloom's tip for you 🌸")
        if st.button("Generate tip from Bloom", use_container_width=True):
            if not log:
                st.info("No check-ins yet — Bloom will generate a tip once your child has used the app.")
            else:
                mood_summary = ", ".join([e['mood'] for e in log])
                tip_prompt   = f"""
                    You are Bloom, a gentle AI companion for autistic children.
                    A parent is reading this — not the child.
                    The child's recent check-ins were: {mood_summary}.
                    Write one warm, specific, non-alarming observation for the parent
                    and one simple, practical suggestion they could try this week.
                    Use plain language. Maximum 3 sentences. Be encouraging.
                    Never use clinical terms. Never suggest the child has a disorder.
                """
                with st.spinner("Bloom is thinking..."):
                    try:
                        response = co.chat(
                            model="command-a-03-2025",
                            messages=[
                                {"role": "system", "content": tip_prompt},
                                {"role": "user",   "content": "Generate a tip for this parent."},
                            ]
                        )
                        tip = response.message.content[0].text
                        st.markdown(f"""
                            <div class="tip-box">
                                <strong>🌸 Bloom's tip</strong><br><br>
                                {tip}
                            </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")

        st.divider()
        st.markdown("### Stories read")
        if not st.session_state.stories_read:
            st.caption("No stories read yet.")
        else:
            for s in st.session_state.stories_read:
                st.markdown(f"📖 {s}")

        st.divider()
        st.markdown("### Calm tools used")
        if not st.session_state.tools_used:
            st.caption("No tools used yet.")
        else:
            for t in st.session_state.tools_used:
                st.markdown(f"🧘 {t}")