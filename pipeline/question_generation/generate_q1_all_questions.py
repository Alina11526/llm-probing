import json
import pandas as pd
from pathlib import Path

from generators.q1_protoscene import generate
from pipeline.assign_gold import assign_gold, save_csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

WORD_META_PATH = PROJECT_ROOT / "metadata" / "word_meta.json"
SENSE_META_PATH = PROJECT_ROOT / "metadata" / "sense_meta.json"
RAW_SENT_DIR = PROJECT_ROOT / "data" / "raw_sentences"
OUT_DIR = PROJECT_ROOT / "questions" / "Q1"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(word: str, n_per_sense=10):
    word_meta = load_json(WORD_META_PATH)
    sense_meta = load_json(SENSE_META_PATH)

    all_questions = []

    # ✅ Q1 options：
    # 所有 sense（包括 protoscene）都从 sense_meta 获取，保证不重复
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

        # Q1：使用前 10 条
        sentences = all_sentences[0:10]


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

    # ✅ 打乱选项 + 分配 ABC + gold
    all_questions = assign_gold(all_questions)

    out_path = OUT_DIR / f"{word}.csv"
    save_csv(all_questions, out_path)

    print(f"[DONE] Q1 questions saved to {out_path}")


if __name__ == "__main__":
    main("走")
