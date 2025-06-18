import pandas as pd


def get_fake_scores():
    return [
        {"evaluator_id": "e1", "startup_id": "s1", "category": "Features & Benefits", "score": 7},
        {"evaluator_id": "e1", "startup_id": "s1", "category": "Readiness", "score": 8},
        {"evaluator_id": "e1", "startup_id": "s2", "category": "Features & Benefits", "score": 6},
        {"evaluator_id": "e1", "startup_id": "s2", "category": "Readiness", "score": 7},

        {"evaluator_id": "e2", "startup_id": "s1", "category": "Features & Benefits", "score": 6},
        {"evaluator_id": "e2", "startup_id": "s1", "category": "Readiness", "score": 7},
        {"evaluator_id": "e2", "startup_id": "s2", "category": "Features & Benefits", "score": 5},
        {"evaluator_id": "e2", "startup_id": "s2", "category": "Readiness", "score": 6},

        {"evaluator_id": "e3", "startup_id": "s1", "category": "Features & Benefits", "score": 8},
        {"evaluator_id": "e3", "startup_id": "s1", "category": "Readiness", "score": 9},
        {"evaluator_id": "e3", "startup_id": "s2", "category": "Features & Benefits", "score": 7},
        {"evaluator_id": "e3", "startup_id": "s2", "category": "Readiness", "score": 8},
    ]

def analyze_subjectivity(df):
    subjectivity = df.groupby(['evaluator_id', 'category'])['score'].std().unstack().fillna(0)
    group_avg = df.groupby(['startup_id', 'category'])['score'].mean().reset_index()
    df_merged = df.merge(group_avg, on=['startup_id', 'category'], suffixes=('', '_avg'))
    df_merged['abs_dev'] = abs(df_merged['score'] - df_merged['score_avg'])
    subjectivity_summary = df_merged.groupby('evaluator_id')['abs_dev'].mean()
    return subjectivity.to_dict(), subjectivity_summary.to_dict()

def analyze_rubric_inconsistency(df):
    pivot = df.pivot_table(index='evaluator_id', columns='category', values='score', aggfunc='mean')
    rubric_drift = pivot.apply(lambda x: x - x.mean(), axis=0)
    rubric_drift_avg = rubric_drift.abs().mean(axis=1)
    return rubric_drift.to_dict(), rubric_drift_avg.to_dict()


if __name__ == "__main__":
    data = get_fake_scores()
    df = pd.DataFrame(data)
    
    subjectivity_detail, subjectivity_summary = analyze_subjectivity(df)
    rubric_drift_detail, rubric_drift_summary = analyze_rubric_inconsistency(df)
    
    print("Subjectivity per evaluator and category:")
    print(subjectivity_detail)
    print("\nSubjectivity summary per evaluator:")
    print(subjectivity_summary)
    
    print("\nRubric drift per evaluator and category:")
    print(rubric_drift_detail)
    print("\nRubric drift average per evaluator:")
    print(rubric_drift_summary)
