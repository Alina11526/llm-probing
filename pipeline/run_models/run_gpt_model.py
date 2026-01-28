
import os
import argparse
import pandas as pd
import requests
from pathlib import Path
from tqdm import tqdm
from pipeline.utils_csv import (
    safe_read_csv,
    safe_write_csv,
    ensure_columns,
)
import re
import time
# =====================
# 配置区（不建议随便改）
# =====================

MODEL_NAME = "gpt-3.5-turbo-0125"
API_URL = "https://sg.uiuiapi.com/v1/chat/completions"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = PROJECT_ROOT / "questions"

INPUT_CSV = QUESTIONS_DIR / "master_questions_shuffled.csv"
OUTPUT_CSV = QUESTIONS_DIR / "model_outputs_rebuilt.csv"


DEFAULT_MAX_QUESTIONS = 10
TEMPERATURE = 0.0
TOP_P = 1.0
TIMEOUT = 60

# =====================
# 工具函数
# =====================

def load_api_key():
    api_key = os.getenv("UIUI_GPT_API_KEY")
    if not api_key:
        raise RuntimeError(
            "UIUI_GPT_API_KEY not found. Please export it as an environment variable."
        )
    return api_key


def build_prompt(row):
    """
    构造单题 prompt：
    - instruction
    - question
    - options
    - 强制输出格式
    """
    parts = []

    if pd.notna(row["instruction"]) and str(row["instruction"]).strip():
        parts.append(str(row["instruction"]).strip())

    parts.append(str(row["question"]).strip())
    parts.append("")

    parts.append(f"A. {row['option_A']}")
    parts.append(f"B. {row['option_B']}")
    parts.append(f"C. {row['option_C']}")

    if pd.notna(row.get("option_D")) and str(row["option_D"]).strip():
        parts.append(f"D. {row['option_D']}")

    parts.append("")
    parts.append(
        "请只选择一个选项字母作答（A/B/C/D），不要解释，不要输出其他内容。"
    )

    return "\n".join(parts)


def call_gpt(api_key, prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个严谨的语言理解模型。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()




def extract_answer(raw_output):
    """
    尝试从模型输出中提取 A/B/C/D
    """
    if not raw_output:
        return ""
    raw_output = raw_output.upper()
    match = re.search(r"\b([A-D])\b", raw_output)
    if match:
        return match.group(1)
    return ""



# =====================
# 主流程
# =====================

def main(max_questions):
    api_key = load_api_key()

    df = pd.read_csv(INPUT_CSV)

    if OUTPUT_CSV.exists():
        out_df = safe_read_csv(OUTPUT_CSV)

        out_df = ensure_columns(
            out_df,
            ["gpt_answer", "gpt_raw_output"]
        )

    else:
        out_df = df.copy()
        out_df["gpt_answer"] = ""
        out_df["gpt_raw_output"] = ""

    # --- 新增修复 dtype 警告 ---
    out_df["gpt_answer"] = out_df["gpt_answer"].astype(object)
    out_df["gpt_raw_output"] = out_df["gpt_raw_output"].astype(object)


    # 找到需要跑的题目
    
    to_run = out_df[out_df["gpt_answer"].isna() | (out_df["gpt_answer"] == "")]
    to_run = to_run.head(max_questions)

    if to_run.empty:
        print("No unanswered questions found. Nothing to do.")
        return

    print(
        f"Running GPT on {len(to_run)} questions "
        f"(model={MODEL_NAME}, temperature={TEMPERATURE})"
    )

    for local_idx, (idx, row) in enumerate(to_run.iterrows()):
        prompt = build_prompt(row)

        # ---------- 自动重试 ----------
        MAX_RETRIES = 6
        for attempt in range(MAX_RETRIES):
            try:
                result = call_gpt(api_key, prompt)
                break  # 成功则跳出重试循环
            except requests.exceptions.HTTPError as e:
                if e.response.status_code >= 500:
                    print(f"Server error, retrying ({attempt+1}/{MAX_RETRIES}) for question {idx}...")
                    time.sleep(2)
                else:
                    raise
            except Exception as e:
                print("Other error:", e)
                result = None
                break
        # ---------- 重试结束 ----------

        if result:
            raw_text = result["choices"][0]["message"]["content"].strip()
            answer = extract_answer(raw_text)
            out_df.loc[idx, "gpt_raw_output"] = raw_text
            out_df.loc[idx, "gpt_answer"] = answer
        else:
            out_df.loc[idx, "gpt_raw_output"] = f"ERROR: failed after {MAX_RETRIES} retries"
            out_df.loc[idx, "gpt_answer"] = ""



    safe_write_csv(out_df, OUTPUT_CSV)
    print(f"Saved results to {OUTPUT_CSV}")


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


