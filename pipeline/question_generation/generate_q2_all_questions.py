'''
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

with open(PROJECT_ROOT / "metadata" / "word_meta.json", encoding="utf-8") as f:
    word_meta = json.load(f)

with open(PROJECT_ROOT / "metadata" / "sense_meta.json", encoding="utf-8") as f:
    sense_meta = json.load(f)


import json
import pandas as pd
from pathlib import Path
from generators.q2_sense_identification import generate

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SENSE_META = PROJECT_ROOT / "metadata" / "sense_meta.json"
RAW_SENT_DIR = PROJECT_ROOT / "data" / "raw_sentences"
OUT_DIR = PROJECT_ROOT / "questions" / "Q2"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(word: str):
    sense_meta = load_json(SENSE_META)
    all_questions = []

    for sense_id in sense_meta[word]:
        csv_path = RAW_SENT_DIR / word / f"{sense_id}.csv"
        if not csv_path.exists():
            print(f"[SKIP] {csv_path} not found")
            continue

        df = pd.read_csv(csv_path)
        sentences = df["sentence"].dropna().tolist()

        questions = generate(
    word=word,
    sense_id=sense_id,
    sentences=sentences,
    word_meta=word_meta,
    sense_meta=sense_meta,
    n=5  # 可选，每个 sense 生成 5 个题目
    
)


        all_questions.extend(questions)

    out_df = pd.DataFrame(all_questions)
    out_path = OUT_DIR / f"{word}.csv"
    out_df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"[DONE] Q2 questions saved to {out_path}")


if __name__ == "__main__":
    main("拿")
'''
'''
# pipeline/generate_q2_all.py
from generators.q2_sense_identification import generate
from pipeline.assign_gold import assign_gold, save_csv

# 假设这些数据从你的 metadata / CSV 中读入
word = "拿"
sense_id = "control"
sentences = [
    "经过代理机构申报专利的前提下，专利授权后，中介机构11--15天拿到…",
    "手拿把攥，汉语俗语，北京地方俗语中的常用表达，其核心语义为'比喻对某事的处理很有把握'"
]
options_list = ["控制、掌控", "攻下，占领", "拿取实物"]

# 生成原始题目字典
questions = generate(word, sense_id, sentences, {}, {}, options_list)

# 打乱选项 + 分配 ABC + gold
questions = assign_gold(questions)

# 保存 CSV
save_csv(questions, "questions/Q2_拿.csv")
'''

import json
import pandas as pd
from pathlib import Path

from generators.q2_sense_identification import generate
from pipeline.assign_gold import assign_gold, save_csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

WORD_META_PATH = PROJECT_ROOT / "metadata" / "word_meta.json"
SENSE_META_PATH = PROJECT_ROOT / "metadata" / "sense_meta.json"
RAW_SENT_DIR = PROJECT_ROOT / "data" / "raw_sentences"
OUT_DIR = PROJECT_ROOT / "questions" / "Q2"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(word: str, n_per_sense=5):
    word_meta = load_json(WORD_META_PATH)
    sense_meta = load_json(SENSE_META_PATH)

    all_questions = []

    # ✅ Q2：该 word 的所有 Protoscene label，作为统一 options_list
    options_list = [
        sense_meta[word][sid]["label_zh"]
        for sid in sense_meta[word]
    ]

    for sense_id in sense_meta[word]:
        csv_path = RAW_SENT_DIR / word / f"{sense_id}.csv"
        if not csv_path.exists():
            print(f"[SKIP] {csv_path} not found")
            continue

        df = pd.read_csv(csv_path)
        all_sentences = df["sentence"].dropna().tolist()

        # Q2：使用中间 15 条
        sentences = all_sentences[10:25]

        questions = generate(
            word=word,
            sense_id=sense_id,
            sentences=sentences,
            word_meta=word_meta,
            sense_meta=sense_meta,
            options_list=options_list
        )
        relation_type = sense_meta[word][sense_id].get("relation_type", "proto")

        for q in questions:
            q["relation_type"] = relation_type

        all_questions.extend(questions)

    # ✅ 分配 ABC + gold
    all_questions = assign_gold(all_questions)

    out_path = OUT_DIR / f"{word}.csv"
    save_csv(all_questions, out_path)

    print(f"[DONE] Q2 questions saved to {out_path}")


if __name__ == "__main__":
    main("拿")
