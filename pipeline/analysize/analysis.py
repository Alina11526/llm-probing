import pandas as pd
from statsmodels.stats.contingency_tables import mcnemar

# -------------------------
# 1. 读取 CSV
# -------------------------
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR.parent / "model_outputs_eval" / "model_outputs_evaluated_1.csv"


df = pd.read_csv(file_path)


# -------------------------
# 2. 将 eval 列转换为 0/1
# -------------------------
eval_cols = ['eval_gpt', 'eval_deepseek', 'eval_bert']
df_numeric = df.copy()
for col in eval_cols:
    df_numeric[col] = df_numeric[col].map({'Correct': 1, 'Incorrect': 0})

# -------------------------
# 3. 辅助函数：生成 n/N (%) 格式
# -------------------------
def format_n_accuracy(n_correct, n_total):
    if n_total == 0:
        return "0/0 (0%)"
    pct = round(n_correct / n_total * 100)
    return f"{n_correct}/{n_total} ({pct}%)"

# -------------------------
# 4. 题型 × 模型正确率 & Overall
# -------------------------
grouped = df_numeric.groupby('question_type')
rows = []

for qt, group in grouped:
    n_questions = len(group)
    gpt_correct = group['eval_gpt'].sum()
    deep_correct = group['eval_deepseek'].sum()
    bert_correct = group['eval_bert'].sum()

    row = {
        'question_type': qt,
        'GPT': format_n_accuracy(gpt_correct, n_questions),
        'DeepSeek': format_n_accuracy(deep_correct, n_questions),
        'BERT': format_n_accuracy(bert_correct, n_questions),
        'N_questions': n_questions
    }
    rows.append(row)

# -------- Overall（不分题型）--------
n_total = len(df_numeric)
overall_row = {
    'question_type': 'Overall',
    'GPT': format_n_accuracy(df_numeric['eval_gpt'].sum(), n_total),
    'DeepSeek': format_n_accuracy(df_numeric['eval_deepseek'].sum(), n_total),
    'BERT': format_n_accuracy(df_numeric['eval_bert'].sum(), n_total),
    'N_questions': n_total
}

rows.insert(0, overall_row)

accuracy_by_type = pd.DataFrame(rows)
accuracy_by_type.to_csv('accuracy_by_type.csv', index=False)
print("题型 × 模型正确率（含 Overall）已保存：accuracy_by_type.csv")

# -------------------------
# 4.5 Overall（不分题型）模型正确率
# -------------------------
n_total = len(df_numeric)

gpt_correct = df_numeric['eval_gpt'].sum()
deep_correct = df_numeric['eval_deepseek'].sum()
bert_correct = df_numeric['eval_bert'].sum()

overall_row = {
    'question_type': 'Overall',
    'GPT': format_n_accuracy(gpt_correct, n_total),
    'DeepSeek': format_n_accuracy(deep_correct, n_total),
    'BERT': format_n_accuracy(bert_correct, n_total),
    'N_questions': n_total
}


# -------------------------
# 5. 题型 × relation_type × 模型正确率 & 做对题数
# -------------------------
rows = []
grouped = df_numeric.groupby(['question_type','relation_type'])
for (qt, rt), group in grouped:
    n_questions = len(group)
    gpt_correct = group['eval_gpt'].sum()
    deep_correct = group['eval_deepseek'].sum()
    bert_correct = group['eval_bert'].sum()
    row = {
        'question_type': qt,
        'relation_type': rt,
        'GPT': format_n_accuracy(gpt_correct, n_questions),
        'DeepSeek': format_n_accuracy(deep_correct, n_questions),
        'BERT': format_n_accuracy(bert_correct, n_questions),
        'N_questions': n_questions
    }
    rows.append(row)

accuracy_by_type_relation = pd.DataFrame(rows)
accuracy_by_type_relation.to_csv('accuracy_by_type_relation.csv', index=False)
print("题型 × relation_type × 模型正确率已保存：accuracy_by_type_relation.csv")

# -------------------------
# 6. McNemar 检验函数
# -------------------------
def compute_mcnemar(df, col1, col2):
    table = pd.crosstab(df[col1], df[col2])
    if table.shape != (2,2):
        return None
    result = mcnemar(table, exact=True)
    return result.pvalue

# -------------------------
# 7. McNemar 按题型 + relation_type
# -------------------------
rows = []
grouped = df_numeric.groupby(['question_type','relation_type'])
for (qt, rt), group in grouped:
    p_gd = compute_mcnemar(group, 'eval_gpt','eval_deepseek')
    p_gb = compute_mcnemar(group, 'eval_gpt','eval_bert')
    p_db = compute_mcnemar(group, 'eval_deepseek','eval_bert')
    row = {
        'question_type': qt,
        'relation_type': rt,
        'GPT_vs_DeepSeek_p': p_gd,
        'GPT_vs_BERT_p': p_gb,
        'DeepSeek_vs_BERT_p': p_db
    }
    rows.append(row)

mcnemar_by_type_relation = pd.DataFrame(rows)
mcnemar_by_type_relation.to_csv('mcnemar_results_by_type_relation.csv', index=False)
print("McNemar 检验（题型+relation_type）已保存：mcnemar_results_by_type_relation.csv")

# -------------------------
# 8. McNemar 按题型整体
# -------------------------
rows = []
grouped = df_numeric.groupby('question_type')
for qt, group in grouped:
    p_gd = compute_mcnemar(group, 'eval_gpt','eval_deepseek')
    p_gb = compute_mcnemar(group, 'eval_gpt','eval_bert')
    p_db = compute_mcnemar(group, 'eval_deepseek','eval_bert')
    row = {
        'question_type': qt,
        'GPT_vs_DeepSeek_p': p_gd,
        'GPT_vs_BERT_p': p_gb,
        'DeepSeek_vs_BERT_p': p_db
    }
    rows.append(row)

mcnemar_by_type = pd.DataFrame(rows)
mcnemar_by_type.to_csv('mcnemar_results_by_type.csv', index=False)
print("McNemar 检验（题型整体）已保存：mcnemar_results_by_type.csv")

# -------------------------
# 9. McNemar 按 relation_type 整体
# -------------------------
rows = []
grouped = df_numeric.groupby('relation_type')
for rt, group in grouped:
    p_gd = compute_mcnemar(group, 'eval_gpt','eval_deepseek')
    p_gb = compute_mcnemar(group, 'eval_gpt','eval_bert')
    p_db = compute_mcnemar(group, 'eval_deepseek','eval_bert')
    row = {
        'relation_type': rt,
        'GPT_vs_DeepSeek_p': p_gd,
        'GPT_vs_BERT_p': p_gb,
        'DeepSeek_vs_BERT_p': p_db
    }
    rows.append(row)

mcnemar_by_relation = pd.DataFrame(rows)
mcnemar_by_relation.to_csv('mcnemar_results_by_relation.csv', index=False)
print("McNemar 检验（relation_type整体）已保存：mcnemar_results_by_relation.csv")

