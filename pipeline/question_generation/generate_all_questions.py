import pandas as pd
from pathlib import Path
import subprocess
import sys

from pipeline import generate_q1_all_questions
from pipeline import generate_q2_all_questions
from pipeline import generate_q3_all_questions


PROJECT_ROOT = Path(__file__).resolve().parents[1]

Q1_DIR = PROJECT_ROOT / "questions" / "Q1"
Q2_DIR = PROJECT_ROOT / "questions" / "Q2"
Q3_DIR = PROJECT_ROOT / "questions" / "Q3"

MASTER_DIR = PROJECT_ROOT / "questions"
MASTER_DIR.mkdir(exist_ok=True)

MASTER_OUT = MASTER_DIR / "all_questions_master.csv"


def run_pipeline(module_name: str, word: str):
    """
    运行某一个 pipeline module
    """
    print(f"[RUN] {module_name} ({word})")
    subprocess.run(
        [sys.executable, "-m", module_name],
        check=True
    )


def load_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"[SKIP] {path} not found")
        return pd.DataFrame()
    return pd.read_csv(path)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    统一字段，缺失的补空
    """
    columns = [
        "question_id",
        "question_type",
        "word",
        "sense_id",
        "sentence",
        "instruction",
        "question",
        "relation_type",
        "option_A",
        "option_B",
        "option_C",
        "option_D",
        "gold_option",
        "gold_text",
    ]

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df[columns]

def assign_gold_option(df: pd.DataFrame) -> pd.DataFrame:
    """
    根据 gold_text 和 option_X 列，动态生成 gold_option。
    """
    for idx, row in df.iterrows():
        for opt_label in ["A", "B", "C", "D"]:
            opt_col = f"option_{opt_label}"
            if row.get(opt_col, "") == row.get("gold_text", ""):
                df.at[idx, "gold_option"] = opt_label
                break
        else:
            # 如果没找到匹配
            df.at[idx, "gold_option"] = ""
            print(f"[WARN] gold_text not found in options for row {idx}")
    return df


def main(word: str):
    # 1️⃣ 运行三个 pipeline（你也可以注释掉，只做 merge）
# 直接在主进程调用各模块的 main 函数，传入 word
    generate_q1_all_questions.main(word)
    generate_q2_all_questions.main(word)
    generate_q3_all_questions.main(word)


    # 2️⃣ 读 CSV
    df_q1 = load_if_exists(Q1_DIR / f"{word}.csv")
    df_q2 = load_if_exists(Q2_DIR / f"{word}.csv")
    df_q3 = load_if_exists(Q3_DIR / f"{word}.csv")

    # 3️⃣ 统一列
    dfs = []
    for df in [df_q1, df_q2, df_q3]:
        if not df.empty:
            dfs.append(normalize_columns(df))

    if not dfs:
        print("[ERROR] No questions generated.")
        return

    master_df = pd.concat(dfs, ignore_index=True)

    # ✅ 新增：动态生成 gold_option
    master_df = assign_gold_option(master_df)

    # 4️⃣ 保存 master CSV
    master_df.to_csv(MASTER_OUT, index=False, encoding="utf-8-sig")



    # 4️⃣ 保存 master CSV
    master_df.to_csv(MASTER_OUT, index=False, encoding="utf-8-sig")
    print(f"[DONE] Master CSV saved to {MASTER_OUT}")
    print(f"[INFO] Total questions: {len(master_df)}")


if __name__ == "__main__":

    all_words = ["拿", "开", "走","吃"]  # 所有多义字列表
    all_dfs = []

    for word in all_words:
        # 直接调用你的 pipeline 模块的 main 函数
        generate_q1_all_questions.main(word)
        generate_q2_all_questions.main(word)
        generate_q3_all_questions.main(word)

        # 读取每个字生成的 CSV
        df_q1 = load_if_exists(Q1_DIR / f"{word}.csv")
        df_q2 = load_if_exists(Q2_DIR / f"{word}.csv")
        df_q3 = load_if_exists(Q3_DIR / f"{word}.csv")

            # 读取 CSV
        df_q1_path = Q1_DIR / f"{word}.csv"
        df_q2_path = Q2_DIR / f"{word}.csv"
        df_q3_path = Q3_DIR / f"{word}.csv"

        # 检查文件是否存在
        for path, qtype in zip([df_q1_path, df_q2_path, df_q3_path], ["Q1","Q2","Q3"]):
            if not path.exists():
                print(f"[MISSING CSV] {qtype} for {word} -> {path} not found")
        
        # 读 CSV（如果不存在会返回空 DataFrame）
        df_q1 = load_if_exists(df_q1_path)
        df_q2 = load_if_exists(df_q2_path)
        df_q3 = load_if_exists(df_q3_path)

        # 打印每类题目数量
        print(f"[INFO] {word} - Q1: {len(df_q1)} | Q2: {len(df_q2)} | Q3: {len(df_q3)}")

        # 进一步检查 Q3 原始句子长度（防止 slice 返回空）
        if not df_q3.empty:
            for idx, row in df_q3.iterrows():
                sentence_lines = str(row.get("sentence","")).split("\n")
                if len(sentence_lines) != 2:
                    print(f"[Q3 WARNING] {word} - row {idx} sentence has {len(sentence_lines)} lines")
                
        for df in [df_q1, df_q2, df_q3]:
            if not df.empty:
                all_dfs.append(normalize_columns(df))

    # 合并所有多义字数据到 master
    if all_dfs:
        master_df = pd.concat(all_dfs, ignore_index=True)
        
        def assign_question_id(df: pd.DataFrame) -> pd.DataFrame:
            ids = []
            for idx, row in df.iterrows():
                qtype = row["question_type"]
                word = row["word"]
                sense = row["sense_id"] if row["sense_id"] else "NA"
                qid = f"{qtype}_{word}_{sense}_{idx:04d}"
                ids.append(qid)
            df["question_id"] = ids
            return df


        master_df = assign_question_id(master_df)
        master_df = assign_gold_option(master_df)
        master_df.to_csv(MASTER_OUT, index=False, encoding="utf-8-sig")
        print(f"[DONE] Master CSV saved to {MASTER_OUT}")
        print(f"[INFO] Total questions: {len(master_df)}")
    else:
        print("[ERROR] No questions generated for any word.")
