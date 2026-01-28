import os
import time
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
from pipeline.utils_csv import safe_write_csv


# =====================
# 配置区
# =====================

DEFAULT_MAX_QUESTIONS = 10

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = PROJECT_ROOT / "questions"

INPUT_CSV = QUESTIONS_DIR / "master_questions_shuffled.csv"
OUTPUT_CSV = QUESTIONS_DIR / "model_outputs_rebuilt.csv"


# =====================
# 工具函数（复用）
# =====================


def ensure_columns(df, columns):
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    return df


def extract_answer_from_scores(scores):
    """从 BERT 的概率/得分向量返回答案和最大得分"""
    if not scores or len(scores) < 3:
        return "", 0.0
    options = ["A", "B", "C", "D"]
    max_idx = np.argmax(scores)
    return options[max_idx], scores[max_idx]


# =====================
# BERT 模型调用
# =====================

def call_bert_model(row):
    """
    这里模拟调用 BERT 模型返回每个选项的得分
    实际可替换为你自己的 BERT 推理逻辑
    返回：scores = [score_A, score_B, score_C, score_D]
    """
    # TODO: 替换为真实 BERT 推理
    import random
    scores = [random.random() for _ in range(4)]
    total = sum(scores)
    scores = [s / total for s in scores]  # 归一化概率
    return scores


# =====================
# 主流程
# =====================

def main(max_questions):
    df = pd.read_csv(INPUT_CSV)

    if OUTPUT_CSV.exists():
        out_df = pd.read_csv(OUTPUT_CSV)
        out_df = ensure_columns(out_df, ["bert_answer", "bert_score", "bert_score_A", "bert_score_B", "bert_score_C", "bert_score_D"])

    else:
        out_df = df.copy()
        out_df["bert_answer"] = ""
        out_df["bert_score"] = ""

    # 保证列类型兼容
    out_df["bert_answer"] = ""
    out_df["bert_score"] = 0.0
    # 新增四列保存每个选项的分数
    out_df["bert_score_A"] = 0.0
    out_df["bert_score_B"] = 0.0
    out_df["bert_score_C"] = 0.0
    out_df["bert_score_D"] = 0.0


    # 找到需要跑的题
    to_run = out_df[out_df["bert_answer"].isna() | (out_df["bert_answer"] == "")]
    to_run = to_run.head(max_questions)

    if to_run.empty:
        print("No unanswered questions found. Nothing to do.")
        return

    print(f"Running BERT on {len(to_run)} questions")

    for local_idx, (idx, row) in enumerate(tqdm(to_run.iterrows(), total=len(to_run))):
        try:
            scores = call_bert_model(row)

            # 适配实际选项数量，提取最高分答案
            options = ["A", "B", "C", "D"][:len(scores)]
            max_idx = np.argmax(scores)
            answer = options[max_idx]
            score = scores[max_idx]

            # 保存最高分结果
            out_df.loc[idx, "bert_answer"] = answer
            out_df.loc[idx, "bert_score"] = score

            # 保存每个选项的分数，缺少的选项填 NaN
            option_cols = ["bert_score_A", "bert_score_B", "bert_score_C", "bert_score_D"]
            for i, col in enumerate(option_cols):
                if i < len(scores):
                    out_df.loc[idx, col] = scores[i]
                else:
                    out_df.loc[idx, col] = np.nan


        except Exception as e:
            print(f"❌ Error processing question {idx}: {e}")
            out_df.loc[idx, "bert_answer"] = ""
            out_df.loc[idx, "bert_score"] = 0.0

        # 每题处理完就写 CSV
        safe_write_csv(out_df, OUTPUT_CSV)

    print(f"✅ Finished running. Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_questions",
        type=int,
        default=DEFAULT_MAX_QUESTIONS,
        help="Maximum number of questions to run (default: 10)",
    )
    args = parser.parse_args()

    main(args.max_questions)
