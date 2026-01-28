import pandas as pd
from pathlib import Path

# =====================
# 文件路径配置
# =====================
QUESTIONS_DIR = Path("/Users/yongyi/Desktop/llm_probing/questions")  # 改成你实际路径
INPUT_CSV = QUESTIONS_DIR / "outputs_rebuilt.cleaned.csv"
OUTPUT_CSV = QUESTIONS_DIR / "model_outputs_evaluated.csv"

# =====================
# 读取 CSV
# =====================
df = pd.read_csv(INPUT_CSV)

# =====================
# 保留 ACL-friendly 核心列
# =====================
keep_cols = [
    "question_id",
    "question_type",
    "sentence",
    "relation_type",
    "option_A",
    "option_B",
    "option_C",
    "option_D",
    "gold_option",
    "gpt_answer",
    "deepseek_answer",
    "bert_answer"
]

df_eval = df[keep_cols].copy()

# =====================
# 新增 eval 列函数
# =====================
def evaluate_answer(pred, gold):
    if pd.isna(pred) or pd.isna(gold):
        return "Incorrect"
    return "Correct" if str(pred).strip() == str(gold).strip() else "Incorrect"

df_eval["eval_gpt"] = df_eval.apply(lambda row: evaluate_answer(row["gpt_answer"], row["gold_option"]), axis=1)
df_eval["eval_deepseek"] = df_eval.apply(lambda row: evaluate_answer(row["deepseek_answer"], row["gold_option"]), axis=1)
df_eval["eval_bert"] = df_eval.apply(lambda row: evaluate_answer(row["bert_answer"], row["gold_option"]), axis=1)

# =====================
# 保存到新 CSV
# =====================
df_eval.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Evaluation 完成，结果保存到 {OUTPUT_CSV}")
