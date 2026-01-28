# pipeline/shuffle_all_questions.py

import pandas as pd
from pathlib import Path

def main():
    # ====== 基于当前脚本位置定位项目根目录 ======
    BASE_DIR = Path(__file__).parent.parent  # llm_probing/
    QUESTIONS_DIR = BASE_DIR / "questions"

    # ====== 输入输出文件路径 ======
    INPUT_CSV = QUESTIONS_DIR / "all_questions_master.csv"
    OUTPUT_CSV = QUESTIONS_DIR / "master_questions_shuffled.csv"

    # ====== 检查输入文件是否存在 ======
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

    # ====== 读取 master CSV ======
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} questions from {INPUT_CSV}")

    # ====== 检查关键列 ======
    if "question_type" not in df.columns:
        raise ValueError("Column 'question_type' not found in CSV")

    # ====== 按 question_type 分组并组内打乱 ======
    shuffled_groups = []
    for qtype, group in df.groupby("question_type", sort=False):
        shuffled = group.sample(frac=1, random_state=42).reset_index(drop=True)
        shuffled_groups.append(shuffled)

    # ====== 拼接所有组 ======
    df_shuffled = pd.concat(shuffled_groups, ignore_index=True)

    # ====== 保存新文件 ======
    df_shuffled.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"Shuffled file saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
