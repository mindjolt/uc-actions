import os
import csv

from database import Database


def ingest_report(db: Database, report_path: str):
    mtime = int(os.path.getmtime(report_path))

    with open(report_path, 'rt') as f:
        rows = list(csv.reader(f))

    metric_names = [row[0] for row in rows]
    samples = []

    report_id = db.create_report(mtime)
    metric_ids = db.get_metric_ids(metric_names)

    for row in rows:
        name, count, stddev, minimum, maximum, mean = row
        samples.append((report_id, metric_ids[name], count, stddev, minimum, maximum, mean))

    db.insert_samples(samples)
