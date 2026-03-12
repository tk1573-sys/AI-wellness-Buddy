# AI Emotional Wellness Buddy — Research Upgrade Guide

## 1) Research Motivation and Problem Statement
- Mental health support systems should capture **longitudinal emotional trajectories**, not only one-turn sentiment.
- This project studies whether conversational emotion signals can be used for:
  1. robust multi-emotion detection,
  2. short-horizon emotional trajectory forecasting,
  3. early and contextual crisis risk signaling.

## 2) Modular Agent Architecture
Implemented in `agent_pipeline.py`.

```text
User Message
   |
   v
[EmotionAnalysisAgent]
   |
   v
[PatternTrackingAgent] ----> advanced metrics (volatility/recovery/persistence/drift)
   |
   v
[ForecastingAgent] ----> OLS / EWMA / SimpleGRU comparison
   |
   v
[AlertDecisionAgent] ----> contextual crisis + sustained distress checks
   |
   v
[ResponseGenerationAgent]
```

## 3) AI / NLP Model Upgrades
- `emotion_analyzer.py`
  - Transformer-first adapter (`MLEmotionAdapter`) for probability outputs.
  - `ContextualCrisisAdapter` for contextual suicidal ideation / severe distress scoring.
  - Adds `emotion_probabilities`, `crisis_probability`, `suicidal_ideation_probability`.

## 4) Forecasting Upgrade
- `prediction_agent.py`
  - Added `SimpleGRUForecaster` (lightweight GRU-style neural baseline).
  - `compare_models()` now reports OLS vs EWMA and optional neural metrics.

## 5) Scientific Evaluation Pipeline
- `research_evaluation.py`
  - Dataset loaders (`json`, `jsonl`, `csv`) for GoEmotions / EmotionLines / DailyDialog-style files.
  - Precision / Recall / F1 / macro metrics for publishable reporting.

### Example evaluation flow
1. Prepare normalized files in `data/benchmarks/`.
2. Load samples with `load_emotion_dataset`.
3. Evaluate using `evaluate_classifier(samples, classifier_fn)`.
4. Report macro-F1 and class-wise metrics in thesis tables.

## 6) Security Notes
- Password hashing remains bcrypt-based (`auth_manager.py`).
- Local data encryption stays Fernet-based with restricted file permissions (`data_store.py`).
- Added contextual crisis scoring without exposing user text to external APIs by default.

## 7) Scalability and Deployment
- Added `api_service.py` (FastAPI optional service layer).
- Added `Dockerfile` for containerized deployment.

### Run API
```bash
pip install fastapi==0.115.11 uvicorn==0.34.0
uvicorn api_service:app --host 0.0.0.0 --port 8000
```

## 8) Reproducibility Checklist
- Python version: 3.12
- Install: `pip install -r requirements.txt`
- Tests: `python -m pytest test_wellness_buddy.py test_full_coverage.py test_extended_features.py test_auth_manager.py test_conversation_memory.py test_ui_modules.py -q`
- Record:
  - model availability flags,
  - dataset split strategy,
  - random seeds,
  - metric tables and confusion matrices.

## 9) Suggested Experiments
1. **Emotion Classification**: Heuristic vs Transformer vs Hybrid.
2. **Forecasting**: OLS vs EWMA vs SimpleGRU on distress trajectory scenarios.
3. **Crisis Detection**: keyword-only vs contextual classifier ablation.
4. **Pattern Metrics Utility**: effect of volatility/recovery/persistence on alert precision.

## 10) Unique Contribution Framing
**Proposed contribution**: a privacy-aware conversational wellness system that combines:
- context-aware emotion understanding,
- long-term emotional trajectory modeling,
- early-warning distress analytics,
- actionable explainability traces.

## 11) Paper Title Ideas and Research Questions
### Candidate Titles
1. *Longitudinal Emotional Trajectory Modeling for Privacy-Preserving Conversational Wellness Assistants*
2. *From Sentiment to Safety: Contextual Crisis Detection and Forecasting in Emotional Support Agents*
3. *Hybrid Transformer-Neural Analytics for Continuous Emotional Wellness Monitoring*

### Candidate Research Questions
1. Does transformer-based multi-emotion modeling significantly improve macro-F1 over keyword+polarity baselines?
2. Can neural sequence forecasting detect pre-distress transitions earlier than OLS?
3. Which advanced emotional metrics best predict sustained distress alerts with low false positives?
