#!/usr/bin/env python3
"""Benchmark keyword, transformer, and hybrid emotion models on GoEmotions.

Saves precision, recall, macro F1, accuracy → results/final_metrics.json.
Saves per-class metrics                     → results/classification_report.csv.
All runs are logged with timestamps         → logs/run.log.

Usage: python run_emotion_benchmark.py [--dataset PATH] [--max-samples N] [--dry-run]
       (omitting all flags uses built-in synthetic data automatically)
"""
from __future__ import annotations
import argparse, csv, json, logging, os, random, sys, tempfile  # noqa: E401

_ROOT = os.path.abspath(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ---------------------------------------------------------------------------
# Logging – writes to logs/run.log (with timestamps) and to the console
# ---------------------------------------------------------------------------
_LOGS_DIR = os.path.join(_ROOT, "logs")
os.makedirs(_LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(os.path.join(_LOGS_DIR, "run.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Startup dependency validation
# ---------------------------------------------------------------------------
_REQUIRED_PACKAGES = {
    "textblob": "textblob==0.17.1",
    "matplotlib": "matplotlib==3.7.0",
    "sklearn": "scikit-learn==1.3.2",
    "transformers": "transformers==4.35.2",
    "torch": "torch==2.1.1",
}

_missing_packages: list[str] = []
for _pkg, _req in _REQUIRED_PACKAGES.items():
    try:
        __import__(_pkg)
    except ImportError:
        _missing_packages.append(_req)

if _missing_packages:
    log.error(
        "Missing required dependencies. Install them with:\n"
        "  pip install %s\n"
        "Then re-run this script.",
        " ".join(_missing_packages),
    )
    sys.exit(1)

from datasets.goemotions_loader import load_goemotions, SYSTEM_LABELS  # noqa: E402
from research_evaluation import evaluate_classifier                     # noqa: E402
from benchmark_emotion_models import (                                  # noqa: E402
    _make_keyword_classifier, _make_transformer_classifier,
    _make_hybrid_classifier, _make_hybrid_no_override_classifier,
)

LABELS = list(SYSTEM_LABELS)

# ---------------------------------------------------------------------------
# Embedded GoEmotions-style subset (312 samples, 52 per emotion class,
# shuffled at runtime).  Used when no external dataset file is provided.
# ---------------------------------------------------------------------------
_GOEMOTIONS_SUBSET: list[tuple[str, str]] = [
    # joy (52 samples)
    ("I feel so happy and excited about the new job!", "joy"),
    ("What a wonderful and amazing day it has been", "joy"),
    ("I am grateful and blessed to have such friends", "joy"),
    ("Everything is going great, I feel fantastic", "joy"),
    ("Just got the best news of my life, so thrilled!", "joy"),
    ("I can't stop smiling, today was perfect", "joy"),
    ("We finally made it — this is everything I hoped for", "joy"),
    ("My heart is so full right now, truly blessed", "joy"),
    ("Absolutely overjoyed by the surprise party!", "joy"),
    ("I love this so much, it made my whole week", "joy"),
    ("So proud of what we accomplished together", "joy"),
    ("Life feels wonderful right now, no complaints", "joy"),
    ("I am beaming with pride and happiness today", "joy"),
    ("This is the happiest I have felt in years", "joy"),
    ("Celebrating big wins with family, best feeling ever", "joy"),
    ("I woke up feeling energetic and optimistic", "joy"),
    ("Great news from the doctor, huge relief and joy", "joy"),
    ("Our team won the championship, absolutely ecstatic!", "joy"),
    ("Just adopted a puppy, my heart is so full", "joy"),
    ("The concert was incredible, pure bliss all night", "joy"),
    ("I am so excited for the trip next week!", "joy"),
    ("Finally finished the project — feeling accomplished", "joy"),
    ("She said yes! Most joyful day of my life!", "joy"),
    ("I feel appreciated and valued by my colleagues", "joy"),
    ("The kids are thriving and I couldn't be prouder", "joy"),
    ("Vacation was amazing, came back recharged and happy", "joy"),
    ("I am loving every moment of this journey", "joy"),
    ("Received a scholarship — all my hard work paid off", "joy"),
    ("Reconnected with an old friend, felt such warmth", "joy"),
    ("The sunrise this morning was breathtaking, pure joy", "joy"),
    ("I am so grateful for this opportunity", "joy"),
    ("Watching my child take their first steps, incredible", "joy"),
    ("Laughter and good food with family, nothing better", "joy"),
    ("I am bursting with excitement about the new project", "joy"),
    ("Everything fell into place today, I feel amazing", "joy"),
    ("So thankful for the kind words from everyone", "joy"),
    ("The promotion finally came through, over the moon!", "joy"),
    ("I feel alive and full of purpose today", "joy"),
    ("Hugged my best friend after months apart, pure bliss", "joy"),
    ("The results came back clean — such a relief and joy", "joy"),
    ("I genuinely love what I do and it shows", "joy"),
    ("The garden is blooming, fills my heart with delight", "joy"),
    ("I am radiating positivity and good energy today", "joy"),
    ("Finished reading a beautiful book, deeply satisfied", "joy"),
    ("Random act of kindness made my whole day", "joy"),
    ("I feel hopeful and enthusiastic about the future", "joy"),
    ("Baby shower was so sweet, everyone was glowing", "joy"),
    ("I sang in the shower this morning — life is good", "joy"),
    ("We sealed the deal — champagne all around!", "joy"),
    ("I am so happy for my sister's success", "joy"),
    ("Surprise gift from my partner, truly touched and happy", "joy"),
    ("I feel light and carefree today, absolutely wonderful", "joy"),

    # sadness (52 samples)
    ("I am so sad and lonely, nothing feels right", "sadness"),
    ("Crying all night, feeling heartbroken and empty", "sadness"),
    ("I feel hopeless and depressed about the future", "sadness"),
    ("The grief and loss I feel is overwhelming", "sadness"),
    ("I miss them so much, it hurts to breathe", "sadness"),
    ("Can't stop crying, everything reminds me of what was", "sadness"),
    ("I feel utterly alone even in a crowded room", "sadness"),
    ("The sadness won't go away no matter what I do", "sadness"),
    ("I lost my best friend and the void is unbearable", "sadness"),
    ("Feeling broken inside, I don't know how to move on", "sadness"),
    ("My heart aches with a sorrow I can't explain", "sadness"),
    ("I am devastated by the news, completely shattered", "sadness"),
    ("Everything feels grey and meaningless right now", "sadness"),
    ("I cry in silence so nobody sees how much I hurt", "sadness"),
    ("The loneliness is crushing me slowly every day", "sadness"),
    ("Regret is eating me alive, I can't forgive myself", "sadness"),
    ("I feel like a burden to everyone around me", "sadness"),
    ("Waking up without you is the hardest part of my day", "sadness"),
    ("I mourn the life I could have had, the paths not taken", "sadness"),
    ("My soul feels heavy and tired all the time", "sadness"),
    ("I keep reliving the moment everything fell apart", "sadness"),
    ("The emptiness inside me is impossible to fill", "sadness"),
    ("I smiled today but it was just a mask, inside I'm broken", "sadness"),
    ("I feel forgotten and invisible to the people I love", "sadness"),
    ("Goodbyes are never easy and this one destroyed me", "sadness"),
    ("There is a constant ache in my chest that won't leave", "sadness"),
    ("I weep for all the time I wasted and cannot reclaim", "sadness"),
    ("Disappointment after disappointment has drained my spirit", "sadness"),
    ("I tried so hard and still failed — it's devastating", "sadness"),
    ("Sitting with old photos, drowning in nostalgia and grief", "sadness"),
    ("I have been feeling low and joyless for weeks now", "sadness"),
    ("Nothing excites me anymore, everything is dull and grey", "sadness"),
    ("I feel a deep sadness I can't quite put into words", "sadness"),
    ("Lost my job today, feeling scared and deeply sad", "sadness"),
    ("I am mourning a relationship I thought would last forever", "sadness"),
    ("Tears keep coming and I don't even know why sometimes", "sadness"),
    ("I feel so defeated and worn down by life", "sadness"),
    ("My heart broke seeing them struggle and not being able to help", "sadness"),
    ("The house feels so empty now that they are gone", "sadness"),
    ("I am grieving and trying to hold it together", "sadness"),
    ("Feeling desolate and forsaken on the hardest days", "sadness"),
    ("I stare at the ceiling at 3am wondering what went wrong", "sadness"),
    ("The silence left behind by loss is deafening", "sadness"),
    ("I gave everything I had and it still wasn't enough", "sadness"),
    ("Heavy-hearted today, just going through the motions", "sadness"),
    ("I miss who I used to be before everything changed", "sadness"),
    ("The sadness comes in waves and today was a big wave", "sadness"),
    ("Feeling hollow inside, like something vital is missing", "sadness"),
    ("I keep waiting for it to hurt less and it never does", "sadness"),
    ("Grief has a way of sneaking up when you least expect it", "sadness"),
    ("I am heartbroken and struggling to see the light", "sadness"),
    ("Some days the weight of sadness feels impossible to carry", "sadness"),

    # anger (52 samples)
    ("I am furious and angry about what happened", "anger"),
    ("This is so frustrating, I hate this situation", "anger"),
    ("I am livid and outraged by the injustice", "anger"),
    ("So irritated and annoyed with everything", "anger"),
    ("I cannot believe they would do something so wrong", "anger"),
    ("This is absolute nonsense and I am fed up", "anger"),
    ("I am seething with rage at the unfairness of it all", "anger"),
    ("They lied to my face and I am beyond angry", "anger"),
    ("How dare they treat people like that, it's disgusting", "anger"),
    ("I am ready to explode, everything is going wrong today", "anger"),
    ("This blatant disrespect makes my blood boil", "anger"),
    ("I am so angry I can barely think straight", "anger"),
    ("They got away with it again — I'm absolutely fuming", "anger"),
    ("The injustice of this situation makes me furious", "anger"),
    ("I stormed out because I couldn't take it anymore", "anger"),
    ("I hate that I let this get under my skin so badly", "anger"),
    ("What they did was cruel and I won't forgive it easily", "anger"),
    ("I am done being walked over, enough is enough", "anger"),
    ("The sheer arrogance of them makes me so angry", "anger"),
    ("I am clenching my fists trying to stay calm right now", "anger"),
    ("Nobody listens and I am sick and tired of repeating myself", "anger"),
    ("I feel betrayed and that betrayal has turned to rage", "anger"),
    ("How can anyone be so selfish and inconsiderate?", "anger"),
    ("I am irritated beyond belief at this incompetence", "anger"),
    ("The audacity of that statement made me see red", "anger"),
    ("I expressed my anger clearly but they dismissed me again", "anger"),
    ("I snapped today and I'm not proud of it but I was pushed", "anger"),
    ("Every time I think about it I get angry all over again", "anger"),
    ("I feel robbed and violated and it makes me furious", "anger"),
    ("This corrupt system infuriates me to my core", "anger"),
    ("I am grinding my teeth just thinking about it", "anger"),
    ("They broke my trust and I am disgusted and angry", "anger"),
    ("I am raging inside even though I look calm outside", "anger"),
    ("Sick and tired of the double standards — I'm done", "anger"),
    ("The way they spoke to me was humiliating and I'm livid", "anger"),
    ("I punched a pillow to release the anger building up", "anger"),
    ("Nothing is more maddening than being misrepresented", "anger"),
    ("I am so annoyed with the constant excuses and delays", "anger"),
    ("Their attitude is infuriating and needs to stop", "anger"),
    ("I am losing my patience at an alarming rate today", "anger"),
    ("I can feel the anger pulsing through me right now", "anger"),
    ("This has gone too far and I will not stay silent", "anger"),
    ("The disrespect I have had to endure is unacceptable", "anger"),
    ("I am deeply offended and outraged by that comment", "anger"),
    ("I left the meeting before saying something I'd regret", "anger"),
    ("I resent being blamed for something that wasn't my fault", "anger"),
    ("Their hypocrisy is maddening, I can barely contain it", "anger"),
    ("What gives them the right to treat others so badly?", "anger"),
    ("I am furious that nothing ever seems to change", "anger"),
    ("The unfairness of the decision has made me really angry", "anger"),
    ("I have reached my limit and I am absolutely livid", "anger"),
    ("Just thinking about what they did makes me so angry", "anger"),

    # fear (52 samples)
    ("I am scared and terrified of what might happen", "fear"),
    ("The dread and horror keep me up at night", "fear"),
    ("I feel frightened and panicked about the future", "fear"),
    ("A wave of terror washed over me when I heard the news", "fear"),
    ("I am paralysed by fear and can't move forward", "fear"),
    ("My heart pounds every time I think about it", "fear"),
    ("I am afraid of the dark thoughts that creep in at night", "fear"),
    ("Something feels terribly wrong and I can't shake the dread", "fear"),
    ("I break into a cold sweat just imagining the worst case", "fear"),
    ("I feel a creeping terror that I can't quite name", "fear"),
    ("I woke up screaming from yet another nightmare", "fear"),
    ("The fear of losing everything keeps me frozen", "fear"),
    ("I am genuinely frightened by how quickly things changed", "fear"),
    ("Panic surged through me and I couldn't breathe properly", "fear"),
    ("I feel a knot of dread in my stomach that won't loosen", "fear"),
    ("Every shadow seems threatening when fear takes hold", "fear"),
    ("I am terrified of what tomorrow will bring", "fear"),
    ("The thought of failure terrifies me more than anything", "fear"),
    ("I feel helpless and frightened and don't know what to do", "fear"),
    ("Fear is dictating my every decision and holding me back", "fear"),
    ("I flinch at every unexpected noise because I'm so scared", "fear"),
    ("A deep-seated dread follows me everywhere I go", "fear"),
    ("I am scared of being abandoned and left alone", "fear"),
    ("The panic attacks are getting more frequent and intense", "fear"),
    ("I am trembling with fear just thinking about it", "fear"),
    ("I am terrified I won't be able to protect the ones I love", "fear"),
    ("The horror of what could happen keeps me awake all night", "fear"),
    ("I feel exposed and vulnerable and it terrifies me", "fear"),
    ("Something ominous is lurking and I feel it in my gut", "fear"),
    ("I am scared of my own mind when the intrusive thoughts come", "fear"),
    ("The uncertainty fills me with a bone-deep fear", "fear"),
    ("I feel cornered and terrified with no way out in sight", "fear"),
    ("My palms are sweating, heart racing — pure fear", "fear"),
    ("I dreaded going outside after what happened", "fear"),
    ("Fear makes everything look dangerous and threatening", "fear"),
    ("I am scared that history will repeat itself", "fear"),
    ("The anxiety of not knowing what comes next is frightening", "fear"),
    ("I feel a primal terror I haven't felt since childhood", "fear"),
    ("I am scared of losing control in front of everyone", "fear"),
    ("The slightest sound at night sends me into a panic", "fear"),
    ("I am terrified the diagnosis is worse than they're saying", "fear"),
    ("I can't shake the feeling that something bad is coming", "fear"),
    ("I feel hunted, even though there's nothing chasing me", "fear"),
    ("A cold wave of fear grips my chest most mornings", "fear"),
    ("I freeze up completely when fear takes hold of me", "fear"),
    ("I am scared to hope in case everything falls apart again", "fear"),
    ("Every time the phone rings I fear the worst", "fear"),
    ("The fear is irrational but it feels completely real", "fear"),
    ("I am frightened by how much I've changed", "fear"),
    ("The terrifying part is not knowing when it will happen", "fear"),
    ("I feel a shiver of dread whenever I'm alone", "fear"),
    ("I am frightened that this time I won't be able to cope", "fear"),

    # anxiety (52 samples)
    ("I am anxious and stressed about the exam", "anxiety"),
    ("Feeling overwhelmed and worried about everything", "anxiety"),
    ("Can't sleep, racing thoughts about what if scenarios", "anxiety"),
    ("I feel tense and uneasy about the situation", "anxiety"),
    ("My mind won't stop cycling through worst-case scenarios", "anxiety"),
    ("I have a constant knot of worry sitting in my chest", "anxiety"),
    ("The pressure of deadlines is making me feel sick", "anxiety"),
    ("I overthink every tiny thing and it exhausts me", "anxiety"),
    ("I feel like something is about to go wrong any moment", "anxiety"),
    ("Restless and on edge, I can't seem to relax at all", "anxiety"),
    ("My brain is in constant overdrive and I can't switch off", "anxiety"),
    ("I keep second-guessing every decision I make", "anxiety"),
    ("The uncertainty of it all is making me really anxious", "anxiety"),
    ("I feel anxious even when nothing specific is wrong", "anxiety"),
    ("My hands shake whenever I think about the presentation", "anxiety"),
    ("Worried sick about something I have no control over", "anxiety"),
    ("I am spiralling into anxiety and struggling to stop it", "anxiety"),
    ("Every small thing feels like a potential catastrophe", "anxiety"),
    ("The social situation filled me with dread and anxiety", "anxiety"),
    ("I can't eat properly because my stomach is in knots", "anxiety"),
    ("I keep checking my phone anxiously for any bad news", "anxiety"),
    ("My anxiety makes me avoid things I used to enjoy", "anxiety"),
    ("I feel overwhelmed by the sheer number of things to do", "anxiety"),
    ("The constant worry is exhausting me physically and mentally", "anxiety"),
    ("I am on edge and anticipating problems that haven't happened", "anxiety"),
    ("I feel a rising panic whenever I think about the future", "anxiety"),
    ("I am stuck in a loop of anxious thoughts I can't break", "anxiety"),
    ("I feel nervous and jittery for no clear reason today", "anxiety"),
    ("Everything feels urgent and overwhelming at the same time", "anxiety"),
    ("I wake up already worried before the day has begun", "anxiety"),
    ("The what-ifs are killing me, I can't stop the thoughts", "anxiety"),
    ("I feel hypervigilant and jumpy, always braced for impact", "anxiety"),
    ("I am consumed by worry and can't focus on anything else", "anxiety"),
    ("Even small decisions fill me with disproportionate anxiety", "anxiety"),
    ("I am dreading next week with every fibre of my being", "anxiety"),
    ("The tension in my body from anxiety is becoming physical pain", "anxiety"),
    ("I keep ruminating and can't let go of the worry", "anxiety"),
    ("I feel a background hum of anxiety almost every single day", "anxiety"),
    ("I am stressed about things that might not even happen", "anxiety"),
    ("I feel scattered and unable to think clearly from anxiety", "anxiety"),
    ("Everything is piling up and I feel on the verge of panic", "anxiety"),
    ("I am wound up tightly and can't find a way to unwind", "anxiety"),
    ("The constant anticipation of bad news wears me down", "anxiety"),
    ("I am anxious about being judged in social settings", "anxiety"),
    ("I feel a creeping unease that follows me throughout the day", "anxiety"),
    ("My chest tightens whenever the anxiety kicks in", "anxiety"),
    ("I feel edgy and irritable because the anxiety won't let up", "anxiety"),
    ("I am rehearsing conversations in my head out of anxiety", "anxiety"),
    ("The exam anxiety is so severe I can barely think straight", "anxiety"),
    ("I am catastrophising again and I know it but can't stop", "anxiety"),
    ("I feel anxious even in situations where I should feel safe", "anxiety"),
    ("Constant low-level anxiety is draining my energy slowly", "anxiety"),

    # neutral (52 samples)
    ("Things are okay, just a normal day", "neutral"),
    ("I am fine, nothing special happening", "neutral"),
    ("Everything is average, getting by as usual", "neutral"),
    ("Just managing, not bad not great", "neutral"),
    ("It was an ordinary day at work", "neutral"),
    ("The meeting was straightforward and uneventful", "neutral"),
    ("I went to the grocery store and picked up a few things", "neutral"),
    ("Nothing much happened today, pretty standard stuff", "neutral"),
    ("I read an article about climate change earlier", "neutral"),
    ("Made a to-do list for the week ahead", "neutral"),
    ("Had lunch at the usual spot, it was fine", "neutral"),
    ("The commute was a bit longer than normal today", "neutral"),
    ("I updated my calendar and scheduled a few meetings", "neutral"),
    ("It rained this morning so I took an umbrella", "neutral"),
    ("I watched a documentary last night about history", "neutral"),
    ("Things are proceeding as expected, nothing out of the ordinary", "neutral"),
    ("I replied to a few emails and then had a coffee", "neutral"),
    ("The report was submitted on time without issues", "neutral"),
    ("I spoke with a colleague about the project timeline", "neutral"),
    ("Everything seems to be moving along at a steady pace", "neutral"),
    ("I went for a short walk during my lunch break", "neutral"),
    ("The weather was mild and unremarkable today", "neutral"),
    ("I cooked pasta for dinner, it turned out okay", "neutral"),
    ("I paid the bills and checked the bank balance", "neutral"),
    ("Sorted through some paperwork this afternoon", "neutral"),
    ("Had a routine check-up at the doctor, all normal", "neutral"),
    ("I cleaned the house and did some laundry", "neutral"),
    ("Browsed the internet for a while, nothing interesting", "neutral"),
    ("Called my parents, it was a brief and casual chat", "neutral"),
    ("I looked up some information about the new bus schedule", "neutral"),
    ("The week has been fairly uneventful so far", "neutral"),
    ("I finished the book I was reading, it was decent", "neutral"),
    ("Set up a reminder for the appointment next Tuesday", "neutral"),
    ("The traffic was light on the way home today", "neutral"),
    ("I went to bed at a reasonable hour last night", "neutral"),
    ("Just going through the usual routine, nothing to report", "neutral"),
    ("Had a standard day, got a few things done", "neutral"),
    ("Made a note to follow up on the pending request", "neutral"),
    ("It was a quiet evening at home, watched some TV", "neutral"),
    ("I transferred files between devices this afternoon", "neutral"),
    ("Ordered something online, it should arrive Thursday", "neutral"),
    ("Took a short nap after work, feeling okay now", "neutral"),
    ("Attended a webinar, it covered some interesting points", "neutral"),
    ("I reviewed the contract briefly before signing", "neutral"),
    ("The day passed without any major incidents", "neutral"),
    ("Had a team lunch, it was pleasant and uneventful", "neutral"),
    ("I reminded myself to drink more water today", "neutral"),
    ("Got a haircut this weekend, same as usual", "neutral"),
    ("Checked the forecast — looks like more of the same weather", "neutral"),
    ("I went through my inbox and archived old messages", "neutral"),
    ("The gym session was routine, nothing particularly new", "neutral"),
    ("Picked up a prescription on the way home from work", "neutral"),
]


def save_plots(final: dict, plots_dir: str) -> None:
    """Generate and save benchmark plots for the IEEE paper.

    Parameters
    ----------
    final : dict
        ``{model_name: {precision, recall, macro_f1, accuracy, confusion_matrix}, ...}``
    plots_dir : str
        Directory where ``model_comparison.png`` and ``confusion_matrix.png``
        are written (created if it does not exist).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    os.makedirs(plots_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Model comparison bar chart
    # ------------------------------------------------------------------
    model_names = list(final.keys())
    metrics = ["precision", "recall", "macro_f1", "accuracy"]
    x = np.arange(len(model_names))
    width = 0.2

    fig, ax = plt.subplots()
    for i, metric in enumerate(metrics):
        values = [final[m][metric] for m in model_names]
        ax.bar(x + i * width, values, width, label=metric.replace("_", " ").title())

    ax.set_xticks(x + width * (len(metrics) - 1) / 2)
    ax.set_xticklabels(model_names)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Score")
    ax.set_title("Model Comparison")
    ax.legend()
    fig.tight_layout()
    comparison_path = os.path.join(plots_dir, "model_comparison.png")
    fig.savefig(comparison_path)
    plt.close(fig)
    print(f"✅ Model comparison plot saved to {comparison_path}")

    # ------------------------------------------------------------------
    # 2. Confusion matrix for the best model (highest macro_f1)
    # ------------------------------------------------------------------
    best_model = max(final, key=lambda m: final[m]["macro_f1"])
    cm_data = final[best_model].get("confusion_matrix", {})
    if cm_data:
        cm_labels = LABELS
        matrix = np.array(
            [[cm_data.get(t, {}).get(p, 0) for p in cm_labels] for t in cm_labels],
            dtype=float,
        )
        fig2, ax2 = plt.subplots()
        im = ax2.imshow(matrix, aspect="auto", cmap="Blues")
        ax2.set_xticks(range(len(cm_labels)))
        ax2.set_yticks(range(len(cm_labels)))
        ax2.set_xticklabels(cm_labels, rotation=45, ha="right")
        ax2.set_yticklabels(cm_labels)
        ax2.set_xlabel("Predicted")
        ax2.set_ylabel("True")
        ax2.set_title(f"Confusion Matrix — {best_model}")
        plt.colorbar(im, ax=ax2)
        for r in range(len(cm_labels)):
            for c in range(len(cm_labels)):
                ax2.text(c, r, int(matrix[r, c]), ha="center", va="center", fontsize=8)
        fig2.tight_layout()
        cm_path = os.path.join(plots_dir, "confusion_matrix.png")
        fig2.savefig(cm_path)
        plt.close(fig2)
        print(f"✅ Confusion matrix plot saved to {cm_path}")


def _write_synthetic_jsonl() -> str:
    """Write GoEmotions subset JSONL to a temp file; return its path."""
    samples = list(_GOEMOTIONS_SUBSET)
    random.shuffle(samples)
    log.info("Using embedded GoEmotions subset: %d samples", len(samples))
    fd, path = tempfile.mkstemp(suffix=".jsonl", prefix="goe_synth_")
    with os.fdopen(fd, "w") as fh:
        for text, label in samples:
            json.dump({"text": text, "labels": [label]}, fh)
            fh.write("\n")
    return path


def run_ablation(dataset_path=None, dry_run=False, max_samples=None):
    """Run ablation study across four model configurations.

    Configurations evaluated:

    * ``Transformer Only``   — transformer scores only, no keyword signal.
    * ``Keyword Only``       — keyword/heuristic scores only, no transformer.
    * ``Hybrid (no override)`` — blended transformer + keyword distribution,
      argmax of fused scores (**override disabled**).
    * ``Hybrid (with override)`` — blended distribution with adaptive keyword
      override when the top keyword score exceeds the threshold.

    Prints a comparison table and saves ``results/ablation.json``.
    """
    log.info("Starting ablation study (dry_run=%s, max_samples=%s)", dry_run, max_samples)
    os.makedirs(os.path.join(_ROOT, "results"), exist_ok=True)
    tmp = None
    if dry_run or not dataset_path:
        tmp = _write_synthetic_jsonl()
        dataset_path = tmp
    samples = load_goemotions(dataset_path, max_samples=max_samples)
    if tmp and os.path.exists(tmp):
        os.unlink(tmp)
    if not samples:
        log.warning("No samples loaded — aborting ablation.")
        return {}
    log.info("Loaded %d samples for ablation", len(samples))
    eval_pairs = [(s["text"], s["label"]) for s in samples]

    transformer_clf, _ = _make_transformer_classifier()
    hybrid_no_ov_clf, _ = _make_hybrid_no_override_classifier()
    hybrid_ov_clf, _ = _make_hybrid_classifier()
    ablation_models = {
        "Transformer Only":       transformer_clf,
        "Keyword Only":           _make_keyword_classifier(),
        "Hybrid (no override)":   hybrid_no_ov_clf,
        "Hybrid (with override)": hybrid_ov_clf,
    }

    final: dict = {}
    for name, clf in ablation_models.items():
        log.info("Evaluating ablation variant: %s", name)
        r = evaluate_classifier(eval_pairs, clf, labels=LABELS)
        final[name] = {
            "precision": r["macro_precision"],
            "recall":    r["macro_recall"],
            "macro_f1":  r["macro_f1"],
            "accuracy":  r["accuracy"],
        }

    hdr = (f"{'Model':<26} {'Precision':>10} {'Recall':>10}"
           f" {'Macro F1':>10} {'Accuracy':>10}")
    sep = "-" * len(hdr)
    print(f"\n{'='*66}\nAblation Study  ({len(samples)} samples)\n{'='*66}")
    print(sep); print(hdr); print(sep)
    for name, m in final.items():
        print(f"{name:<26} {m['precision']:>10.4f} {m['recall']:>10.4f}"
              f" {m['macro_f1']:>10.4f} {m['accuracy']:>10.4f}")
    print(sep)

    out = os.path.join(_ROOT, "results", "ablation.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(final, fh, indent=2)
    log.info("Ablation results saved to %s", out)
    print(f"\n✅ Ablation results saved to {out}")
    return final


def run_benchmark(dataset_path=None, dry_run=False, max_samples=None):
    """Evaluate all three models; print table; save results/final_metrics.json
    and results/classification_report.csv."""
    log.info("Starting benchmark (dry_run=%s, max_samples=%s)", dry_run, max_samples)
    os.makedirs(os.path.join(_ROOT, "results"), exist_ok=True)
    tmp = None
    if dry_run or not dataset_path:
        tmp = _write_synthetic_jsonl()
        dataset_path = tmp
    samples = load_goemotions(dataset_path, max_samples=max_samples)
    if tmp and os.path.exists(tmp):
        os.unlink(tmp)
    if not samples:
        log.warning("No samples loaded — aborting benchmark.")
        return {}
    log.info("Loaded %d samples for evaluation", len(samples))
    eval_pairs = [(s["text"], s["label"]) for s in samples]
    transformer_clf, _ = _make_transformer_classifier()
    hybrid_clf, _ = _make_hybrid_classifier()
    models = {
        "Keyword":     _make_keyword_classifier(),
        "Transformer": transformer_clf,
        "Hybrid":      hybrid_clf,
    }
    final: dict = {}
    full_results: dict = {}
    for name, clf in models.items():
        log.info("Evaluating model: %s", name)
        r = evaluate_classifier(eval_pairs, clf, labels=LABELS)
        final[name] = {
            "precision": r["macro_precision"],
            "recall":    r["macro_recall"],
            "macro_f1":  r["macro_f1"],
            "accuracy":  r["accuracy"],
            "confusion_matrix": r.get("confusion_matrix", {}),
        }
        full_results[name] = r
    hdr = f"{'Model':<22} {'Precision':>10} {'Recall':>9} {'Macro F1':>10} {'Accuracy':>10}"
    sep = "-" * len(hdr)
    print(f"\n{'='*62}\nGoEmotions Benchmark  ({len(samples)} samples)\n{'='*62}")
    print(sep); print(hdr); print(sep)
    for name, m in final.items():
        print(f"{name:<22} {m['precision']:>10.4f} {m['recall']:>9.4f}"
              f" {m['macro_f1']:>10.4f} {m['accuracy']:>10.4f}")
    print(sep)

    # Save results/final_metrics.json
    out = os.path.join(_ROOT, "results", "final_metrics.json")
    json_metrics = {
        name: {k: v for k, v in m.items() if k != "confusion_matrix"}
        for name, m in final.items()
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(json_metrics, fh, indent=2)
    log.info("Results saved to %s", out)
    print(f"\n✅ Results saved to {out}")

    # Save results/classification_report.csv (per-class metrics for each model)
    csv_path = os.path.join(_ROOT, "results", "classification_report.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["model", "emotion", "precision", "recall", "f1_score"])
        for name, r in full_results.items():
            for emotion, metrics in r.get("per_class", {}).items():
                writer.writerow([
                    name,
                    emotion,
                    metrics.get("precision", ""),
                    metrics.get("recall", ""),
                    metrics.get("f1", ""),
                ])
    log.info("Classification report saved to %s", csv_path)
    print(f"✅ Classification report saved to {csv_path}")

    save_plots(final, os.path.join(_ROOT, "plots"))
    return final


def main(argv=None):
    p = argparse.ArgumentParser(
        description=(
            "Benchmark emotion models on GoEmotions.\n"
            "When no --dataset is given the built-in synthetic subset is used "
            "automatically — no manual data download required."
        )
    )
    p.add_argument("--dataset", metavar="PATH",
                   help="Path to GoEmotions dataset (.jsonl/.csv/.json).")
    p.add_argument("--dry-run", action="store_true",
                   help="Force use of built-in synthetic data (no file needed).")
    p.add_argument("--max-samples", type=int, default=None,
                   help="Limit number of samples evaluated.")
    p.add_argument("--ablation", action="store_true",
                   help="Run ablation study (4 variants) and save results/ablation.json.")
    args = p.parse_args(argv)
    log.info(
        "run_emotion_benchmark starting — dataset=%s dry_run=%s max_samples=%s ablation=%s",
        args.dataset, args.dry_run, args.max_samples, args.ablation,
    )
    if args.ablation:
        run_ablation(dataset_path=args.dataset, dry_run=args.dry_run,
                     max_samples=args.max_samples)
    else:
        run_benchmark(dataset_path=args.dataset, dry_run=args.dry_run,
                      max_samples=args.max_samples)
        run_ablation(dataset_path=args.dataset, dry_run=args.dry_run,
                     max_samples=args.max_samples)
    log.info("run_emotion_benchmark finished.")


if __name__ == "__main__":
    main()
