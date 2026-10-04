import pandas as pd
import numpy as np

np.random.seed(42)

n = 1000

# ---------------------------------
# 1. Task duration
# ---------------------------------

original_days = np.random.randint(5, 20, n)

# Days already spent on the task
days_elapsed = np.array([
    np.random.randint(0, d + 1)
    for d in original_days
])

# Days remaining
days_left = original_days - days_elapsed


# ---------------------------------
# 2. Expected progress
# ---------------------------------

expected_progress = (
    days_elapsed / original_days
) * 100


# ---------------------------------
# 3. Generate realistic progress
# ---------------------------------

# 0 = on track
# 1 = slightly delayed
# 2 = heavily delayed

delay_type = np.random.choice(
    [0, 1, 2],
    n,
    p=[0.50, 0.30, 0.20]
)

progress = []

for expected, delay in zip(expected_progress, delay_type):

    if delay == 0:
        # Task is roughly on schedule
        actual = expected + np.random.normal(0, 8)

    elif delay == 1:
        # Task is somewhat behind
        actual = expected - np.random.uniform(10, 25)

    else:
        # Task is significantly behind
        actual = expected - np.random.uniform(25, 50)

    progress.append(actual)


progress = np.clip(progress, 5, 100)


# ---------------------------------
# 4. Other task information
# ---------------------------------

priority = np.random.choice(
    [1, 2, 3],
    n,
    p=[0.3, 0.4, 0.3]
)

dependencies = np.random.randint(0, 5, n)

previous_delays = np.random.randint(0, 5, n)

reassignments = np.random.randint(0, 4, n)

team_workload = np.round(
    np.random.uniform(0.2, 1.0, n),
    2
)

response_delay = np.round(
    np.random.uniform(1, 48, n),
    1
)

estimated_hours = np.random.randint(
    2,
    40,
    n
)

hours_spent = np.random.randint(
    1,
    40,
    n
)


# ---------------------------------
# 5. Create DataFrame
# ---------------------------------

df = pd.DataFrame({

    "task_id": [
        f"T{i:04d}"
        for i in range(1, n + 1)
    ],

    "priority": priority,

    "days_left": days_left,

    "progress": np.round(progress, 2),

    "estimated_hours": estimated_hours,

    "hours_spent": hours_spent,

    "dependencies": dependencies,

    "previous_delays": previous_delays,

    "reassignments": reassignments,

    "team_workload": team_workload,

    "response_delay": response_delay,

    "original_days": original_days,

    "days_elapsed": days_elapsed,

    "expected_progress": np.round(
        expected_progress,
        2
    )
})


# ---------------------------------
# 6. Calculate progress gap
# ---------------------------------

df["progress_gap"] = (
    df["expected_progress"]
    - df["progress"]
).clip(lower=0).round(2)


# ---------------------------------
# 7. Save dataset
# ---------------------------------

df.to_csv(
    "data/tasks.csv",
    index=False
)


# ---------------------------------
# 8. Display results
# ---------------------------------

print("Dataset generated successfully!")

print("\nSample:")
print(
    df[
        [
            "task_id",
            "days_left",
            "expected_progress",
            "progress",
            "progress_gap"
        ]
    ].head(15)
)

print("\nProgress Gap Statistics:")
print(
    df["progress_gap"].describe()
)

print("\nTasks with progress gap > 20:")
print(
    (df["progress_gap"] > 20).sum()
)

print("\nTasks with progress gap > 40:")
print(
    (df["progress_gap"] > 40).sum()
)