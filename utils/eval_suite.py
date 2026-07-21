"""
eval_suite.py
Root Wrapper Module for AI Model Accuracy Benchmark & Evaluation Suite
Exposes run_golden_dataset_evaluation and evaluate_candidate_submission.
"""

from utils.eval_suite import run_golden_dataset_evaluation, evaluate_candidate_submission

__all__ = [
    "run_golden_dataset_evaluation",
    "evaluate_candidate_submission"
]

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING GOLDEN DATASET BENCHMARK EVALUATION SUITE")
    print("=" * 60)
    res = run_golden_dataset_evaluation()
    summary = res["summary"]
    print(f"Total Test Cases: {summary['total_resumes']} Resumes")
    print(f"Mean Absolute Error (MAE): {summary['mae_percentage']:.2f}%")
    print(f"Human-AI Correlation Accuracy: {summary['correlation_accuracy']:.1f}%")
    print(f"Gate Agreement Rate: {summary['screening_gate_agreement_rate']:.1f}%")
    print("=" * 60)