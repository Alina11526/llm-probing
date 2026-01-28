import os
import time
import argparse
import requests
import pandas as pd
import re
from pathlib import Path
from tqdm import tqdm
from pipeline.utils_csv import safe_write_csv


# =====================
# 配置区（不建议随便改）
# =====================

MODEL_NAME = "deepseek-chat"
API_URL = "https://sg.uiuiapi.com/v1/chat/completions"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = PROJECT_ROOT / "questions"

INPUT_CSV = QUESTIONS_DIR / "master_questions_shuffled.csv"
OUTPUT_CSV = QUESTIONS_DIR / "model_outputs_rebuilt.csv"


DEFAULT_MAX_QUESTIONS = 10
TEMPERATURE = 0.0
TOP_P = 1.0
TIMEOUT = 60
MAX_RETRIES = 6
RETRY_SLEEP = 2


# =====================
# 工具函数
# =====================

def load_api_key():
    api_key = os.getenv("UIUI_DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("UIUI_DEEPSEEK_API_KEY not found. Please export it as an environment variable.")
    return api_key



def ensure_columns(df, columns):
    """保证输出 CSV 包含指定列"""
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    return df


def build_prompt(row):
    """构造每题 prompt"""
    parts = []

    if pd.notna(row.get("instruction", "")) and str(row.get("instruction")).strip():
        parts.append(str(row["instruction"]).strip())

    parts.append(str(row["question"]).strip())
    parts.append("")

    if pd.notna(row.get("option_A")):
        parts.append(f"A. {row['option_A']}")
    if pd.notna(row.get("option_B")):
        parts.append(f"B. {row['option_B']}")
    if pd.notna(row.get("option_C")):
        parts.append(f"C. {row['option_C']}")
    if pd.notna(row.get("option_D")) and str(row.get("option_D")).strip():
        parts.append(f"D. {row['option_D']}")

    parts.append("")
    parts.append("请只选择一个选项字母作答（A/B/C/D），不要解释，不要输出其他内容。")

    return "\n".join(parts)


def call_deepseek(api_key, prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个严格按照指令作答的语言模型。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else None
            if status and status >= 500:
                print(f"⚠️ DeepSeek 500 error, retry {attempt}/{MAX_RETRIES}")
                time.sleep(RETRY_SLEEP)
            else:
                raise
        except Exception as e:
            print(f"❌ DeepSeek error: {e}")
            break
    return None


def extract_answer(raw_output):
    """提取 A/B/C/D"""
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
        out_df = pd.read_csv(OUTPUT_CSV)
        out_df = ensure_columns(out_df, ["deepseek_answer", "deepseek_raw_output"])
    else:
        out_df = df.copy()
        out_df["deepseek_answer"] = ""
        out_df["deepseek_raw_output"] = ""

    # 保证列类型兼容
    out_df["deepseek_answer"] = out_df["deepseek_answer"].astype(object)
    out_df["deepseek_raw_output"] = out_df["deepseek_raw_output"].astype(object)

    # 找到需要跑的题
    to_run = out_df[out_df["deepseek_answer"].isna() | (out_df["deepseek_answer"] == "")]
    to_run = to_run.head(max_questions)

    if to_run.empty:
        print("No unanswered questions found. Nothing to do.")
        return

    print(f"Running DeepSeek on {len(to_run)} questions (model={MODEL_NAME})")

    for local_idx, (idx, row) in enumerate(tqdm(to_run.iterrows(), total=len(to_run))):
        prompt = build_prompt(row)

        result = None
        for attempt in range(MAX_RETRIES):
            try:
                result = call_deepseek(api_key, prompt)
                if result:
                    break
            except Exception as e:
                print(f"Attempt {attempt+1} error: {e}")
                time.sleep(RETRY_SLEEP)

        if result:
            raw_text = result["choices"][0]["message"]["content"].strip()
            answer = extract_answer(raw_text)
            out_df.loc[idx, "deepseek_raw_output"] = raw_text
            out_df.loc[idx, "deepseek_answer"] = answer
        else:
            out_df.loc[idx, "deepseek_raw_output"] = f"ERROR: failed after {MAX_RETRIES} retries"
            out_df.loc[idx, "deepseek_answer"] = ""

        # 每题处理完就写 CSV，保证安全
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
