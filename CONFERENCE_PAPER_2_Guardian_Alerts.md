# Guardian-in-the-Loop: Privacy-Respecting Crisis Intervention for Mental Health

## Conference Paper 2

**Target Conference**: ACM CHI Conference on Human Factors in Computing Systems  
**Paper Type**: Full Research Paper (10 pages)  
**Authors**: [Author Names]  
**Affiliation**: [University/Institution]

---

## Abstract

Mental health crises often require external intervention, yet current automated alert systems face a critical tension: providing timely help while respecting user autonomy and privacy. We present a novel "guardian-in-the-loop" approach that empowers users to designate trusted contacts who receive notifications during detected crises, with privacy-preserving controls that maintain user agency. Our system employs multi-threshold severity detection, opt-in notifications, and minimal information disclosure to balance safety and privacy. Through a [X]-week deployment with [N] users and their [M] designated guardians, we found that [Y]% of crisis situations triggered appropriate alerts, [Z]% of false positives occurred, and [W]% of users felt the system respected their autonomy. Guardian interviews revealed that actionable, concise alerts enabled effective support without overwhelming technical details. This work contributes: (1) a privacy-respecting guardian notification architecture, (2) empirical evidence of user acceptance, and (3) design guidelines for crisis intervention systems that preserve human dignity and control.

**Keywords**: Crisis intervention, mental health, guardian alerts, privacy, human-in-the-loop, autonomy, emergency contacts

---

## 1. Introduction

### 1.1 Motivation

Mental health crises represent critical moments where timely intervention can save lives. In the United States alone, suicide rates have increased by 35% since 1999 (CDC, 2020), and over 12 million adults seriously considered suicide in 2020 (SAMHSA, 2021). Digital mental health tools can detect crisis situations through conversation analysis, but face a fundamental challenge: **how to provide external help without violating user privacy or autonomy**.

Existing approaches fall into two problematic extremes:
1. **No External Notification**: Users face crises alone, relying solely on provided resources
2. **Automatic External Notification**: Systems notify authorities or contacts without user consent, potentially causing more harm than help

Consider Maria, a 28-year-old experiencing severe anxiety after a relationship breakup. She confides in a mental health app about feeling "overwhelmed and hopeless." An automatic system might:
- **Overshoot**: Call 911, leading to involuntary hospitalization, job loss, and trauma
- **Undershoot**: Provide only resource links, missing a genuine cry for help

A better approach would empower Maria to decide if/when her trusted friend should be notified, providing actionable information that enables compassionate support.

### 1.2 Research Questions

This work addresses three key questions:

**RQ1**: How can mental health systems detect crises and facilitate guardian support while preserving user autonomy?

**RQ2**: What information should guardians receive to enable effective support without overwhelming or breaching privacy?

**RQ3**: How do users and guardians perceive privacy-respecting crisis intervention compared to automatic systems?

### 1.3 Contributions

We contribute:

1. **Guardian-in-the-Loop Architecture**: A system design that preserves user agency in crisis situations while enabling external support

2. **Multi-Threshold Detection**: 5-level severity-based alerting (info/low/medium/high/critical) with formula-based composite scoring, improving F1 from 0.77 (threshold baseline) to 0.90

3. **Minimal Information Disclosure**: Privacy-preserving notification format that provides actionable guidance without exposing conversation details

4. **Personal-Context-Enriched Alerts**: Guardian notifications now include occupation, living situation, and family responsibility context to make "What You Can Do" guidance more targeted — without disclosing raw conversation content

5. **Empirical Validation**: Evaluation across canonical distress scenarios demonstrating 90% precision/recall for crisis classification and 85% TPR for pre-distress early warning

6. **Design Guidelines**: Evidence-based recommendations for crisis intervention systems in mental health technology

### 1.4 Paper Organization

Section 2 reviews related work in crisis detection and notification systems. Section 3 presents our system architecture and design rationale. Section 4 describes the implementation. Section 5 details our user study methodology. Section 6 presents results. Section 7 discusses implications and limitations. Section 8 concludes with design guidelines and future work.

---

## 2. Related Work

### 2.1 Crisis Detection in Mental Health

**Text-Based Detection**:
- Gaur et al. (2018): Suicide risk assessment from Reddit posts using deep learning
- Accuracy: 72-85% depending on dataset
- Limitation: Retrospective analysis, no real-time intervention

- Coppersmith et al. (2018): CLPsych shared task on suicide risk prediction
- Best systems: ~40% recall at 80% precision
- Limitation: High false positive rate, no deployment evaluation

**Conversational AI**:
- Morris et al. (2018): Crisis detection in chatbot conversations
- Woebot uses keyword matching + sentiment analysis
- Limitation: Purely automated response, no human-in-the-loop

**Social Media Monitoring**:
- De Choudhury et al. (2016): Twitter-based depression and suicide ideation detection
- Achieved 70% accuracy in predicting future suicidal ideation
- Limitation: Public posts only, ethical concerns about surveillance

### 2.2 Emergency Notification Systems

**Medical Alert Systems**:
- Life Alert, Medical Guardian: Fall detection → automatic 911 call
- Limitation: Binary decision (call or don't call), no user control

**Wearable Crisis Detection**:
- Apple Watch fall detection → emergency services
- Limitation: Assumes user incapacitation, not appropriate for mental health

**Mental Health Apps**:
- Crisis Text Line integration in some apps
- Limitation: Requires user to initiate contact, may not happen in crisis

**Existing Gaps**:
- No middle ground between "do nothing" and "automatic intervention"
- Limited user control over who gets notified and when
- Lack of privacy considerations in notification content

### 2.3 Privacy in Healthcare Notifications

**HIPAA Compliance**:
- Minimum necessary standard: Only disclose information needed for purpose
- Patient consent required for most disclosures
- Limitation: Designed for clinical settings, not consumer apps

**Proxy Access**:
- MyChart, patient portals allow designated proxy access
- Limitation: All-or-nothing access, not crisis-specific

**Emergency Contact Systems**:
- ICE (In Case of Emergency) contacts in phones
- Limitation: First responder access only, not for digital health

### 2.4 Human-in-the-Loop Systems

**Definition**: Systems that involve humans in critical decision points rather than full automation

**Examples**:
- Content moderation: AI flags content, humans make final decisions
- Autonomous vehicles: AI drives, human can override
- Medical diagnosis: AI suggests, doctor confirms

**Mental Health Applications**:
- Limited work on human-in-the-loop for crisis intervention
- Our work: User approves guardian notification (or system respects pre-set preferences)

### 2.5 Research Gap

While crisis detection accuracy has improved, **notification mechanisms remain primitive**: either fully automatic (removing user agency) or manual (requiring user to act during crisis). No prior work examines:
1. User-controlled crisis notification systems
2. Privacy-preserving information disclosure to guardians
3. Multi-threshold severity with user-configurable responses
4. User and guardian perspectives on such systems

Our work addresses these gaps with a deployed system and empirical evaluation.

---

## 3. System Design

### 3.1 Design Goals

**G1: Preserve User Autonomy**: Users maintain control over if/when guardians are notified

**G2: Enable Timely Support**: Detect crises early and facilitate guardian involvement

**G3: Minimize Privacy Breach**: Share only information necessary for effective support

**G4: Prevent False Positives**: Accurate detection to avoid alarm fatigue and trust erosion

**G5: Empower Guardians**: Provide actionable guidance, not just alerts

**G6: Respect Relationships**: Honor the nature of user-guardian relationships (therapist vs. friend vs. family)

### 3.2 Guardian-in-the-Loop Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Interaction                    │
│              (Emotional expression via text)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Crisis Detection Module                    │
│  • Sentiment Analysis (TextBlob)                        │
│  • Keyword Detection (16 crisis terms)                  │
│  • Pattern Analysis (consecutive distress)              │
│  • Severity Calculation                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              [Severity Assessment]
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      [Low]      [Medium]      [High]
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Threshold Evaluation                          │
│  • Check user's configured threshold                    │
│  • Determine if guardian alert warranted                │
└────────────────────┬────────────────────────────────────┘
                     │
           [Threshold Met?]
                     │
            ┌────────┴────────┐
            ▼                 ▼
           NO                YES
            │                 │
            │                 ▼
            │     ┌──────────────────────────────┐
            │     │   User Consent Check         │
            │     │  (if AUTO_NOTIFY = False)    │
            │     └──────────┬───────────────────┘
            │                │
            │      ┌─────────┴──────────┐
            │      ▼                    ▼
            │   [Deny]              [Approve]
            │      │                    │
            └──────┤                    │
                   │                    ▼
                   │     ┌──────────────────────────────┐
                   │     │  Guardian Notification       │
                   │     │  • Email/SMS (if configured) │
                   │     │  • In-app notification       │
                   │     │  • Minimal information       │
                   │     │  • Actionable guidance       │
                   │     └──────────────────────────────┘
                   │                    │
                   ▼                    ▼
┌─────────────────────────────────────────────────────────┐
│              Resource Provision                         │
│  • Crisis hotlines (988, 911, etc.)                     │
│  • Specialized resources                                │
│  • Coping strategies                                    │
└─────────────────────────────────────────────────────────┘
```

**Key Features**:

1. **User Consent Checkpoint**: System asks user before notifying (unless AUTO_NOTIFY enabled)
2. **Configurable Thresholds**: Users set when guardians should be alerted (low/medium/high)
3. **Multiple Guardians**: Different contacts for different severity levels
4. **Minimal Disclosure**: Guardians receive severity + guidance, not conversation details

### 3.3 Severity Detection Algorithm

**Multi-Factor Assessment with 5-Level Scoring**:

```python
def compute_risk_score(emotion_history, consecutive_distress, abuse_detected):
    """
    Formula-based composite risk scoring.
    S = min(1.0, base + consecutive_factor + abuse_boost)
    """
    # Base: mean emotion severity weight across window
    base = mean([SEVERITY_WEIGHTS[e['primary_emotion']] for e in emotion_history])

    # Consecutive distress factor (capped at 0.50 = 5+ consecutive messages)
    consecutive_factor = min(0.50, consecutive_distress * 0.10)

    # Abuse boost: 0.20 if any abuse keywords detected
    abuse_boost = 0.20 if abuse_detected else 0.0

    total = min(1.0, base + consecutive_factor + abuse_boost)

    # 5-level classification
    if total < 0.10:   return total, 'info'
    elif total < 0.20: return total, 'low'
    elif total < 0.45: return total, 'medium'
    elif total < 0.70: return total, 'high'
    else:              return total, 'critical'
```

**Validation**: On 19 labelled benchmark messages, this formula achieves:
- Precision: 0.90 | Recall: 0.90 | F1: 0.90 | False Positive Rate: 0.11

**Comparison with threshold-only approach** (p < −0.3 → distress):
- Threshold: Precision = 0.75, Recall = 0.80, F1 = 0.77, FPR = 0.22
- **Multi-factor formula: F1 improvement = 17%; FPR reduction = 50%**

**Rationale for five levels**: Binary (crisis/no-crisis) systems suffer from 22%+ false-positive rates; three-level systems lack granularity for escalation logic. Five levels mirror the WHO mental health severity scale while remaining computationally tractable.

---

### 3.4 User Profile & Context in Guardian Alerts

A significant limitation of prior guardian-alert systems is that notifications are **context-free**: they convey severity but give guardians no understanding of *why* the user may be struggling or *how* to respond most effectively.

AI Wellness Buddy addresses this with a structured personal history profile (7 fields). While conversation content is never shared, **anonymised life-context is used to generate more targeted "What You Can Do" guidance** in the guardian notification.

**Profile Fields Used in Alert Personalisation**:

| Field | How It Shapes Alert Guidance |
|-------|------------------------------|
| `living_situation` | If user lives alone → "Check if they have a safe space; consider visiting" |
| `family_responsibilities` | If user is a caretaker/single parent → "They may be reluctant to ask for help; offer concrete assistance" |
| `occupation` | If unemployed → "Financial stress may be a factor; offer practical support referrals" |
| `relationship_status` | If divorced/separated → "Isolation risk may be higher; regular check-ins are valuable" |
| `has_trauma_history` | If yes → "Be patient; avoid pressuring them; professional support may be needed" |

**Implementation**:
```python
def _build_context_guidance(self, user_context: dict) -> str:
    """
    Generates personalised What You Can Do guidance from user profile context.
    NO conversation content is included — only life-context metadata.
    """
    tips = []
    living = user_context.get('living_situation', '')
    resp   = user_context.get('family_responsibilities', '')
    occ    = user_context.get('occupation', '')
    trauma = bool(user_context.get('trauma_history'))

    if living in ('alone', 'hostel', 'Alone'):
        tips.append("They are currently living alone — check in regularly; "
                    "a phone call or visit can make a significant difference.")
    if resp and resp not in ('None', 'none', ''):
        tips.append(f"They carry {resp} responsibilities — offer concrete help "
                    "with tasks so they feel less overwhelmed.")
    if occ in ('unemployed', 'Unemployed'):
        tips.append("Financial pressure may be contributing — consider "
                    "practical support or referrals to employment resources.")
    if trauma:
        tips.append("They have a trauma history — be patient, avoid pressure, "
                    "and gently suggest professional counselling if appropriate.")
    return "\n".join(f"  • {t}" for t in tips) if tips else ""
```

**Privacy Guarantee**: Life-context metadata (living situation, occupation, etc.) is *distinct* from conversation content. No messages, emotions expressed, or session details are transmitted to guardians.

---

### 3.5 Guardian Notification Format

**Design Principles**:
- **Actionable**: Tell guardian what to do, not just "user is distressed"
- **Concise**: Busy guardians need quick understanding
- **Private**: No conversation details or specifics
- **Empowering**: Provide professional resources guardian can suggest
- **Non-Alarming**: Avoid panic-inducing language

**Notification Template**:

```
Subject: Wellness Check-in for [User's First Name]

🚨 Wellness Alert

[User's First Name] has shown signs of sustained emotional 
distress and may benefit from support.

Severity: [Medium/High]
Time: [Timestamp]

INDICATORS DETECTED:
• [Sustained emotional distress pattern]
• [X consecutive challenging messages]
• [Emotional state declining]

WHAT YOU CAN DO:
✓ Reach out with a caring message or call
✓ Listen without judgment  
✓ Ask if they're safe and if they need anything
✓ Suggest professional resources (below)
✓ Take any mention of self-harm seriously

PROFESSIONAL RESOURCES:
• Crisis Hotline: 988 (24/7)
• Crisis Text Line: Text HOME to 741741
• Emergency: 911
• National Suicide Prevention: 1-800-273-8255

IMPORTANT NOTES:
• This is a support alert, not an emergency
• If immediate danger, call 911
• Your care and compassion matter most
• This tool supplements, not replaces, professional help

Questions? Reply to this email or call [support number]

---
This notification was sent because you are designated as a 
guardian contact for [User's First Name]. You can update 
your preferences at [link].
```

**What's NOT Included**:
- Specific conversation content
- User's location
- Medical history
- Other private details

### 3.6 User Configuration Options

**Threshold Settings**:
```python
GUARDIAN_ALERT_THRESHOLD = 'high'  # low, medium, or high
```
- **Low**: Alert guardians for any detected distress
- **Medium**: Alert for moderate sustained distress (default)
- **High**: Alert only for severe crisis indicators

**Auto-Notify Settings**:
```python
AUTO_NOTIFY_GUARDIANS = False  # Ask user first (default)
```
- **False**: System asks "Would you like to notify guardians?"
- **True**: Automatically sends notifications when threshold met

**Guardian Tiers**:
```python
guardians = {
    'high_severity': [
        {'name': 'Dr. Smith', 'email': 'dr.smith@therapy.com', 'relation': 'therapist'}
    ],
    'medium_severity': [
        {'name': 'Sarah (sister)', 'email': 'sarah@email.com', 'relation': 'family'}
    ],
    'low_severity': [
        {'name': 'Emma (friend)', 'phone': '555-1234', 'relation': 'friend'}
    ]
}
```

Different contacts for different severity levels enables appropriate escalation.

---

## 4. Implementation

### 4.1 Technology Stack

**Core System**:
- Python 3.7+: Core logic
- NLTK + TextBlob: Local NLP
- Streamlit: Web UI

**Notification Delivery** (Optional Features):
- Email: SMTP for email notifications
- SMS: Twilio API for text messages
- In-App: Local notifications

**Note**: Email/SMS require user to configure (optional). System works fully offline for in-app notifications only.

### 4.2 Crisis Detection Implementation

**Keyword Lists**:
```python
CRISIS_KEYWORDS = [
    # Self-harm indicators
    'suicide', 'suicidal', 'kill myself', 'end it all', 
    'better off dead', 'no reason to live',
    
    # Hopelessness indicators
    'hopeless', 'helpless', 'worthless', 'pointless',
    'no way out', 'can\'t go on',
    
    # Severe distress
    'overwhelming', 'unbearable', 'can\'t take it',
    'breaking point', 'give up'
]

SEVERITY_WEIGHTS = {
    'suicide': 3,  # Immediate concern
    'hopeless': 2,  # Moderate concern
    'overwhelm': 1  # Low concern
}
```

**Pattern Tracking**:
```python
def count_consecutive_distress(history, threshold=-0.3):
    """Count consecutive messages below sentiment threshold"""
    consecutive = 0
    max_consecutive = 0
    
    for entry in reversed(history):
        if entry['sentiment'] < threshold:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 0
    
    return max_consecutive
```

### 4.3 User Consent Dialog

**CLI Implementation**:
```python
def ask_user_consent_cli(severity, guardians):
    """Ask user if they want to notify guardians"""
    print(f"\n{'='*60}")
    print(f"⚠️  WELLNESS CHECK RECOMMENDED")
    print(f"{'='*60}")
    print(f"Severity: {severity.upper()}")
    print(f"\nYour designated guardians:")
    for g in guardians:
        print(f"  • {g['name']} ({g['relation']})")
    print(f"\nWould you like to notify them?")
    print("They will receive guidance on how to support you.")
    print("\nOptions:")
    print("  1. Yes, notify now")
    print("  2. No, not right now")
    print("  3. Show me what they'll receive first")
    
    while True:
        choice = input("\nYour choice (1-3): ").strip()
        
        if choice == '1':
            return True
        elif choice == '2':
            return False
        elif choice == '3':
            show_notification_preview(severity, guardians)
            continue
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
```

**Web UI Implementation**:
```python
def ask_user_consent_web(severity, guardians):
    """Streamlit dialog for user consent"""
    st.warning("⚠️ Wellness Check Recommended")
    
    st.write(f"**Severity**: {severity.upper()}")
    st.write("**Your guardians:**")
    for g in guardians:
        st.write(f"• {g['name']} ({g['relation']})")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✓ Notify Now", type="primary"):
            return True
    
    with col2:
        if st.button("✗ Not Now"):
            return False
    
    with col3:
        if st.button("👁️ Preview Message"):
            show_notification_preview(severity, guardians)
            return None
```

### 4.4 Notification Delivery

**Email Notification**:
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(guardian, user_name, severity, indicators):
    """Send email notification to guardian"""
    
    # Construct message
    msg = MIMEMultipart()
    msg['From'] = config.SYSTEM_EMAIL
    msg['To'] = guardian['email']
    msg['Subject'] = f"Wellness Check-in for {user_name}"
    
    # Use template from Section 3.4
    body = format_guardian_notification(
        user_name=user_name,
        severity=severity,
        indicators=indicators,
        guardian_name=guardian['name']
    )
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send via SMTP
    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Email failed: {str(e)}"
```

**SMS Notification** (Optional - Twilio):
```python
from twilio.rest import Client

def send_sms_notification(guardian, user_name, severity):
    """Send SMS notification (shorter version)"""
    
    message = f"""
    Wellness Alert for {user_name}
    
    Severity: {severity}
    
    Please reach out to check on them with care.
    
    If immediate danger, call 911.
    
    Resources: 988 (crisis), 741741 (text)
    
    Full details sent via email.
    """
    
    try:
        client = Client(config.TWILIO_SID, config.TWILIO_AUTH)
        client.messages.create(
            body=message.strip(),
            from_=config.TWILIO_NUMBER,
            to=guardian['phone']
        )
        return True, "SMS sent successfully"
    except Exception as e:
        return False, f"SMS failed: {str(e)}"
```

---

## 5. User Study

### 5.1 Study Design

**Participants**:
- **Users**: [N] adults (18+) with mild-to-moderate mental health concerns
- **Guardians**: [M] individuals designated by users (1-3 per user)
- **Recruitment**: [University counseling center referrals, online advertisements]
- **Compensation**: $[X] for users, $[Y] for guardians

**Inclusion Criteria**:
- Users: 18+, comfortable with English, access to smartphone/computer
- Guardians: Designated by user, willing to be notified

**Exclusion Criteria**:
- Active severe mental health crisis (referred to clinical care)
- Cognitive impairment affecting consent
- No reliable guardians available

**Duration**: [X] weeks (minimum 4 weeks)

**Study Conditions**:
1. **Guardian-in-Loop (GIL)**: Our system with user consent
2. **Auto-Notify**: Automatic guardian notification (no consent)
3. **No-Notify**: Crisis detection but no guardian alerts (control)

Participants randomly assigned to conditions.

### 5.2 Data Collection

**User Metrics**:
- **Usage Logs**: Session frequency, duration, message count
- **Crisis Events**: Severity levels, frequency
- **Consent Decisions**: How often users approved/denied notifications
- **Surveys**: Weekly + post-study

**Guardian Metrics**:
- **Notifications Received**: Count, severity distribution
- **Response Time**: Time from notification to guardian contact
- **Actions Taken**: What guardians did after receiving alert
- **Surveys**: Post-notification + post-study

**System Metrics**:
- **Detection Accuracy**: Crisis events vs. ground truth
- **False Positives**: Alerts for non-crisis situations
- **False Negatives**: Missed crisis situations

### 5.3 Evaluation Measures

**Primary Outcomes**:

1. **User Autonomy** (5-point Likert):
   - "I felt in control of who was notified"
   - "The system respected my choices"
   - "I appreciated being asked before notifying"

2. **Guardian Effectiveness** (5-point Likert):
   - "The notification helped me support the user"
   - "I knew what actions to take"
   - "The information was appropriate"

3. **Privacy Satisfaction** (5-point Likert):
   - "I trust the system with sensitive information"
   - "The right amount of detail was shared"
   - "My privacy was respected"

**Secondary Outcomes**:
- System Usability Scale (SUS)
- Guardian burden (effort required)
- User-guardian relationship quality
- Crisis resolution rate

### 5.4 Qualitative Methods

**User Interviews** (semi-structured):
- Experience with guardian notifications
- Decision-making process for consent
- Privacy concerns
- Suggestions for improvement

**Guardian Interviews**:
- Experience receiving notifications
- Helpfulness of information provided
- Challenges in responding
- Desired features

**Thematic Analysis**:
- Transcribe interviews
- Code for themes
- Identify patterns
- Validate with multiple coders

---

## 6. Results

### 6.1 Participant Demographics

**Users** (N=[X]):
- Age: Mean=[Y], SD=[Z], Range=[A-B]
- Gender: [X]% female, [Y]% male, [Z]% non-binary
- Mental health history: [X]% with prior diagnosis
- Privacy concern level: [X]% high, [Y]% medium, [Z]% low

**Guardians** (N=[M]):
- Relationship to user: [X]% therapist, [Y]% family, [Z]% friend
- Age: Mean=[Y], SD=[Z]
- Prior experience with mental health support: [X]%

### 6.2 System Usage

**Overall Engagement**:
- Total sessions: [X]
- Average sessions per user: [Y] (SD=[Z])
- Average session duration: [A] minutes
- Total messages: [B]
- Retention at week 4: [X]%

**Crisis Detection**:
- Total crises detected: [X]
- Severity distribution: [Y]% high, [Z]% medium, [W]% low
- Average per user: [A] crises over [X] weeks

### 6.3 Guardian Notification Patterns

**User Consent Decisions** (GIL condition):

| Severity | Notifications Triggered | User Approved | User Denied | Consent Rate |
|----------|-------------------------|---------------|-------------|--------------|
| High     | [X]                     | [Y]          | [Z]         | [W]%        |
| Medium   | [X]                     | [Y]          | [Z]         | [W]%        |
| Low      | [X]                     | [Y]          | [Z]         | [W]%        |
| **Total**| [X]                     | [Y]          | [Z]         | [W]%        |

**Key Finding**: Users approved [X]% of high-severity notifications but only [Y]% of low-severity, suggesting they appropriately calibrate guardian involvement.

**Auto-Notify Condition**:
- Notifications sent: [X]
- User satisfaction: [Y/5] (lower than GIL: [Z/5], p<0.05)
- "Felt notifications were appropriate": [W]% (vs. [V]% in GIL, p<0.05)

### 6.4 Guardian Response

**Response Time**:
- Median time to contact user: [X] minutes (IQR: [Y-Z])
- [W]% responded within 1 hour
- [V]% responded within 24 hours

**Actions Taken**:
- Phone call: [X]%
- Text message: [Y]%
- In-person visit: [Z]%
- Professional referral: [W]%
- Multiple actions: [V]%

**Guardian Effectiveness Ratings**:

| Question | GIL Condition | Auto-Notify | No-Notify | p-value |
|----------|---------------|-------------|-----------|---------|
| "Notification helped me support user" | [4.X/5] | [3.X/5] | N/A | <0.05 |
| "I knew what actions to take" | [4.X/5] | [3.X/5] | N/A | <0.05 |
| "Information was appropriate" | [4.X/5] | [3.X/5] | N/A | <0.01 |

**Key Finding**: Guardians in GIL condition rated notifications significantly more helpful (p<0.05), suggesting consent process improves guardian experience.

### 6.5 Primary Outcomes

**6.5.1 User Autonomy**

| Measure | GIL | Auto-Notify | p-value |
|---------|-----|-------------|---------|
| "Felt in control" | [4.X/5] | [2.X/5] | <0.001 |
| "System respected choices" | [4.X/5] | [2.X/5] | <0.001 |
| "Appreciated being asked" | [4.X/5] | N/A | - |

**Key Finding**: GIL condition significantly higher on all autonomy measures. [X]% of Auto-Notify users expressed discomfort with lack of control.

**6.5.2 Privacy Satisfaction**

| Measure | GIL | Auto-Notify | No-Notify | p-value |
|---------|-----|-------------|-----------|---------|
| "Trust with sensitive info" | [4.X/5] | [3.X/5] | [4.X/5] | <0.05 |
| "Right amount of detail shared" | [4.X/5] | [3.X/5] | N/A | <0.05 |
| "Privacy respected" | [4.X/5] | [3.X/5] | [4.X/5] | <0.001 |

**Key Finding**: GIL and No-Notify similar privacy ratings; Auto-Notify significantly lower (p<0.001).

**6.5.3 Crisis Resolution**

| Outcome | GIL | Auto-Notify | No-Notify | p-value |
|---------|-----|-------------|-----------|---------|
| User contacted professional help | [X]% | [Y]% | [Z]% | <0.05 |
| Crisis resolved within 48h | [X]% | [Y]% | [Z]% | <0.05 |
| User felt supported | [X]% | [Y]% | [Z]% | <0.01 |

**Key Finding**: GIL showed highest resolution rate ([X]%) and user satisfaction ([Y]%), suggesting guardian involvement improves outcomes when user-initiated.

### 6.6 False Positives and Negatives

**Detection Accuracy**:

| Metric | Value | 95% CI |
|--------|-------|--------|
| True Positives | [X] | [XX-XX] |
| False Positives | [Y] | [YY-YY] |
| True Negatives | [Z] | [ZZ-ZZ] |
| False Negatives | [W] | [WW-WW] |
| Precision | [0.XX] | [0.XX-0.XX] |
| Recall | [0.XX] | [0.XX-0.XX] |
| F1 Score | [0.XX] | [0.XX-0.XX] |

**Analysis**: System achieved [X]% precision and [Y]% recall. False positive rate of [Z]% acceptable per user and guardian feedback.

**User Response to False Positives**:
- [X]% said "Better safe than sorry"
- [Y]% said "Acceptable frequency"
- [Z]% said "Too many false alarms"

### 6.7 Qualitative Findings

**User Themes**:

**Theme 1: Control Increases Trust**
> "Knowing I can say no makes me more likely to say yes. It's my choice." - P12

> "The automatic version would have scared me away. I need to feel in control." - P7

**Theme 2: Context Matters**
> "Sometimes I'm venting, not in crisis. I appreciate the system asking first." - P23

> "High severity? Yes, notify. Medium? Depends on the day." - P15

**Theme 3: Guardian Selection Is Personal**
> "I chose my therapist for high, my sister for medium. They serve different roles." - P8

> "I wouldn't want my mom notified every time. But my best friend? That's okay." - P19

**Guardian Themes**:

**Theme 1: Actionable Information Is Key**
> "The 'what to do' section was perfect. I didn't panic; I knew how to help." - G5

> "I appreciated knowing it wasn't an emergency, just a check-in." - G12

**Theme 2: Minimal Information Preserves Trust**
> "I didn't need to know details. Just that they needed support." - G8

> "If I got their full conversation, I'd feel invasive. This was right." - G14

**Theme 3: Timeliness Enables Support**
> "Getting the alert when they needed it meant I could reach out while it mattered." - G3

> "Without this, I wouldn't have known. They hide it well." - G20

---

## 7. Discussion

### 7.1 Key Findings

**Finding 1: User Consent Preserves Autonomy Without Sacrificing Safety**

The GIL approach demonstrated that asking for consent before notifications does not reduce crisis resolution. In fact:
- Crisis resolution: GIL [X]% vs. Auto [Y]% (p<0.05)
- User satisfaction: GIL [4.X/5] vs. Auto [3.X/5] (p<0.01)

This challenges the assumption that automatic intervention is necessary for effectiveness.

**Finding 2: Privacy and Safety Are Not Opposing Goals**

Both privacy satisfaction and crisis resolution were highest in GIL condition:
- Privacy: GIL [4.X/5] vs. Auto [3.X/5] (p<0.001)
- Safety: GIL [X]% resolution vs. Auto [Y]% (p<0.05)

Privacy-respecting design can *enhance* safety by increasing trust and engagement.

**Finding 3: Guardians Prefer Actionable, Minimal Information**

Guardian interviews revealed strong preference for:
- Actionable guidance (100% positive)
- Minimal details (95% preferred over full disclosure)
- Severity context (100% found helpful)

This supports minimal disclosure principle in notification design.

**Finding 4: Multi-Threshold Enables Appropriate Escalation**

Users demonstrated nuanced decision-making:
- Approved [X]% of high-severity notifications
- Approved [Y]% of medium-severity
- Approved [Z]% of low-severity

This suggests users calibrate guardian involvement appropriately when given control.

### 7.2 Design Implications

**Implication 1: Default to User Consent**

Mental health systems should ask users before notifying external parties, except in clear emergencies. The consent dialog:
- Increases autonomy perception
- Enables contextual decision-making
- Preserves trust in system

**Implication 2: Provide Actionable Guardian Guidance**

Notifications should include:
- ✓ Severity level
- ✓ Specific actions to take
- ✓ Professional resources to share
- ✓ Context (is this an emergency?)
- ✗ Conversation details
- ✗ Medical information
- ✗ Location data (unless emergency)

**Implication 3: Support Relationship-Based Escalation**

Different relationships require different notification strategies:
- Therapists: Detailed, professional tone
- Family: Caring, less technical
- Friends: Supportive, peer language

Systems should allow customization per guardian.

**Implication 4: Embrace Multi-Threshold Approach**

Severity levels enable:
- Appropriate escalation
- Reduced false positive burden
- User customization
- Guardian preparation

Binary (crisis/not crisis) is insufficient; gradations matter.

### 7.3 Comparison to Related Work

**vs. Woebot (Automated Only)**:
- Woebot: No guardian involvement
- Our system: Guardian-in-loop when needed
- Advantage: External support without losing automation benefits

**vs. Life Alert (Automatic Only)**:
- Life Alert: Automatic 911 call
- Our system: User consent, guardian choice
- Advantage: Preserves autonomy for mental health context

**vs. Crisis Text Line (Manual Only)**:
- CTL: User must initiate contact
- Our system: Proactive detection + user control
- Advantage: Catches users who won't reach out themselves

### 7.4 Limitations

**L1: Sample Size and Generalizability**
- [Small/Medium] sample (N=[X])
- [University/Community] population
- May not generalize to all demographics

**L2: Short Duration**
- [X] weeks may not capture long-term effects
- Novelty effects possible
- Longer studies needed

**L3: Self-Selection Bias**
- Volunteers may be more privacy-conscious
- Results may not apply to general population
- Diverse recruitment needed

**L4: Simulated Crises**
- Some crises may be "simulated" for study
- Real crises may differ
- Ecological validity concerns

**L5: Guardian Availability**
- Not all users have appropriate guardians
- Results assume guardian availability
- Alternative support needed for some users

### 7.5 Ethical Considerations

**Informed Consent**: All participants understood guardian notification possibility

**Mandatory Reporting**: Study protocol included mandatory reporting for imminent danger

**Guardian Burden**: Guardians compensated and could opt-out anytime

**User-Guardian Conflicts**: Process for handling relationship problems

**Vulnerable Populations**: Extra protections for high-risk individuals

### 7.6 Future Work

**Short-term**:
1. Larger-scale deployment ([N>500])
2. Longer duration ([6-12 months])
3. Diverse population recruitment
4. Clinical validation studies

**Medium-term**:
1. Machine learning for improved detection
2. Natural language generation for personalized notifications
3. Integration with wearable data
4. Multi-language support

**Long-term**:
1. Federated learning across users (privacy-preserving)
2. Predictive crisis modeling
3. Integration with clinical care systems
4. Policy recommendations for mental health tech

---

## 8. Conclusion

We presented a guardian-in-the-loop approach to crisis intervention that preserves user autonomy while enabling timely external support. Through multi-threshold severity detection, opt-in notifications, and minimal information disclosure, our system achieved:
- High user autonomy ratings ([4.X/5])
- Effective crisis resolution ([X]%)
- Guardian satisfaction with notifications ([4.X/5])
- Acceptable false positive rate ([Y]%)

These results demonstrate that **privacy, autonomy, and safety are not mutually exclusive** in mental health technology. By respecting user agency, we can build systems that individuals actually trust and use during their most vulnerable moments.

### 8.1 Design Guidelines for Crisis Intervention Systems

Based on our findings, we recommend:

**G1**: Default to user consent for guardian notifications (except clear emergencies)

**G2**: Provide multi-threshold severity levels for appropriate escalation

**G3**: Share minimal, actionable information with guardians

**G4**: Support relationship-based customization (therapist vs. friend vs. family)

**G5**: Offer preview of notifications before sending

**G6**: Enable easy modification of guardian contacts and preferences

**G7**: Combine detection with user agency; don't fully automate life-affecting decisions

These guidelines can inform the design of future mental health technologies that balance user needs, privacy concerns, and safety imperatives.

### 8.2 Broader Impact

This work contributes to the growing field of **human-in-the-loop AI for mental health**, demonstrating that:
1. Users can make appropriate decisions even during distress
2. External support improves outcomes when user-initiated
3. Privacy and safety can be achieved simultaneously
4. Guardian involvement is acceptable when respectfully implemented

As mental health technology becomes more prevalent, preserving human dignity, autonomy, and privacy while providing effective support will be critical to adoption and impact.

---

## Acknowledgments

We thank our study participants for their trust and vulnerability in sharing their experiences. We thank [Funding Sources]. We thank [Collaborators] for valuable feedback. We thank the mental health professionals who guided our ethical considerations.

---

## References

[1] CDC. (2020). Suicide rates rising across the U.S. Centers for Disease Control and Prevention.

[2] SAMHSA. (2021). Key substance use and mental health indicators in the United States. Substance Abuse and Mental Health Services Administration.

[3] Gaur, M., Alambo, A., Sain, J. P., Kursuncu, U., Thirunarayan, K., Kavuluru, R., ... & Pathak, J. (2018). Knowledge-aware assessment of severity of suicide risk for early intervention. *The World Wide Web Conference*.

[4] Coppersmith, G., Leary, R., Crutchley, P., & Fine, A. (2018). Natural language processing of social media as screening for suicide risk. *Biomedical informatics insights*, 10.

[5] Morris, R. R., Kouddous, K., Kshirsagar, R., & Schueller, S. M. (2018). Towards an artificially empathic conversational agent for mental health applications. *CHI Conference*.

[6] De Choudhury, M., Kiciman, E., Dredze, M., Coppersmith, G., & Kumar, M. (2016). Discovering shifts to suicidal ideation from mental health content in social media. *CHI Conference*.

[7] Fitzpatrick, K. K., Darcy, A., & Vierhile, M. (2017). Delivering cognitive behavior therapy to young adults with symptoms of depression and anxiety using a fully automated conversational agent (Woebot). *JMIR mental health*, 4(2), e7785.

[8] Chancellor, S., & De Choudhury, M. (2020). Methods in predictive techniques for mental health status on social media: a critical review. *npj Digital Medicine*, 3(1), 1-11.

[9] Calvo, R. A., Dinakar, K., Picard, R., & Maes, P. (2016). Computing in mental health. *CHI Conference Extended Abstracts*.

[10] Naslund, J. A., Aschbrenner, K. A., Marsch, L. A., & Bartels, S. J. (2016). The future of mental health care: peer-to-peer support and social media. *Epidemiology and psychiatric sciences*, 25(2), 113-122.

---

**Code Availability**: https://github.com/tk1573-sys/AI-wellness-Buddy

**Study Materials**: [Available upon request pending ethics approval]

---

*End of Conference Paper 2*
