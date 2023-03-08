import csv
import math

from database import Database


def _calculate_standard_deviation(values: list[float]) -> float:
    mean = sum(values) / len(values)
    total = 0.0

    for value in values:
        delta = value - mean
        total += delta * delta

    return max(0.01, math.sqrt(total))


def compare_report(db: Database, report_path: str):
    with open(report_path, 'rt') as f:
        rows = list(csv.reader(f))

    metric_names = [row[0] for row in rows]
    metric_ids = db.get_metric_ids(metric_names, create_missing=False)
    metric_ids = {k: v for k, v in metric_ids.items() if v is not None}
    samples: dict[int, list[float]] = {metric_id: [] for metric_id in metric_ids.values()}

    for metric_id, mean in db.get_history(metric_ids.values()):
        samples[metric_id].append(mean)

    samples = {k: v for k, v in samples.items() if len(v) >= 10}
    standard_deviations = {k: _calculate_standard_deviation(v) for k, v in samples.items()}
    alerts, skipped = 0, 0

    for row in rows:
        name = row[0]
        mean = float(row[5])
        metric_id = metric_ids[name]

        if metric_id not in samples:
            skipped += 1
            continue

        prior_mean = sum(samples[metric_id]) / len(samples[metric_id])
        variance = (mean - prior_mean) / standard_deviations[metric_id]

        if mean > prior_mean and variance >= 2.0:
            percent = (100.0 * mean / prior_mean) - 100.0
            symbol = '\u26d4' if (variance >= 3.0) else '\u2623'

            print(f'* {symbol} {name} has gotten {percent:0.2f}% slower.')
            alerts += 1
        elif mean < prior_mean and variance <= -2.0:
            percent = 100.0 * (1.0 - mean / prior_mean)

            print(f'* \u2747 {name} has gotten {percent:0.2f}% faster!')
            alerts += 1

    if alerts == 0:
        print('* All clear! :+1:')

    if skipped > 0:
        print('* _Note: Some metrics do not have enough data to properly analyse yet._')
