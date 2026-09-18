"""Live Comparative Evaluation Script for Jev Routing: Baseline vs Grounded Profile Mode."""
import sys
import os
import json
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

load_dotenv()

from app.classifier import JevClassifier
from app.knowledge_base import SkillKnowledgeBase
from app.models import TaskType, RoutingTier

BENCHMARK_FILE = Path(__file__).parent.parent / "data" / "benchmark_80.json"
OUTPUT_REPORT = Path(__file__).parent.parent / "data" / "eval_comparison_report.json"

async def run_single_eval(classifier: JevClassifier, item: dict) -> dict:
    prompt = item["prompt"]
    start = time.perf_counter()
    res = await classifier.classify(prompt)
    duration_ms = round((time.perf_counter() - start) * 1000, 1)

    matched_skill = res.matched_skill
    tier_str = "Tier 1" if "Tier 1" in res.recommended_tier else ("Tier 2" if "Tier 2" in res.recommended_tier else "Tier 3")
    
    # Check correctness
    expected_tier = item["expected_tier"]
    expected_skill = item.get("expected_skill")
    is_negative = item.get("is_negative", False)

    if is_negative:
        # For negative cases, success means it did NOT match the forbidden skill and did not assign Tier 2 with that skill
        correct = (matched_skill is None) or (res.guarantee_badge == "Veto Triggered") or (tier_str == expected_tier)
    elif expected_skill:
        correct = (matched_skill == expected_skill) and (tier_str == expected_tier)
    else:
        correct = (tier_str == expected_tier)

    return {
        "task_type": str(res.task_type),
        "matched_skill": matched_skill,
        "matching_rate": res.matching_rate,
        "recommended_tier": tier_str,
        "guarantee_badge": res.guarantee_badge,
        "latency_ms": duration_ms,
        "correct": correct,
        "rationale": res.rationale
    }

async def main():
    print("=================================================================")
    print("🚀 Running Live TypeSafe Jev Benchmark: Baseline vs Profile Mode")
    print("=================================================================\n")

    if not BENCHMARK_FILE.exists():
        print(f"Error: {BENCHMARK_FILE} not found!")
        return

    data = json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))
    eval_items = [x for x in data if x["split"] == "eval"]
    print(f"Loaded {len(data)} total items. Testing {len(eval_items)} UNSEEN Final Eval items.\n")

    api_key = os.getenv("TYPESAFE_API_KEY")
    if api_key:
        print(f"✓ Using LIVE TypeSafe API Key: {api_key[:12]}...")
    else:
        print("⚠ Warning: No TYPESAFE_API_KEY found, running heuristic fallback.")

    # Initialize Classifiers
    kb = SkillKnowledgeBase()
    clf_baseline = JevClassifier(api_key=api_key, kb=kb, criteria_mode="baseline", timeout=20.0)
    clf_profile = JevClassifier(api_key=api_key, kb=kb, criteria_mode="profile", timeout=20.0)

    results = []

    # Run evaluations
    print(f"{'ID':<14} | {'Expected':<12} | {'Baseline Choice':<22} | {'Profile Choice':<22} | {'Result'}")
    print("-" * 85)

    for idx, item in enumerate(eval_items, 1):
        item_id = item["id"]
        exp_tag = f"{item['expected_tier']} ({item['expected_skill'] or 'None'})"[:12]

        # 1. Baseline Run
        b_res = await run_single_eval(clf_baseline, item)
        await asyncio.sleep(0.1)  # small rate limit guard

        # 2. Profile Run
        p_res = await run_single_eval(clf_profile, item)
        await asyncio.sleep(0.1)

        b_choice = f"{b_res['recommended_tier']}: {b_res['matched_skill'] or b_res['task_type']}"[:22]
        p_choice = f"{p_res['recommended_tier']}: {p_res['matched_skill'] or p_res['task_type']}"[:22]
        
        status = "✓ Profile Win" if (p_res["correct"] and not b_res["correct"]) else (
            "✗ Regress" if (not p_res["correct"] and b_res["correct"]) else (
                "✓ Both Green" if (p_res["correct"] and b_res["correct"]) else "✗ Both Fail"
            )
        )

        print(f"{item_id:<14} | {exp_tag:<12} | {b_choice:<22} | {p_choice:<22} | {status}")

        results.append({
            "id": item_id,
            "prompt": item["prompt"],
            "category": item.get("category", "eval"),
            "is_negative": item.get("is_negative", False),
            "expected_tier": item["expected_tier"],
            "expected_skill": item.get("expected_skill"),
            "baseline": b_res,
            "profile": p_res,
            "status": status
        })

    # Summary Statistics
    total = len(results)
    b_correct_cnt = sum(1 for r in results if r["baseline"]["correct"])
    p_correct_cnt = sum(1 for r in results if r["profile"]["correct"])

    b_acc = b_correct_cnt / total
    p_acc = p_correct_cnt / total

    # Veto/Negative Accuracy (15 cases)
    neg_cases = [r for r in results if r["is_negative"]]
    b_neg_correct = sum(1 for r in neg_cases if r["baseline"]["correct"])
    p_neg_correct = sum(1 for r in neg_cases if r["profile"]["correct"])

    # Positive Skill Accuracy (20 cases)
    pos_cases = [r for r in results if not r["is_negative"] and r["expected_skill"]]
    b_pos_correct = sum(1 for r in pos_cases if r["baseline"]["correct"])
    p_pos_correct = sum(1 for r in pos_cases if r["profile"]["correct"])

    # Latencies
    b_avg_lat = sum(r["baseline"]["latency_ms"] for r in results) / total
    p_avg_lat = sum(r["profile"]["latency_ms"] for r in results) / total

    summary = {
        "total_eval_samples": total,
        "baseline_accuracy": round(b_acc, 4),
        "profile_accuracy": round(p_acc, 4),
        "accuracy_delta": round(p_acc - b_acc, 4),
        "positive_skill_accuracy": {
            "baseline": f"{b_pos_correct}/{len(pos_cases)} ({b_pos_correct/len(pos_cases):.1%})",
            "profile": f"{p_pos_correct}/{len(pos_cases)} ({p_pos_correct/len(pos_cases):.1%})"
        },
        "negative_veto_accuracy": {
            "baseline": f"{b_neg_correct}/{len(neg_cases)} ({b_neg_correct/len(neg_cases):.1%})",
            "profile": f"{p_neg_correct}/{len(neg_cases)} ({p_neg_correct/len(neg_cases):.1%})"
        },
        "average_latency_ms": {
            "baseline": round(b_avg_lat, 1),
            "profile": round(p_avg_lat, 1)
        }
    }

    report_payload = {
        "metadata": {
            "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": "jev-latest",
            "api_endpoint": "https://api.typesafe.ai/v1/systemone",
            "unseen_eval_count": total
        },
        "summary": summary,
        "details": results
    }

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 50)
    print("📊 EVALUATION BENCHMARK SUMMARY")
    print("=" * 50)
    print(f"Total Eval Prompts: {total}")
    print(f"Baseline Accuracy : {b_acc:.1%} ({b_correct_cnt}/{total})")
    print(f"Profile Accuracy  : {p_acc:.1%} ({p_correct_cnt}/{total})")
    print(f"Accuracy Delta    : {p_acc - b_acc:+.1%}")
    print(f"Positive Matching : Baseline {summary['positive_skill_accuracy']['baseline']} -> Profile {summary['positive_skill_accuracy']['profile']}")
    print(f"Negative Veto Acc : Baseline {summary['negative_veto_accuracy']['baseline']} -> Profile {summary['negative_veto_accuracy']['profile']}")
    print(f"Avg Latency       : Baseline {b_avg_lat:.1f}ms -> Profile {p_avg_lat:.1f}ms")
    print(f"Saved full report to: {OUTPUT_REPORT}")

if __name__ == "__main__":
    asyncio.run(main())
