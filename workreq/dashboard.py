"""대시보드 집계."""

from workreq.criteria import DEPARTMENTS, URGENCIES, WORK_TYPES

RECENT_LIMIT = 10


def count_by(rows, column, options):
    """목록 순서대로 건수를 센다. 0건인 값도 포함한다."""
    counts = {option: 0 for option in options}
    for row in rows:
        if row[column] in counts:
            counts[row[column]] += 1
    return counts


def summarize(rows):
    return {
        "total": len(rows),
        "work_type": count_by(rows, "work_type", WORK_TYPES),
        "urgency": count_by(rows, "urgency", URGENCIES),
        "department": count_by(rows, "department", DEPARTMENTS),
        "recent": rows[:RECENT_LIMIT],
    }
