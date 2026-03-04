# Understanding Results

## Confusion Matrix in a WAF Context

wafworth maps WAF testing to a standard confusion matrix:

|  | WAF blocks | WAF allows |
|--|-----------|-----------|
| **Should block** (attack) | True Positive (TP) | False Negative (FN) |
| **Should allow** (legit) | False Positive (FP) | True Negative (TN) |

- **TP**: WAF correctly blocks a malicious request
- **FN**: WAF misses an attack (bypass)
- **FP**: WAF blocks legitimate traffic (false alarm)
- **TN**: WAF correctly allows legitimate traffic

## Metrics

wafworth computes 7 metrics from the confusion matrix:

| Metric | Formula | What it tells you |
|--------|---------|-------------------|
| **Detection Rate** (Recall) | TP / (TP + FN) | What fraction of attacks are caught |
| **False Positive Rate** | FP / (FP + TN) | What fraction of legitimate traffic is blocked |
| **Precision** | TP / (TP + FP) | Of all blocks, how many were actual attacks |
| **Recall** | Same as Detection Rate | Alias for detection rate |
| **F1 Score** | 2 * P * R / (P + R) | Harmonic mean of precision and recall |
| **Balanced Accuracy** | (TPR + TNR) / 2 | Average of true positive rate and true negative rate |
| **Youden's Index** | TPR - FPR | Net effectiveness (-1 to 1, higher is better) |

## Console Output

The console report shows:

1. **Overall metrics**: detection rate, FP rate, precision, F1, balanced accuracy, Youden's index
2. **Per-category breakdown**: detection rate and FP rate for each attack category
3. **Per-encoding breakdown**: detection rate per encoding (when using multiple encodings)
4. **Latency stats**: p50, p95, p99, mean, and max response times

## JSON Output Structure

JSON results are written to the output directory (default `results/`). Structure:

```json
{
  "target": "modsecurity",
  "timestamp": "2026-03-04T12:00:00Z",
  "summary": {
    "total": 580,
    "tp": 520,
    "fp": 3,
    "tn": 27,
    "fn": 30,
    "detection_rate": 0.945,
    "false_positive_rate": 0.1,
    "precision": 0.994,
    "f1": 0.969,
    "balanced_accuracy": 0.923,
    "youdens_index": 0.845
  },
  "by_category": { ... },
  "by_encoding": { ... },
  "latency": {
    "p50_ms": 12.3,
    "p95_ms": 45.6,
    "p99_ms": 89.1,
    "mean_ms": 15.2,
    "max_ms": 120.5
  },
  "results": [
    {
      "test_id": "sqli-adv-001",
      "passed": true,
      "expected_action": "block",
      "actual_status": 403,
      "latency_ms": 11.2,
      "encoding": "plain",
      "category": "SQL Injection",
      "title": "Error-based extraction via EXTRACTVALUE"
    }
  ]
}
```

## Markdown Output

A Markdown summary is also generated, suitable for pasting into PR descriptions or issue trackers. It includes the same metrics tables and per-category breakdown.
