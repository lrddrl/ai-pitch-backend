import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt
import seaborn as sns

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
    # Connect to the database
    engine = sqlalchemy.create_engine("postgresql://postgres:152535@localhost:5432/ai_pitch_db")
    df = pd.read_sql_table("ai_evaluations", engine)

    # Rename columns as needed
    df = df.rename(columns={
        "ai_eval_id": "evaluator_id",
        "ai_pitch_deck_name": "startup_id",
        "tca_factor": "category",
    })

    # Run analysis
    subjectivity, subjectivity_summary = analyze_subjectivity(df)
    rubric_drift, rubric_drift_avg = analyze_rubric_inconsistency(df)

    # Output
    # print("Subjectivity:", subjectivity)
    # print("Subjectivity summary:", subjectivity_summary)
    # print("Rubric drift:", rubric_drift)
    # print("Rubric drift avg:", rubric_drift_avg)

     # --- Subjectivity Summary Visualization ---
    plt.figure(figsize=(12, 6))
    subjectivity_values = list(subjectivity_summary.values())
    subjectivity_keys = list(subjectivity_summary.keys())
    plt.bar(subjectivity_keys, subjectivity_values)
    plt.xlabel("Evaluator ID")
    plt.ylabel("Mean Absolute Deviation")
    plt.title("Subjectivity Summary per Evaluator")
    plt.tight_layout()
    plt.show()

    # --- Rubric Drift Avg Visualization ---
    plt.figure(figsize=(12, 6))
    drift_values = list(rubric_drift_avg.values())
    drift_keys = list(rubric_drift_avg.keys())
    plt.bar(drift_keys, drift_values, color='orange')
    plt.xlabel("Evaluator ID")
    plt.ylabel("Avg Absolute Rubric Drift")
    plt.title("Rubric Drift Average per Evaluator")
    plt.tight_layout()
    plt.show()

    # --- (Optional) Subjectivity Heatmap ---
    subj_df = pd.DataFrame(subjectivity)
    if not subj_df.empty:
        plt.figure(figsize=(10, 6))
        sns.heatmap(subj_df.T, annot=True, cmap="coolwarm", cbar_kws={'label': 'STD'})
        plt.title("Subjectivity Heatmap (STD per Evaluator & Category)")
        plt.xlabel("Evaluator ID")
        plt.ylabel("Category")
        plt.tight_layout()
        plt.show()

