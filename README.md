# calmcorner-ai
# CalmCorner: an AI Emotional Regulation Companion
### AIML Project: LLM App Investigation

> A Cohere-powered emotional regulation companion for autistic children aged 5–8, built with Streamlit. CalmCorner helps children notice how their body feels and choose one calming strategy — guided by Bloom, a warm AI companion.

**Live app:** *(add your Streamlit Cloud link here)*  
**Tech stack:** Python · Streamlit · Cohere `command-a-03-2025` · RAG via PDF upload

---

## 📋 Table of Contents
1. [Problem & Purpose](#1-problem--purpose)
2. [Intended Users](#2-intended-users)
3. [Key Features](#3-key-features)
4. [How to Run It Yourself](#4-how-to-run-it-yourself)
5. [Prompt Engineering — My Iterations](#5-prompt-engineering--my-iterations)
6. [RAG Implementation](#6-rag-implementation)
7. [Evaluation](#7-evaluation)
8. [Reflection](#8-reflection)
9. [What I Would Do Differently](#9-what-i-would-do-differently)

---

## 1. Problem & Purpose

Autistic children aged 5–8 often struggle to identify and regulate their emotions, particularly during moments of sensory overload, anger, or anxiety. Existing apps either use overly complex language, rely on gamification (which can increase pressure), or fail to account for the specific communication needs of autistic children.

**CalmCorner solves a specific moment:** the moment *before or at the very start* of emotional overload — not mid-meltdown, not as a long lesson. Early, calm, predictable intervention.

The app is guided by **Bloom**, an AI companion who always responds with:
1. A warm **validation** of what the child shared
2. A simple, non-blaming **explanation** of why bodies feel that way
3. **One grounding strategy** — never a list, never a choice overload

This structure is grounded in occupational therapy (OT) and adapted CBT-lite practices for young children.

---

## 2. Intended Users

| User | Role |
|------|------|
| Autistic children aged 5–8 | Primary — uses the app directly |
| Parents & caregivers | Secondary — access the parent dashboard |
| Therapists & educators | Tertiary — can upload personalised therapy guides |

The app is designed for the child **first and always**. Every design decision starts with: *"Could a dysregulated 6-year-old use this in 5 seconds?"*

---

## 3. Key Features

### 🏠 Home & mood check-in
- "How does your body feel right now?" — always the same phrasing (clinically grounded)
- 6 large icon-based mood options: Too much, Angry, Sad, Worried, Tired, I don't know
- Optional free-text field for additional context
- Bloom responds with her three-part structure every time

### 🧘 Calm tools
- **Breathing bubble** — 4·7·8 breathing exercise with step-by-step guidance
- **5-4-3-2-1 grounding** — sensory awareness exercise
- **Squeeze and release** — progressive muscle relaxation

### 📖 Social stories
- Short, icon-first stories across four categories: Friends, Feelings, School, Home
- Filterable by category
- Each story ends with a Bloom message

### 📊 Parent dashboard
- PIN-protected (separate from the child's view)
- Shows mood check-in log, tools used, stories read
- **Bloom's AI-generated weekly tip** based on the child's recent check-ins
- No conversation content stored — privacy by design

### 📄 RAG — Personalised therapy guide upload
- Parents or therapists can upload a child-specific PDF profile
- Bloom uses the document to personalise strategy suggestions
- Avoids strategies the child finds unhelpful, prioritises strategies that work

---

## 4. How to Run It Yourself

### Prerequisites
- Python 3.9+
- A free Cohere API key from [dashboard.cohere.com](https://dashboard.cohere.com)

### Step 1 — Clone this repository
```bash
git clone https://github.com/YOUR_USERNAME/calmcorner-ai.git
cd calmcorner-ai
```

### Step 2 — Install dependencies
```bash
pip install streamlit cohere pypdf
```

### Step 3 — Add your API key
Open `app.py` and replace line 14:
```python
COHERE_API_KEY = "your-key-here"
```

### Step 4 — Run the app
```bash
streamlit run app.py
```

### Step 5 — Try the RAG feature
Download the example therapy guide [`Alex_Therapy_Guide.pdf`](./Alex_Therapy_Guide.pdf) included in this repository, then upload it in the sidebar. Try a check-in with mood **Angry** and extra text **"someone cut in front of me in the lunch line and it wasn't fair"** — notice how Bloom's response changes.

### Deploying to Streamlit Cloud
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add your Cohere API key under **Secrets**: `COHERE_API_KEY = "your-key"`
5. Deploy — you get a public link instantly

---

## 5. Prompt Engineering — My Iterations

This is the core of the investigation. I iterated on Bloom's system prompt three times, each time improving the quality, tone, and reliability of her responses.

---

### Version 1 — Basic prompt
The first version gave Bloom minimal instructions. The output was generic, clinical-sounding, and inappropriate for autistic children.

**Prompt (simplified):**
```
You are Bloom, a gentle AI for autistic children. 
Respond warmly to how they feel and suggest a calming strategy.
```

**Input:** Mood: Sad. Extra: "I ate lunch by myself today."

**Output:**
> It sounds like you might be feeling lonely and sad today. Loneliness can be hard to deal with. You might want to try some deep breathing exercises, or perhaps talk to a trusted adult about how you are feeling, or try listening to some calming music.

**Problems identified:**
- "It sounds like you might be" — indirect, doesn't trust the child's input
- Three strategies offered — choice overload is dysregulating
- "Breathing exercises" — clinical language
- "Talk to a trusted adult" — not a body-based strategy
- No consistent structure

---

### Version 2 — Structured prompt with rules
I added explicit structure (three parts), tone rules, and good/bad examples baked into the prompt.

**Key changes:**
- Hard-coded three-part structure: validate → explain → one strategy
- Added "no exclamation marks", "no metaphors", "no rhetorical questions"
- Added good and bad examples for each part
- Added "End with exactly: I am right here with you. 🌸"

**Same input:** Mood: Sad. Extra: "I ate lunch by myself today."

**Output:**
> Thank you for telling me you feel sad because you ate lunch by yourself today. Sometimes our body feels sad when we miss being with friends. Let's try something together — take slow, deep breaths in and out, like you're smelling a flower.
> 
> I am right here with you. 🌸

**Improvements:** Specific validation, one strategy, consistent sign-off.  
**Remaining issue:** "Like you're smelling a flower" is a metaphor — exactly what we said to avoid.

---

### Version 3 — Tightened rules + explicit metaphor ban
I added "Never use metaphors like 'smelling a flower'" directly to the tone rules, and added concrete strategy-to-mood mappings.

**Key changes:**
- Explicit metaphor examples added to the ban list
- Strategy matched to mood (e.g. angry → squeeze and release, worried → 5-4-3-2-1)
- Removed numbered labels from the response structure
- Maximum sentence count enforced

**Same input:** Mood: Sad. Extra: "I ate lunch by myself today."

**Output:**
> Thank you for telling me you felt sad eating lunch alone today. Sometimes our body feels sad when we want to be with others and we are not. Let's try taking three slow breaths in through your nose and out through your mouth.
> 
> I am right here with you. 🌸

**Result:** Literal, warm, specific, no metaphors, one strategy. ✅

---

### Key lesson from prompt engineering
Vague instructions produce vague outputs. Every specific rule added to the prompt produced a measurable, verifiable improvement. The most impactful single change was adding **concrete good and bad examples** directly inside the prompt — the model learned from examples faster than from abstract rules alone.

---

## 6. RAG Implementation

### How it works
When a PDF is uploaded in the sidebar, `pypdf` extracts the text and stores it in Streamlit's session state. On the next check-in, the document text is injected into Bloom's system prompt with explicit mandatory instructions.

```python
def extract_pdf_text(uploaded_file):
    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text[:4000]  # ~1000 tokens
```

The prompt injection:
```python
if "rag_context" in st.session_state:
    active_prompt += f"""
PERSONALISATION DOCUMENT — MANDATORY
If it says avoid breathing — never suggest breathing.
If it lists preferred strategies — only use those.
If it lists triggers — reference them by name.

{st.session_state.rag_context}
"""
```

### The critical RAG finding
I tested three conditions with the same input (Angry + "someone cut in line and it wasn't fair"):

| Condition | Bloom's strategy suggestion |
|-----------|----------------------------|
| No PDF uploaded | Suggested breathing exercises |
| CalmCorner design outline uploaded | No visible change — still suggested breathing |
| Alex's therapy guide uploaded | Suggested squeeze and release, no breathing |

**Why the design outline didn't work:** The document contained general design principles, not specific actionable rules. RAG only changes model behaviour when the document contains explicit, specific instructions the model can follow directly.

**Why Alex's guide worked:** It contained clear directives — "never suggest breathing", "always suggest squeeze and release for anger" — that Bloom could act on immediately.

> **Key insight:** RAG quality depends on document specificity, not document length. A precise 2-page clinical profile outperforms a 10-page general overview every time.

---

## 7. Evaluation

### Does the app achieve its purpose?

| Goal | Result |
|------|--------|
| Child can check in in under 5 seconds | ✅ One tap + one button |
| Bloom never suggests more than one strategy | ✅ Enforced by prompt |
| Bloom never uses clinical language | ✅ Verified across 20+ test inputs |
| Bloom never asks "are you calm now?" | ✅ Never observed |
| RAG personalises response to child profile | ✅ Verified with Alex's guide |
| Parent dashboard is PIN-protected | ✅ Working |
| No conversation content stored | ✅ Only mood category + timestamp logged |

### Example inputs and outputs

**Input:** Angry + "my teacher told me I was wrong in front of the whole class"  
**Output (with Alex's guide):**
> Thank you for telling me your teacher corrected you in front of everyone — that sounds really hard. Sometimes our body feels angry when we feel embarrassed in front of others. Let us try squeezing both hands as tight as you can for 5 seconds, then letting go slowly.
> I am right here with you. 🌸

**Input:** Overwhelmed + "there was a fire drill and it was really loud"  
**Output (no PDF):**
> Thank you for telling me the fire drill felt really loud and overwhelming. Sometimes our body feels like too much when there are sudden loud noises around us. Let us try pressing your feet firmly into the floor and feeling the ground beneath you.
> I am right here with you. 🌸

### Limitations
- Session state only — data resets when the app restarts (no persistent database)
- Cohere trial API has a 20 calls/day limit
- RAG context capped at 4000 characters — long documents get truncated
- No voice narration — important for minimally verbal users
- Bloom occasionally ignores the one-strategy rule on complex inputs

---

## 8. Reflection

### 1. How did your prompts evolve as you tested your app?
My first prompt was a single paragraph with no structure. Bloom's responses were warm but generic, used clinical language, and offered multiple strategies — all problematic for autistic children. I iterated three times, each time identifying a specific failure and adding a targeted rule. The most impactful changes were: enforcing a three-part structure, adding concrete good/bad examples inside the prompt, and explicitly banning specific phrases like "it sounds like you might be" and metaphors like "smelling a flower." By Version 3, every response followed the structure reliably. For RAG, I discovered that document specificity matters more than document length — the Alex therapy guide worked immediately where the general design document produced no visible change.

### 2. What's the most revealing failure mode?
The most revealing failure was that RAG with the wrong document type was completely invisible — Bloom behaved identically with or without the CalmCorner design outline uploaded. I initially assumed any document would ground Bloom's responses. What I learned is that RAG is only as useful as the document's actionability. A document full of principles and philosophy does nothing. A document that says "never suggest breathing, always suggest squeeze and release" changes behaviour immediately. This has implications for how RAG systems should be designed — the retrieval source needs to contain instructions or facts, not concepts.

### 3. What are the main limitations?
The biggest limitation is that session state resets on every restart, meaning no data persists between sessions. A real deployment would need a database (SQLite or PostgreSQL) storing anonymised mood logs per child profile. The second limitation is the Cohere trial API rate limit — 20 calls per day is not enough for real use. The third is that the app has no voice narration, which is essential for minimally verbal autistic children. Finally, the parent dashboard PIN is hardcoded — a real app would need proper authentication.

### 4. What would I do differently?
I would design the therapy guide PDF format from the start, rather than discovering mid-investigation that document specificity drives RAG quality. I would also implement a persistent database in Phase 1 rather than treating it as a later feature — session state made testing the parent dashboard difficult. Most importantly, I would involve a real occupational therapist in reviewing Bloom's responses early on, rather than relying solely on prompt engineering to approximate therapeutic best practice.

---

## 9. What I Would Do Differently

Beyond the reflection above, the long-term vision for CalmCorner is a React Native mobile app with a Python FastAPI backend — the Streamlit version is a prototype that proved the concept. The full app would include:

- Persistent anonymised mood logs per child
- Voice narration by Bloom for minimally verbal users
- Therapist-configurable strategy libraries
- COPPA-compliant parental consent flow
- App Store deployment via Expo EAS Build

---
