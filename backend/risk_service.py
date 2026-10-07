def generate_reasons(
    days_left,
    progress_gap,
    team_workload,
    dependencies,
    previous_delays
):
    reasons = []

    if progress_gap > 40:
        reasons.append(
            "Progress is significantly behind the expected schedule."
        )
    elif progress_gap > 20:
        reasons.append(
            "Progress is noticeably behind the expected schedule."
        )
    elif progress_gap > 10:
        reasons.append(
            "Progress is slightly behind the expected schedule."
        )

    if days_left <= 2:
        reasons.append(
            "The deadline is approaching rapidly."
        )
    elif days_left <= 5:
        reasons.append(
            "Limited time remains to complete the task."
        )

    if team_workload > 0.8:
        reasons.append(
            "Team workload is currently high."
        )
    elif team_workload > 0.6:
        reasons.append(
            "Team workload is moderately high."
        )

    if dependencies >= 3:
        reasons.append(
            "Multiple dependencies may create bottlenecks."
        )

    if previous_delays >= 3:
        reasons.append(
            "The task has experienced repeated delays."
        )

    if not reasons:
        reasons.append(
            "No major risk signals were detected."
        )

    return reasons


def generate_recommendations(
    risk_label,
    reasons
):
    if risk_label == "Critical":
        return [
            "Prioritize this task immediately.",
            "Resolve blocking dependencies.",
            "Consider redistributing workload.",
        ]

    if risk_label == "Emerging Risk":
        return [
            "Review this task before risk increases.",
            "Address dependency bottlenecks.",
            "Redistribute lower-priority work if necessary.",
        ]

    if risk_label == "Watch":
        return [
            "Monitor the task closely.",
            "Review progress at the next checkpoint.",
        ]

    return [
        "Continue monitoring normal progress.",
        "Review again during the next project checkpoint.",
    ]