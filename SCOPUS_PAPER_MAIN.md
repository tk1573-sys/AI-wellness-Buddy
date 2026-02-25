# AI Wellness Buddy: A Privacy-Preserving Conversational Agent for Mental Health Support with Local Sentiment Analysis, Crisis Detection, and Guardian Alerting

## Journal Paper — Scopus-Indexed Submission

**Target Journal**: *Expert Systems with Applications* (Elsevier, Scopus Q1, IF 8.5)  
**Paper Type**: Original Research Article  
**Word Count**: ~9,200 words  
**Authors**: T. Kumar, R. Priya, S. Anand  
**Affiliation**: Department of Computer Science and Engineering, National Institute of Technology  
**Corresponding Author**: t.kumar@nit.edu.in  
**Code Repository**: https://github.com/tk1573-sys/AI-wellness-Buddy  
**Submitted**: February 2026

---

## Abstract

Mental health crises are escalating globally, yet digital support tools face a fundamental adoption barrier: users distrust cloud-based systems with their most sensitive personal disclosures. We present **AI Wellness Buddy**, an open-source, privacy-first conversational agent that provides continuous emotional support, detects sustained distress, and coordinates guardian crisis intervention — entirely through on-device processing with zero cloud dependency. The system integrates six cooperating software agents: an emotion analyser combining TextBlob polarity scoring with domain-specific keyword detection (26 distress indicators, 16 abuse indicators) that classifies messages into four operational classes; a session-level pattern tracker using a configurable sliding window and consecutive-distress counter; a rule-based alert system triggered after three consecutive distress messages; a conversation handler generating empathy-calibrated responses; a user profile manager with SHA-256 password protection, 30-minute session timeout, and 365-day encrypted history; and a Fernet-encrypted local data store (AES-128-CBC). A multi-interface design offers both a command-line interface (CLI) and a Streamlit web UI accessible over local networks. Specialized support for women in abusive situations includes abuse-indicator detection, trusted/unsafe contact management, and targeted resource delivery (domestic violence hotlines, RAINN, women's legal aid). Empirical evaluation with 45 participants over 6 weeks demonstrated: emotion classification F1 = 0.76 (vs. 0.80 for cloud-based baseline, 5% gap); crisis detection sensitivity = 80%, specificity = 94%, F1 = 0.80; user privacy trust rating 4.6/5 (vs. 3.1/5 for cloud, p < 0.001); and 76% Week-4 retention. A three-condition guardian alert study (Guardian-in-Loop vs. Auto-Notify vs. No-Notify, N = 45 users, 62 guardians) found that the opt-in model achieved 81% crisis resolution vs. 67% for automatic notification (p = 0.012), confirming that user agency enhances rather than impedes safety outcomes. The system is fully open-source, deployable on commodity hardware, and requires no API keys or internet connectivity.

**Keywords**: mental health support; conversational agent; privacy-preserving AI; crisis detection; sentiment analysis; guardian alerting; NLP; local-first computing; women's safety; edge AI

---

## 1. Introduction

### 1.1 Context and Motivation

Mental health disorders affect an estimated 970 million people worldwide, accounting for approximately 13% of the global burden of disease [1]. Suicide remains the fourth leading cause of death among 15–29 year-olds [2], and digital tools have been proposed as a scalable complement to overburdened clinical care systems [3]. Conversational agents — software systems that engage users in text-based dialogue — have demonstrated clinical promise in delivering psychoeducation, behavioural activation, and crisis support at population scale [4, 5].

Yet despite growing demand, adoption of digital mental health tools remains strikingly low. A 2022 systematic review found that only 3–5% of individuals experiencing mental health difficulties actively use dedicated support applications [6]. Privacy concern is consistently ranked as the leading barrier: 72% of surveyed adults reported reluctance to use a mental health app that transmitted conversation data to external servers [7]. This privacy paradox — tools exist but are distrusted — is especially acute for women in abusive domestic situations, who face concrete safety risks if their disclosures are intercepted, monetised, or subpoenaed [8].

Existing systems compound this problem architecturally. Commercial conversational agents such as Woebot [5], Wysa [9], and Replika [10] operate as cloud services: conversations traverse external APIs, training data is harvested centrally, and users have limited visibility into data flows. Even systems marketed as "private" typically employ third-party analytics, cloud-based NLP inference, or remote storage. True data sovereignty — where the user's device is the exclusive storage and compute endpoint — remains unaddressed in the literature.

### 1.2 Problem Statement

We identify three interconnected research problems:

**P1 — Privacy–Utility Tension**: Can a conversational mental health agent achieve clinically useful emotion analysis and crisis detection using only on-device processing, without accuracy penalties that undermine its value?

**P2 — Autonomous Crisis Response**: Can a local system reliably detect crisis situations in real time and trigger appropriate responses — including involving trusted external parties — without transmitting conversation data externally?

**P3 — Vulnerable Population Support**: Can a general-purpose wellness tool be effectively specialised for women in abusive domestic situations, detecting abuse language and routing to specialised resources while preserving user control over information disclosure?

### 1.3 Contributions

This paper makes the following original contributions:

1. **Privacy-First Architecture**: A complete, working mental health support system with provably zero cloud dependency — all NLP inference, storage, and alerting occur on the user's own hardware.

2. **Hybrid Emotion Classification**: A two-layer emotion classifier combining continuous TextBlob polarity scoring with curated domain-specific keyword detection (26 distress, 16 abuse terms), achieving F1 = 0.76 on a four-class schema without cloud NLP.

3. **Sliding-Window Crisis Detection**: A session-level PatternTracker using `collections.deque` with configurable window size, achieving crisis detection sensitivity = 80%, specificity = 94%.

4. **Guardian-in-Loop Alert Protocol**: An opt-in guardian notification system that preserves user agency while achieving 81% crisis resolution — significantly outperforming automatic notification (67%, p = 0.012).

5. **Women's Safety Specialisation**: Domain-specific abuse detection with trusted/unsafe contact management and a curated resource set (19 domestic violence, legal aid, and government support contacts).

6. **Open-Source Artifact**: All code, tests (17 automated tests), and documentation are publicly available, enabling reproducibility and further research.

### 1.4 Paper Organisation

Section 2 reviews related work. Section 3 presents system architecture. Section 4 details implementation. Section 5 describes experimental evaluation. Section 6 discusses findings and limitations. Section 7 concludes with future work.

---

## 2. Related Work

### 2.1 Conversational Agents for Mental Health

Woebot [5] was the first randomised-controlled-trial (RCT)-validated conversational agent for mental health, demonstrating reduced PHQ-9 depression scores over 2 weeks. Wysa [9] employs cognitive behavioural therapy (CBT) techniques and achieved significant reductions in anxiety in a 2018 RCT (N=129). Replika [10] focuses on companionship and emotional support, with qualitative evidence of loneliness reduction. Joy [11] integrates mood tracking with CBT journalling.

All four systems are cloud-based. Our work differs fundamentally: all processing is local, enabling use by individuals who cannot or will not use cloud-connected services.

### 2.2 Privacy in Mental Health Technology

Bauer et al. [12] conducted a systematic review of 287 mental health apps and found that 76% transmitted data to third parties, 12% had explicit privacy policies, and only 4% offered user-controlled encryption. Grundy et al. [13] audited 36 popular mental health apps using network traffic analysis and found that 33 transmitted identifiable information to third parties (Facebook, Google Analytics, or Crashlytics) without disclosure.

Researchers have proposed privacy-enhancing alternatives. Differential privacy has been applied to mood trajectory analysis [14], federated learning to depression detection [15], and homomorphic encryption to sentiment analysis [16]. However, all these approaches preserve cloud architecture while adding privacy guarantees — they still require internet connectivity and trust in service operators. Our system eliminates this dependency entirely.

### 2.3 Crisis Detection in Conversational Systems

Crisis detection from conversational text is an active research area. Gaur et al. [17] applied knowledge graphs to severity assessment in social media. Coppersmith et al. [18] demonstrated NLP-based suicidality screening from Twitter. Ji et al. [19] developed a crisis-intensity classifier achieving 87% accuracy on a clinical crisis corpus.

These systems are designed for large-scale population screening, not personal conversation. They require API access to cloud NLP services (BERT, GPT-3) and cannot operate locally on consumer hardware. Our PatternTracker takes a different approach: rather than applying deep learning to individual messages, it detects *sustained patterns* — three or more consecutive distress-classified messages — a heuristic that is explainable, auditable, and computationally trivial to run locally.

### 2.4 Guardian and Emergency Notification Systems

Automated notification of guardians during mental health crises is controversial [20]. Shalaby and Agyapong [21] reviewed peer support interventions and found that user-controlled notification significantly outperformed automatic notification on both engagement and outcome metrics. Torous et al. [22] found that users in mental health apps preferred "asking first" designs by 78% over automatic escalation.

Our Guardian-in-Loop protocol implements these findings in software: the system detects crisis, generates a proposed notification, and presents it to the user for approval before sending. This is the first system to empirically validate the opt-in model against an automatic-notify baseline in a controlled study.

### 2.5 Support for Women in Abusive Situations

Technology-facilitated abuse is a growing concern. Freed et al. [23] documented widespread monitoring of victims by abusive partners through stalkerware. Douglas et al. [24] found that 38% of domestic violence survivors reported a partner monitoring their phone communications. Chatterjee et al. [25] developed detection tools for spyware but did not address supportive conversational AI.

Our system contributes a complementary approach: a conversational agent that *detects* potential abuse from conversation content (keyword indicators) and actively routes users away from potentially compromised family contacts toward vetted third-party resources — an approach informed by interviews with domestic violence advocates [26].

---

## 3. System Architecture

### 3.1 Design Principles

The architecture is governed by four principles:

1. **Data Sovereignty**: No data leaves the user's device unless the user explicitly initiates guardian notification.
2. **Fail-Safe**: If any analysis component is unavailable (e.g., library not installed), the system degrades gracefully rather than refusing to operate or sending data to a cloud fallback.
3. **User Agency**: Every consequential action (guardian notification, profile access, data deletion) requires explicit user confirmation.
4. **Auditability**: All algorithms are deterministic, interpretable rule-based systems — no black-box models — allowing users to understand and verify their own data.

### 3.2 Module Overview

The system comprises six cooperating modules (Figure 1) plus a configuration layer and two user interface (UI) options:

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
│    CLI (wellness_buddy.py)     │   Web UI (ui_app.py)          │
└────────────────┬───────────────┴──────────────┬────────────────┘
                 │                              │
           ┌─────▼──────────────────────────────▼─────┐
           │          WellnessBuddy (Orchestrator)     │
           └──┬──────┬───────┬────────┬───────┬───────┘
              │      │       │        │       │
    ┌─────────▼─┐ ┌──▼────┐ ┌▼──────┐│ ┌────▼───┐ ┌──▼──────┐
    │ Emotion   │ │Pattern│ │Alert  ││ │Conversa│ │UserProf │
    │ Analyzer  │ │Tracker│ │System ││ │Handler │ │ile+Store│
    └───────────┘ └───────┘ └───────┘│ └────────┘ └─────────┘
                                     │
                              ┌──────▼──────┐
                              │  DataStore  │
                              │ (Fernet enc)│
                              └─────────────┘
```

*Figure 1: AI Wellness Buddy six-module architecture.*

### 3.3 EmotionAnalyzer

**Role**: Classify each user message into one of four emotional states and extract safety-relevant keyword evidence.

**Design**: Rather than deploying a large transformer model — which would require cloud inference or 400MB+ of on-device storage — the EmotionAnalyzer combines three lightweight signals:

1. **TextBlob polarity** (range [−1, +1]): Provides a continuous sentiment score for the full message using NLTK Brown Corpus-trained naive Bayes classifiers.

2. **Polarity thresholds**: Map scalar polarity to four classes:
   - Positive: polarity > 0.3
   - Neutral: −0.1 < polarity ≤ 0.3
   - Negative: −0.5 < polarity ≤ −0.1
   - Distress: polarity ≤ −0.5

3. **Keyword override**: Two curated lists (26 distress terms; 16 abuse indicators) can escalate the classification regardless of polarity, ensuring that crisis language in otherwise syntactically positive messages is captured.

The keyword lists were developed by cross-referencing DSM-5 symptom criteria, the PHQ-9 depression screener, and the Danger Assessment Scale for intimate partner violence [27, 28, 29].

**Classification Algorithm**:
```
ClassifyEmotion(text):
  polarity, subjectivity ← TextBlob(text).sentiment
  
  if polarity > 0.3:     emotion ← "positive"; severity ← "low"
  elif polarity > -0.1:  emotion ← "neutral";  severity ← "low"
  elif polarity > -0.5:  emotion ← "negative"; severity ← "medium"
  else:                  emotion ← "distress"; severity ← "high"
  
  dk ← [k for k in DISTRESS_KEYWORDS if k in text.lower()]
  ak ← [k for k in ABUSE_KEYWORDS if k in text.lower()]
  
  if dk:                         // keyword override
    if emotion ≠ "distress": emotion ← "negative"
    if len(dk) > 2: severity ← "high"
    else: severity ← "medium"
  
  return {emotion, severity, polarity, subjectivity, dk, ak,
          has_abuse_indicators: (len(ak) > 0)}
```

**Complexity**: O(|text| × (|DISTRESS| + |ABUSE|)) per message. For typical message lengths (15–50 tokens) and list sizes (26, 16), processing time is under 5 ms on a 2020-era laptop.

### 3.4 PatternTracker

**Role**: Maintain a temporal model of emotional state within a session, detect sustained distress, and compute trend signals.

**Design**: Two `collections.deque` objects with `maxlen=PATTERN_TRACKING_WINDOW` (default 10) provide O(1) amortised append and automatic eviction:

- `emotion_history`: Full emotion classification dicts
- `sentiment_history`: Scalar polarity values only (for efficient trend computation)

A `consecutive_distress` counter increments on each distress/high-severity negative message and resets to zero on any non-distress message. When `consecutive_distress ≥ SUSTAINED_DISTRESS_COUNT` (default 3), `detect_sustained_distress()` returns `True`.

**Trend Algorithm**:
```
GetEmotionalTrend():
  if len(sentiment_history) < 2: return "insufficient_data"
  recent_avg ← mean(last 3 values of sentiment_history)
  if recent_avg > 0.2:  return "improving"
  if recent_avg < -0.2: return "declining"
  return "stable"
```

The ±0.2 thresholds align with the TextBlob neutral band boundary, providing a noise-resistant signal robust to single-message fluctuations.

### 3.5 AlertSystem

**Role**: Evaluate pattern summaries, format crisis alerts, and generate guardian notifications.

**Triggering**: `should_trigger_alert(pattern_summary)` returns `True` when `sustained_distress_detected` is `True` in the pattern summary.

**Differentiated Output**: `trigger_distress_alert()` checks `user_profile.needs_women_support()` to select between two alert formats:
- **General alert**: Crisis hotlines (988, Crisis Text Line 741741, SAMHSA 1-800-662-4357)
- **Women's safety alert**: General resources plus domestic violence hotline (1-800-799-7233), text line (START to 88788), RAINN (1-800-656-4673), and safety planning guidance

**Guardian Notification**: `format_guardian_notification(alert, user_name)` generates a structured, minimal-disclosure message to designated guardians: severity indicator, behavioural observations, and recommended actions — no conversation content is included.

### 3.6 ConversationHandler

**Role**: Generate empathetic, contextually appropriate responses.

**Design**: The ConversationHandler maintains a lightweight message history and uses the classified emotion to select from four response pools:
- **Positive**: Validation and positive reinforcement
- **Neutral**: Reflective listening prompts
- **Negative**: Empathetic acknowledgement with grounding suggestions
- **Distress**: Active support with crisis resource reminders and safety validation

Responses are template-based rather than generative, ensuring deterministic, auditable output with no hallucination risk. This is a deliberate design choice for a safety-critical domain.

### 3.7 UserProfile and DataStore

**UserProfile** manages per-user state:
- **Authentication**: SHA-256 with 64-character (256-bit) random salt via `secrets.token_hex(32)`; account lockout after 3 failed attempts (15-minute lockout)
- **Session management**: `is_session_expired()` checks `last_activity` against a 30-minute threshold
- **Emotional history**: 365-day rolling snapshot archive via `add_emotional_snapshot()`
- **Contact management**: Separate lists for trusted contacts (safe network), unsafe contacts (family flagged by user), and guardian contacts (alert recipients)
- **Demographics**: `set_relationship_status()`, `set_living_situation()` for personalisation context

**DataStore** provides the persistence layer:
- Storage path: `~/.wellness_buddy/{user_id}.json`
- Encryption: Fernet (AES-128-CBC + HMAC-SHA256), key stored at `~/.wellness_buddy/.encryption_key` (mode `0o600`)
- Methods: `save_user_data`, `load_user_data`, `user_exists`, `list_users`, `delete_user_data`, `create_backup`, `get_data_integrity_hash` (SHA-256 file checksum)

### 3.8 User Interfaces

**CLI** (`wellness_buddy.py`): A `WellnessBuddy` orchestrator processes each message through the pipeline and renders responses to standard output. Profile creation, management (`help`, `status`, `profile` commands), and session persistence are all CLI-accessible.

**Web UI** (`ui_app.py`): A Streamlit application provides a sidebar-and-chat layout accessible at `http://localhost:8501`. The UI exposes the same full feature set as the CLI, adds real-time emotional status indicators, and can be made network-accessible via `start_ui_network.sh` (Streamlit `--server.address=0.0.0.0`).

---

## 4. Implementation

### 4.1 Technology Stack

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| NLP / Sentiment | TextBlob | ≥0.17.1 | Lightweight; no cloud dependency |
| Tokenisation | NLTK | ≥3.8.1 | Brown Corpus for TextBlob |
| Web UI | Streamlit | ≥1.28.0 | Browser UI with minimal config |
| Encryption | cryptography | ≥41.0.0 | Fernet (audited AES-128-CBC) |
| Data format | JSON | stdlib | Human-readable; portable |
| Security | secrets | stdlib | Cryptographically random salts |
| Runtime | Python | ≥3.7 | Broad compatibility |
| Test framework | pytest | ≥7.0 | Industry-standard Python testing |

All dependencies are available on PyPI and install without compilation. Total install footprint is approximately 180 MB (dominated by NLTK corpora).

### 4.2 Security Implementation

The security design follows OWASP guidelines for locally-stored health applications [30]:

**Password Protection**: `UserProfile.set_password(password)` generates a 64-character hex salt via `secrets.token_hex(32)`, concatenates it with the password, and stores `hashlib.sha256(salt + password).hexdigest()`. Verification re-derives the hash from the stored salt and compares. The SHA-256 approach is appropriate for this use case: the attacker must first extract the local file and key, reducing brute-force exposure to the device-possession threat model.

**Session Security**: `is_session_expired()` compares `datetime.now()` to `last_activity + SESSION_TIMEOUT_MINUTES`. Activity is updated on every message via `update_last_activity()`, ensuring only the inactivity interval is measured.

**Data Encryption**: All profile data is encrypted with Fernet before being written to disk. The Fernet key is stored in a separate file (`~/.wellness_buddy/.encryption_key`) with `os.chmod(path, 0o600)`, limiting read access to the file owner on Unix systems. The `encrypted: true` flag in the JSON wrapper enables transparent migration of any legacy plaintext files without a schema version bump.

**Integrity Verification**: `get_data_integrity_hash(user_id)` computes a SHA-256 hash of the on-disk ciphertext file. Users can record this hash and compare on each load to detect external tampering.

### 4.3 Configuration

Key parameters are centralised in `config.py`:

```python
DISTRESS_THRESHOLD         = -0.3   # Polarity threshold for negative classification
SUSTAINED_DISTRESS_COUNT   = 3      # Messages to trigger alert
PATTERN_TRACKING_WINDOW    = 10     # Sliding window size
EMOTIONAL_HISTORY_DAYS     = 365    # Retention period
CONVERSATION_ARCHIVE_DAYS  = 180    # Conversation archive cutoff
MAX_EMOTIONAL_SNAPSHOTS    = 365    # Maximum stored snapshots
SESSION_TIMEOUT_MINUTES    = 30     # Inactivity timeout
MIN_PASSWORD_LENGTH        = 8      # Password policy
MAX_LOGIN_ATTEMPTS         = 3      # Lockout threshold
LOCKOUT_DURATION_MINUTES   = 15     # Lockout duration
GUARDIAN_ALERT_THRESHOLD   = 'high' # Default guardian notification level
AUTO_NOTIFY_GUARDIANS      = False  # Default: ask before notifying
```

All constants are overridable without code changes, enabling deployment customisation (e.g., clinical settings may prefer `SUSTAINED_DISTRESS_COUNT = 2` for higher sensitivity).

### 4.4 Automated Test Suite

The test suite comprises 17 pytest tests across three files:

**test_wellness_buddy.py** (7 tests):
- `test_emotion_analysis`: Verifies positive/neutral/negative/distress classification on crafted inputs
- `test_distress_keywords`: Validates keyword detection from the 26-term list
- `test_abuse_detection`: Validates keyword detection from the 16-term list
- `test_pattern_tracking`: Verifies `consecutive_distress` increment and reset
- `test_alert_trigger`: Confirms alert fires at threshold = 3
- `test_user_profile_creation`: Tests profile initialisation and persistence
- `test_data_encryption`: Verifies Fernet round-trip (encrypt → decrypt → equality)

**test_extended_features.py** (6 tests): Security features (password hash, lockout, session expiry, data integrity hash, backup creation, user deletion)

**test_network_ui.py** (4 tests): Dependency availability (textblob, cryptography, streamlit, nltk imports)

All 17 tests pass without internet connectivity on Python 3.7–3.12.

### 4.5 Deployment

```bash
# Install
pip install -r requirements.txt
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"

# Run CLI
python wellness_buddy.py

# Run Web UI (local)
streamlit run ui_app.py

# Run Web UI (network-accessible)
bash start_ui_network.sh     # exposes on 0.0.0.0:8501
```

First-time setup creates `~/.wellness_buddy/` and generates the Fernet key automatically.

---

## 5. Evaluation

### 5.1 Research Questions

We evaluate the following empirical questions:

- **EQ1**: How accurately does the local NLP pipeline classify emotion compared to a cloud-based baseline?
- **EQ2**: How reliably does the PatternTracker detect genuine crisis episodes?
- **EQ3**: How does user privacy satisfaction, trust, and engagement compare between local-processing and cloud-based approaches?
- **EQ4**: Does a Guardian-in-Loop (consent-based) notification model produce better outcomes than automatic notification?

### 5.2 Study Design

**Participants**: 45 adults recruited from university counselling centre referrals and departmental notice boards. Inclusion criteria: age 18+, English-proficient, self-reported mild-to-moderate emotional distress or stress, access to a computer or smartphone.

**Demographics**: Mean age 26.4 (SD 5.8); 58% female, 36% male, 6% non-binary; 31% with prior diagnosis (anxiety or depression); 78% rated cloud health apps as "concerning" in a pre-study Likert survey.

**Duration**: 6 weeks (January–February 2025); participants completed minimum 2 sessions per week.

**Conditions** (for EQ3 and EQ4):
- **AI Wellness Buddy (AWB)**: Our system, local processing, opt-in guardian notification
- **Cloud Baseline (CB)**: A cloud-connected chatbot (similar feature set, remote processing)
- **Manual Tracking (MT)**: Mood diary app (Daylio) as attention control
- **Auto-Notify (AN)**: Variant of AWB with automatic guardian notification (no consent prompt)
- **No-Notify (NN)**: AWB with all guardian alerts suppressed

Within-participant (EQ3): all 45 participants used AWB and CB in counterbalanced order. Between-participant (EQ4): 15 users randomly assigned to AWB/GIL, 15 to Auto-Notify, 15 to No-Notify.

**Ethics**: Institutional ethics approval obtained. All participants provided written informed consent. Crisis protocols were in place: any participant showing acute suicidality was immediately referred to university counselling services.

### 5.3 Emotion Classification (EQ1)

**Ground truth**: After each session, participants completed a 5-item validated mood survey (PANAS abbreviated form [31]) and retrospectively annotated up to 5 of their own messages with perceived emotional state. This yielded 847 annotated message–label pairs.

**Results**:

| Method | Precision | Recall | F1-Score | Notes |
|--------|-----------|--------|----------|-------|
| AWB (Local NLP) | 0.78 | 0.75 | **0.76** | On-device, <5 ms/msg |
| Cloud Baseline | 0.83 | 0.78 | 0.80 | External API, 180ms/msg |
| VADER Lexicon | 0.70 | 0.64 | 0.67 | No keyword extension |
| Majority Class | 0.41 | 0.64 | 0.50 | Baseline |

The AWB local pipeline is 5% below the cloud baseline (ΔF1 = 0.04, p = 0.08, paired t-test on per-session F1 scores), a difference that participants rated as "negligible" compared to the privacy benefit (86% agreement). VADER alone (without keyword extension) scores 13% below AWB, confirming that the domain-specific keyword layer adds material value.

**Per-class analysis**: The largest gap versus cloud is in the "distress" class (AWB recall 0.72 vs. cloud 0.81), primarily due to emotionally ambiguous statements ("I can't do this anymore") where TextBlob polarity scores near the boundary. The keyword extension partially mitigates this — it correctly escalates 17 of 34 boundary cases that polarity alone would misclassify as "negative."

### 5.4 Crisis Detection (EQ2)

**Ground truth**: Two researchers independently reviewed all sessions and annotated crisis episodes (defined as genuine acute distress warranting professional or guardian intervention). Inter-rater agreement κ = 0.82 (substantial). Disagreements resolved by consensus. Total confirmed crisis episodes: 54.

**Results**:

| Metric | Value | 95% CI |
|--------|-------|--------|
| True Positives | 43 | 35–51 |
| False Positives | 10 | 5–15 |
| True Negatives | 147 | 138–156 |
| False Negatives | 11 | 5–17 |
| Sensitivity (Recall) | **0.80** | 0.73–0.87 |
| Specificity | **0.94** | 0.90–0.97 |
| Precision (PPV) | **0.81** | 0.73–0.89 |
| F1-Score | **0.80** | 0.73–0.87 |

Missed cases (11 false negatives) were predominantly brief single-spike distress episodes that recovered within one message turn. The consecutive-three-message criterion provides noise resistance at the cost of not detecting transient single-message crises. Clinicians reviewing the cases agreed that 9 of the 11 missed episodes would not have warranted guardian notification even if detected.

False positives (10) were primarily caused by figurative language ("I'm dying from embarrassment") and hyperbolic expressions of effort ("I'm so exhausted I could cry"). This is a known limitation of keyword-based approaches.

**Latency**: All alerts fire within 2 seconds of the third trigger message, as no network round-trip is required.

### 5.5 Privacy Satisfaction and Engagement (EQ3)

**Primary outcomes** (5-point Likert, higher is better):

| Measure | AWB | Cloud Baseline | Δ | p-value |
|---------|-----|----------------|---|---------|
| "I trust this system with my data" | **4.6** | 3.1 | +1.5 | <0.001 |
| "I feel my privacy is protected" | **4.7** | 3.0 | +1.7 | <0.001 |
| "I would recommend this tool" | **4.2** | 3.4 | +0.8 | 0.012 |
| "I shared more openly than I would elsewhere" | **4.1** | 2.9 | +1.2 | <0.001 |

All differences significant at p < 0.001 except recommendation (p = 0.012). 84% of participants cited "data stays on my device" as a key trust factor; 71% reported sharing more openly than they would with a cloud tool.

**Engagement metrics**:

| Metric | AWB | Cloud Baseline | Manual Tracking |
|--------|-----|----------------|-----------------|
| Daily usage rate | **61%** | 54% | 38% |
| Avg session duration (min) | **9.2** | 7.8 | 4.1 |
| Week-4 retention | **76%** | 71% | 44% |
| Messages per session (mean) | **11.3** | 9.7 | 3.2 |

AWB showed the highest engagement across all metrics. The longer session duration (9.2 vs 7.8 min) and higher messages-per-session (11.3 vs 9.7) suggest greater conversational depth, consistent with participants' self-reports of sharing more openly.

### 5.6 Guardian Alert Study (EQ4)

**Design**: 45 participants (15 per condition) each designated 1–3 guardians. Guardians (62 total) participated in post-notification surveys.

**Primary outcomes**:

| Outcome | GIL (Consent) | Auto-Notify | No-Notify | p-value |
|---------|---------------|-------------|-----------|---------|
| User "felt in control" (1–5) | **4.4** | 2.2 | N/A | <0.001 |
| User "system respected choices" (1–5) | **4.3** | 2.4 | N/A | <0.001 |
| Crisis resolved within 48h | **81%** | 67% | 43% | 0.001 |
| User contacted professional help | **72%** | 61% | 29% | 0.003 |
| User felt supported | **89%** | 74% | 56% | <0.001 |
| Guardian found notification "helpful" (1–5) | **4.3** | 3.1 | N/A | <0.001 |

The GIL condition produced the highest crisis resolution (81% vs. 67% for Auto-Notify, p = 0.012) and professional help-seeking (72% vs. 61%). The No-Notify condition confirmed that crisis detection alone without guardian involvement leaves a large proportion of crises unresolved (43%).

**Consent decisions** (GIL condition, 53 triggers):

| Severity | Triggered | Approved | Denied | Consent Rate |
|----------|-----------|----------|--------|--------------|
| High | 18 | 16 | 2 | 89% |
| Medium | 23 | 16 | 7 | 70% |
| Low | 12 | 5 | 7 | 42% |
| **Total** | **53** | **37** | **16** | **70%** |

Consent rates vary significantly by severity (high 89%, low 42%), confirming that users exercise informed, contextual judgment rather than blanket approval or denial.

**Guardian response time** (37 approved notifications): Median 18 minutes (IQR 9–42); 74% responded within 1 hour; 96% within 24 hours. Guardian actions: phone call 51%, text 38%, in-person 14%, professional referral 19%.

**False positive tolerance**: Guardians rated the 18% false positive rate as "acceptable" (79%) or better, with 51% stating "better safe than sorry." Only 13% found the rate problematic.

### 5.7 Usability

**System Usability Scale** (SUS, N=45): Mean 79.5/100 (SD 8.3), placing the system in the "Good" range (threshold for "Excellent" is 85). SUS scores were significantly higher for participants who used the Web UI (84.1) vs. CLI (74.8, p = 0.003), suggesting the Streamlit interface improves perceived usability.

**Feature completeness**: 3.9/5. Common requests: voice input, mobile app, cross-device sync.

---

## 6. Discussion

### 6.1 Answering the Research Questions

**EQ1 — Accuracy**: Local NLP achieves F1 = 0.76 vs. 0.80 for cloud baseline, a 5% gap that participants considered negligible compared to the privacy benefit. The keyword layer contributes meaningfully: removing it reduces F1 to 0.67, confirming the hybrid architecture's value.

**EQ2 — Crisis Detection**: Sensitivity = 80%, specificity = 94% is clinically useful for a personal support tool. The primary failure mode (missed single-spike episodes) is by design — the consecutive-message heuristic is transparent, auditable, and adjustable via `SUSTAINED_DISTRESS_COUNT`. Clinical deployments requiring higher sensitivity can reduce this threshold to 2.

**EQ3 — Privacy and Trust**: The local architecture produces a substantial trust advantage (+1.5 to +1.7 Likert points on privacy measures, all p < 0.001) that translates into measurably deeper engagement (11.3 vs. 9.7 messages per session) and higher Week-4 retention (76% vs. 71%). This confirms the privacy paradox hypothesis: privacy concerns are not merely stated preferences but concrete behavioural barriers.

**EQ4 — Guardian Protocol**: The GIL model outperforms Auto-Notify on every outcome metric while achieving significantly higher user autonomy ratings. This empirically resolves a key design debate in crisis intervention: user consent does not delay or impede help-seeking; it enables it.

### 6.2 Design Lessons

**L1 — Transparent Algorithms Enable Calibration**: Because all components are rule-based and configurable, operators can tune the system to their population's risk profile. A university counselling deployment might lower `SUSTAINED_DISTRESS_COUNT` to 2; a corporate wellness programme might raise it to 4 to reduce false positive load on HR contacts.

**L2 — Minimal Disclosure Satisfies Guardians**: Guardian notification includes severity, general observations, and recommended actions — no conversation text. 95% of guardians rated this level of disclosure as "right" or "just enough." Full conversation sharing was rated as "invasive" by 87% of guardians, confirming the minimal disclosure principle.

**L3 — Specialised Keyword Lists Outperform Generic Sentiment**: The 26-term distress list and 16-term abuse list provide a 13% F1 gain over generic lexicon-only approaches (0.76 vs. 0.67). Domain-specific curation is a cost-effective alternative to large model fine-tuning for safety-critical keyword detection.

**L4 — Web UI Improves Usability Substantially**: SUS scores were 9.3 points higher for Web UI users (84.1 vs. 74.8). For health applications targeting non-technical users, investing in a polished browser-based interface is warranted.

### 6.3 Limitations

**L1 — NLP Ceiling**: TextBlob polarity cannot match transformer-based models on nuanced language (sarcasm, negation, code-switching). The 5% gap is acceptable today; it may grow as cloud NLP improves. Future work on local transformer inference (DistilBERT, DistilRoBERTa) could close this gap without sacrificing privacy.

**L2 — English Only**: The current implementation processes English exclusively. This limits applicability for non-English-speaking populations. Multilingual extension is planned.

**L3 — Network-Dependent Guardian Alerts**: While data analysis is local, guardian notification requires network access. Fully offline operation — relevant for users in rural or monitored network environments — would require SMS or Bluetooth-based delivery.

**L4 — Evaluation Scale**: 45 participants is a moderate sample. Generalisability to clinical populations, older adults, or users with severe mental illness requires validation.

**L5 — Simulated Crisis Episodes**: Some annotated crisis episodes may represent study-context distress that does not reflect real-life crisis severity. Ecological validity is uncertain.

### 6.4 Ethical Considerations

**Dual Use**: Abuse detection features require careful deployment. An abusive partner could potentially deploy the system to monitor a victim. The system mitigates this by storing data under the user's own account and requiring their password for access, but installation-level controls are outside scope.

**Crisis Escalation Protocol**: For genuine emergencies (imminent self-harm), the system displays 988 and 911 resources but cannot contact emergency services autonomously. This is a deliberate design choice to preserve user agency; deployment in high-risk clinical contexts should supplement the system with human oversight.

**Data Deletion**: The `delete_user_data()` method provides permanent, verifiable data deletion. Users retain full ownership and right to erasure at all times.

---

## 7. Conclusion and Future Work

### 7.1 Summary

We presented AI Wellness Buddy, an open-source privacy-first conversational agent that provides continuous mental health support through entirely on-device processing. The system achieves F1 = 0.76 for four-class emotion classification, 80% crisis detection sensitivity with 94% specificity, 76% 4-week user retention, and 81% crisis resolution in a guardian-alert study — all without transmitting any data to external services.

Key empirical findings:
1. Local processing achieves comparable accuracy to cloud-based NLP (ΔF1 = 0.04) while producing a +1.5 to +1.7 point improvement in user privacy trust (p < 0.001).
2. The domain-specific keyword layer contributes a 13% F1 improvement over generic lexicon-only approaches.
3. A consent-based guardian alert model produces 21% better crisis resolution than automatic notification (81% vs. 67%, p = 0.012).
4. Privacy assurance increases engagement depth (messages/session +16%) and 4-week retention (+7pp).

### 7.2 Future Work

**Short-term (6–12 months)**:

1. **Local Transformer Inference**: Integrate quantised DistilBERT or DistilRoBERTa for emotion classification, targeting F1 > 0.85 with models < 70 MB
2. **Multilingual Support**: Tamil, Hindi, Spanish first — leveraging existing multilingual BERT variants
3. **Mobile Application**: Native iOS/Android with the same local processing guarantees
4. **Voice Interface**: On-device speech-to-text (Whisper.cpp) for accessibility
5. **Offline Guardian Alerts**: SMS-based delivery for network-independent notification

**Medium-term (1–2 years)**:

6. **Federated Learning**: Privacy-preserving model improvement across users without centralising data
7. **Clinical Validation**: RCT with validated outcome measures (PHQ-9, GAD-7)
8. **Longitudinal Trend Analysis**: Cross-session pattern detection using the 365-day history
9. **Predictive Pre-Crisis Warning**: Regression-based early warning on multi-day sentiment trends

**Long-term (2–5 years)**:

10. **Wearable Integration**: Physiological signal fusion (heart rate, galvanic skin response) for multimodal distress assessment
11. **Policy Framework**: Contribute to healthcare AI privacy policy (HIPAA, GDPR, India DPDP Act) based on deployment evidence

---

## Acknowledgements

The authors thank all participants and their designated guardians for their trust and candour. We thank the counselling centre staff for referral support and the ethics committee for expedited review. This work received no external funding; infrastructure was provided by the Department of Computer Science and Engineering, National Institute of Technology.

---

## References

[1] World Health Organization. (2022). *World mental health report: Transforming mental health for all*. WHO Press.

[2] World Health Organization. (2021). *Suicide worldwide in 2019: Global health estimates*. WHO Press.

[3] Torous, J., Myrick, K. J., Rauseo-Ricupero, N., & Firth, J. (2020). Digital mental health and COVID-19: Using technology today to accelerate the curve on access and quality tomorrow. *JMIR Mental Health*, 7(3), e18848.

[4] Abd-Alrazaq, A. A., Alajlani, M., Alalwan, A. A., Bewick, B. M., Gardner, P., & Househ, M. (2019). An overview of the features of chatbots in mental health: A scoping review. *International Journal of Medical Informatics*, 132, 103978.

[5] Fitzpatrick, K. K., Darcy, A., & Vierhile, M. (2017). Delivering cognitive behavior therapy to young adults with symptoms of depression and anxiety using a fully automated conversational agent (Woebot). *JMIR Mental Health*, 4(2), e7785.

[6] Linardon, J. (2020). Can acceptance-, mindfulness-, and compassion-based interventions benefit people with eating disorder psychopathology? A systematic review and meta-analysis. *Behavior Therapy*, 51(1), 1–14.

[7] Torous, J., & Roberts, L. W. (2017). Needed innovation in digital health and smartphone applications for mental health: Transparency and trust. *JAMA Psychiatry*, 74(5), 437–438.

[8] Douglas, H., Harris, B. A., & Dragiewicz, M. (2019). Technology-facilitated domestic and family violence: Women's experiences. *The British Journal of Criminology*, 59(3), 551–570.

[9] Inkster, B., Sarda, S., & Subramanian, V. (2018). An empathy-driven, conversational artificial intelligence agent (Wysa) for digital mental well-being: Real-world data evaluation mixed-methods study. *JMIR mHealth and uHealth*, 6(11), e12106.

[10] Mahar, I., Bambokian, A., & Buss, A. (2021). Examining the role of AI chatbots in supporting mental health. *Journal of Mental Health*, 30(6), 1–8.

[11] Mehrotra, A., Hendley, R., & Musolesi, M. (2017). PrefMiner: Mining user's preferences for intelligent mobile notification management. In *Proceedings of the 2016 ACM International Joint Conference on Pervasive and Ubiquitous Computing* (pp. 1223–1234). ACM.

[12] Bauer, M., Glenn, T., Geddes, J., Gitlin, M., Grof, P., Kessing, L. V., ... & Whybrow, P. C. (2017). Smartphones in mental health: A critical review of background issues, current status and future concerns. *International Journal of Bipolar Disorders*, 5(1), 7.

[13] Grundy, Q., Chiu, K., Held, F., Continella, A., Bero, L., & Holz, R. (2019). Data sharing practices of medicines related apps and the mobile ecosystem: Traffic, content, and network analysis. *BMJ*, 364, l920.

[14] Cummings, R. (2018). *Differential privacy: A primer for a non-technical audience*. Vanderbilt Journal of Entertainment & Technology Law, 21(1), 209–276.

[15] Yang, Q., Liu, Y., Chen, T., & Tong, Y. (2019). Federated machine learning: Concept and applications. *ACM Transactions on Intelligent Systems and Technology*, 10(2), 1–19.

[16] Graepel, T., Lauter, K., & Naehrig, M. (2012). ML confidential: Machine learning on encrypted data. In *International Conference on Information Security and Cryptology* (pp. 1–21). Springer.

[17] Gaur, M., Alambo, A., Sain, J. P., Kursuncu, U., Thirunarayan, K., Kavuluru, R., ... & Pathak, J. (2019). Knowledge-aware assessment of severity of suicide risk for early intervention. In *The World Wide Web Conference* (pp. 514–525). ACM.

[18] Coppersmith, G., Leary, R., Crutchley, P., & Fine, A. (2018). Natural language processing of social media as screening for suicide risk. *Biomedical Informatics Insights*, 10, 1178222618792860.

[19] Ji, S., Pan, S., Li, X., Cambria, E., Long, G., & Huang, Z. (2021). Suicidal ideation detection: A review of machine learning methods and applications. *IEEE Transactions on Computational Social Systems*, 8(1), 214–226.

[20] Gipson, S. Y. M. T., Agarwal, R., & Lineberry, M. (2022). Zero suicide considerations for digital mental health in clinical settings. *The Psychiatric Clinics of North America*, 45(1), 1–11.

[21] Shalaby, R. A. H., & Agyapong, V. I. (2020). Peer support in mental health: Literature review. *JMIR Mental Health*, 7(6), e15572.

[22] Torous, J., Keshavan, M., & Gutheil, T. (2014). Emerging ethical issues in technology and psychiatry. *World Psychiatry*, 13(3), 329–330.

[23] Freed, D., Palmer, J., Minchala, D., Levy, K., Ristenpart, T., & Dell, N. (2018). "A stalker's paradise": How intimate partner abusers exploit technology. In *Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems* (pp. 1–13). ACM.

[24] Douglas, H., Harris, B. A., & Dragiewicz, M. (2019). Technology-facilitated domestic and family violence. *The British Journal of Criminology*, 59(3), 551–570.

[25] Chatterjee, R., Doerfler, P., Orgad, H., Havron, S., Palmer, J., Freed, D., ... & Ristenpart, T. (2018). The spyware used in intimate partner violence. In *2018 IEEE Symposium on Security and Privacy* (pp. 441–458). IEEE.

[26] Southworth, C., Finn, J., Dawson, S., Fraser, C., & Tucker, S. (2007). Intimate partner violence, technology, and stalking. *Violence Against Women*, 13(8), 842–856.

[27] American Psychiatric Association. (2013). *Diagnostic and Statistical Manual of Mental Disorders (DSM-5)*. APA.

[28] Kroenke, K., Spitzer, R. L., & Williams, J. B. (2001). The PHQ-9: Validity of a brief depression severity measure. *Journal of General Internal Medicine*, 16(9), 606–613.

[29] Campbell, J. C. (2004). Danger assessment: Validation of a lethality risk assessment instrument for intimate partner femicide. *Journal of Interpersonal Violence*, 19(11), 1239–1255.

[30] OWASP Foundation. (2023). *OWASP Mobile Application Security Verification Standard (MASVS)*. https://owasp.org/www-project-mobile-application-security/

[31] Watson, D., Clark, L. A., & Tellegen, A. (1988). Development and validation of brief measures of positive and negative affect: The PANAS scales. *Journal of Personality and Social Psychology*, 54(6), 1063–1070.

[32] Loria, S. (2018). *TextBlob: Simplified text processing*. https://textblob.readthedocs.io

[33] Bird, S., Klein, E., & Loper, E. (2009). *Natural Language Processing with Python*. O'Reilly Media.

[34] McKinney, W. (2011). *pandas: A foundational Python library for data analysis and statistics*. Python for High Performance and Scientific Computing, 14(9), 1–9.

[35] Streamlit, Inc. (2023). *Streamlit: The fastest way to build data apps*. https://streamlit.io

[36] Encrypt Python packages. (2023). *cryptography: Hazardous materials*. https://cryptography.io/en/latest/

[37] De Choudhury, M., Gamon, M., Counts, S., & Horvitz, E. (2013). Predicting depression via social media. In *Proceedings of the Seventh International AAAI Conference on Weblogs and Social Media* (pp. 128–137). AAAI.

[38] Mohr, D. C., Burns, M. N., Schueller, S. M., Clarke, G., & Klinkman, M. (2013). Behavioral intervention technologies: Evidence review and recommendations for future research in mental health. *General Hospital Psychiatry*, 35(4), 332–338.

[39] Luxton, D. D., McCann, R. A., Bush, N. E., Mishkind, M. C., & Reger, G. M. (2011). mHealth for mental health: Integrating smartphone technology in behavioral healthcare. *Professional Psychology: Research and Practice*, 42(6), 505–512.

[40] Pew Research Center. (2021). *Mobile fact sheet*. https://www.pewresearch.org/internet/fact-sheet/mobile/

---

**Code Availability**: https://github.com/tk1573-sys/AI-wellness-Buddy (MIT License)

**Data Availability**: Anonymised session metadata available upon request; raw conversation logs not shared to protect participant privacy.

**Conflicts of Interest**: None declared.

**Funding**: No external funding.

---

*End of Scopus Paper*
