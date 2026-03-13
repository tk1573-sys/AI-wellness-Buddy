# IEEE/Scopus Reviewer Revision Guide  
**Project:** AI Wellness Buddy: A Privacy-Preserving Mental Health Monitoring System

This document provides concrete, publication-focused revisions to strengthen both the repository and manuscript for IEEE/Scopus review.

---

## 1) Concrete Improvements Required (Reviewer Checklist)

### A. AI Methodology
- Use **transformer-based emotion inference** as the primary model path (already scaffolded through adapter architecture).
- Keep **rule-based** inference as baseline for ablation (privacy and low-resource fallback).
- Report calibrated multi-emotion probabilities, not only a single hard label.

### B. Forecasting Methodology
- Treat OLS as an interpretable baseline, not the final method.
- Compare:
  - OLS
  - EWMA
  - GRU (implemented lightweight baseline)
  - LSTM (planned)
  - Temporal Transformer (planned)
- Use the same train/validation split protocol and prediction horizon for all models.

### C. Evaluation Methodology
- Move from synthetic-only evidence to benchmark-backed evaluation:
  - GoEmotions: https://github.com/google-research/google-research/tree/master/goemotions
  - EmotionLines: https://github.com/declare-lab/EmotionLines
  - DailyDialog: http://yanran.li/dailydialog
- Mandatory metrics:
  - Precision, Recall, F1 (micro/macro)
  - Confusion matrix
  - ROC-AUC (one-vs-rest for multi-class)
  - Calibration error for probability outputs (recommended)

### D. Research Framing and Novelty
- Primary research question should be explicit:  
  **Can privacy-preserving, longitudinal emotional trajectory modeling provide early, clinically relevant distress signals without cloud data transfer?**
- Novelty should be framed as:
  1. local-first architecture,
  2. longitudinal trajectory modeling,
  3. explainable distress escalation pipeline,
  4. modular agentized design enabling controlled ablations.

### E. Trust and Real-World Adoption
- Trust must be treated as a first-class objective:
  - transparent model cards,
  - explicit non-diagnostic disclaimer,
  - user-visible rationale for alerts,
  - consent-gated guardian escalation,
  - auditable local data controls (export/delete).
- Avoid claims that imply universal or clinical replacement capability.

---

## 2) Rewritten Paper Sections (Drop-In IEEE Style)

## 2.1 Rewritten Problem Statement
Current mental health chat systems are typically optimized for short-turn response quality and cloud-scale deployment, but they under-emphasize longitudinal state tracking, user-controlled privacy, and accountable alerting. This creates three technical gaps: (i) limited emotional granularity under rule-based or polarity-only signals, (ii) weak temporal modeling for identifying sustained decline prior to crisis, and (iii) limited transparency in escalation decisions. The present work addresses these gaps by introducing a privacy-preserving, modular agent pipeline that combines contextual emotion inference, longitudinal pattern analytics, predictive forecasting, and explainable risk escalation under explicit user consent boundaries.

## 2.2 Rewritten Novelty and Contributions
This study contributes a local-first emotional AI framework whose novelty lies in **trajectory-aware, privacy-preserving distress modeling** rather than chatbot response generation alone. Specifically, the system (1) unifies rule-based and transformer-based emotion pathways within a swappable architecture for controlled comparison, (2) introduces longitudinal emotional metrics (volatility, recovery rate, stress persistence, behavioral drift) for risk-aware monitoring, (3) evaluates interpretable and neural forecasting models under a shared protocol, and (4) operationalizes consent-aware alerting with user-visible rationale outputs. Together, these elements form an auditable, research-oriented baseline for privacy-sensitive mental wellness support.

## 2.3 Rewritten Evaluation Design
The evaluation protocol combines controlled synthetic trajectories with public benchmark corpora. Emotion classification is assessed on GoEmotions, EmotionLines, and DailyDialog-derived mappings using macro/micro precision, recall, F1, and one-vs-rest ROC-AUC. Forecasting models (OLS, EWMA, GRU; with planned LSTM and temporal transformer baselines) are compared using MAE/RMSE over fixed forecasting horizons and matched train/validation folds. Alert quality is measured using event-level precision/recall against predefined distress-transition labels, with ablation studies isolating the effect of contextual crisis modeling and longitudinal metrics.

## 2.4 Rewritten Limitations Section
This work has four principal limitations. First, benchmark-to-deployment transfer remains uncertain due to domain shift between curated corpora and personal wellness conversations. Second, multilingual robustness beyond current Tamil/Tanglish support has not yet been established through large annotated corpora. Third, probability calibration under severe class imbalance requires further study, particularly for low-frequency crisis classes. Fourth, although the system is designed for safety-oriented support, it is not a diagnostic instrument and should not be used to replace professional mental healthcare pathways.

## 2.5 Rewritten Discussion (Privacy–Accuracy Trade-Off)
The central design trade-off is between privacy guarantees and peak predictive performance. Cloud-hosted large models can improve raw accuracy but increase data exposure risk and reduce user control over sensitive mental health narratives. A local-first architecture reduces this exposure and improves data sovereignty, but may constrain model capacity on commodity hardware. The proposed modular design therefore supports configurable operation modes: deterministic fallback for strict privacy contexts, and transformer/neural enhancement for research settings that permit additional compute. This explicit trade-off framing is essential for honest reporting and ethical deployment.

---

## 3) Refined Architecture and Agent Interaction Pipeline

```text
User Input
   |
   v
[Emotion Analysis Agent]
  - rule-based baseline
  - transformer classifier (optional)
  - contextual crisis probabilities
   |
   v
[Pattern Tracking Agent]
  - trajectory window
  - volatility / recovery / persistence / drift
   |
   v
[Forecasting Agent]
  - OLS, EWMA, GRU (current)
  - LSTM, Temporal Transformer (planned)
   |
   v
[Risk Assessment + Alert Agent]
  - composite risk score
  - explainable trigger rationale
  - consent-gated guardian escalation
   |
   v
[Response Generation Agent]
  - empathetic response synthesis
  - safety-constrained messaging
  - bilingual adaptation
```

### Architectural Clarification
- The **Emotion Analysis Agent** should emit both `primary_emotion` and calibrated probability distributions.
- The **Risk Assessment Agent** should consume both instantaneous and longitudinal features.
- The **Alert Agent** should expose machine-readable reasons (e.g., high stress persistence + worsening forecast + crisis context signal).
- The **Response Agent** should remain decoupled from detection logic to avoid hidden policy coupling.

---

## 4) Reproducibility Requirements (Repository-Level)

To be publication-ready, include and maintain:

1. **Dataset manifest** (`data/README.md`) with source URLs, licenses, splits, and preprocessing assumptions.
2. **Training/evaluation configs** (`configs/*.yaml`) defining:
   - model type,
   - hyperparameters,
   - seed,
   - split strategy,
   - metrics.
3. **Executable scripts**
   - `scripts/train_emotion_model.py`
   - `scripts/eval_emotion_model.py`
   - `scripts/eval_forecasting_models.py`
4. **Versioned outputs**
   - metrics JSON,
   - confusion matrices,
   - ROC curves,
   - checkpoint metadata (hash + config).
5. **Environment pinning**
   - requirements lockfile or reproducible environment spec.

---

## 5) Additional Experiments to Strengthen Publication Quality

1. **Ablation Study**
   - Rule-only vs Transformer-only vs Hybrid.
2. **Forecast Horizon Stress Test**
   - 1-step, 3-step, 7-step forecasting error comparison.
3. **Robustness to Noisy Inputs**
   - Code-mixed Tamil/English misspellings and colloquial variants.
4. **Calibration Study**
   - Reliability diagrams and expected calibration error.
5. **Fairness/Slice Evaluation**
   - Performance across language/script slices and emotion prevalence buckets.
6. **Human Evaluation**
   - Clinician/annotator scoring for response appropriateness and safety.
7. **Latency vs Accuracy**
   - On-device CPU profiling for practical deployability.

---

## 6) Code Structure Improvements for Publishability

Proposed structure for cleaner research workflows:

```text
ai_wellness_buddy/
  models/
    emotion/
    forecasting/
  agents/
  evaluation/
  data/
  scripts/
  configs/
  docs/
```

Key engineering recommendations:
- Separate production inference code from experimental training code.
- Keep deterministic baselines in `models/baselines.py`.
- Persist experiment metadata in structured JSON for reproducibility audits.
- Add explicit model version IDs in API responses for traceability.

---

## 7) Trust-Building Recommendations for Broad User Adoption

To convince users and institutions that the system can be responsibly used at scale:

1. Publish a concise **Safety and Scope Statement** in UI and docs.
2. Add a **“Why this alert?”** explanation panel (feature-level rationale).
3. Expose **user controls**: export, delete, pause monitoring, disable guardian alerts.
4. Publish **model cards** and known failure cases.
5. Report false-positive/false-negative risks in plain language.
6. Perform third-party security and ethics review before clinical-facing deployment.

These actions build trust by making system boundaries explicit, auditable, and user-controlled.

