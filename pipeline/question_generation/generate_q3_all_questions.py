import json
import pandas as pd
from pathlib import Path

from generators.q3_semantic_linkage import generate
from pipeline.assign_gold import save_csv   # 只用 save_csv，不用 assign_gold

PROJECT_ROOT = Path(__file__).resolve().parents[1]

WORD_META_PATH = PROJECT_ROOT / "metadata" / "word_meta.json"
SENSE_META_PATH = PROJECT_ROOT / "metadata" / "sense_meta.json"
RAW_SENT_DIR = PROJECT_ROOT / "data" / "raw_sentences"
OUT_DIR = PROJECT_ROOT / "questions" / "Q3"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(word: str):
    word_meta = load_json(WORD_META_PATH)
    sense_meta = load_json(SENSE_META_PATH)

    all_questions = []

    for sense_id, sense_info in sense_meta[word].items():

        # ❌ protoscene 不生成 Q3
        if sense_info["relation_type"] == "proto":
            continue

        # A: 当前 sense
        csv_A = RAW_SENT_DIR / word / f"{sense_id}.csv"
        if not csv_A.exists():
            print(f"[SKIP] {csv_A} not found")
            continue

        df_A = pd.read_csv(csv_A)
        sentences_A = df_A["sentence"].dropna().tolist()[25:40]  # 15 条

        # B: derived_from
        derived_from_label = sense_info["derived_from"]

        # 找到 derived_from 对应的 sense_id
        derived_sense_id = None
        for sid, info in sense_meta[word].items():
            if info["label_zh"] == derived_from_label:
                derived_sense_id = sid
                break

        if derived_sense_id is None:
            raise ValueError(f"Cannot find derived_from sense for {sense_id}")

        csv_B = RAW_SENT_DIR / word / f"{derived_sense_id}.csv"
        df_B = pd.read_csv(csv_B)
        sentences_B = df_B["sentence"].dropna().tolist()[25:40]

        questions = generate(
            word=word,
            sense_id=sense_id,
            sentences_A=sentences_A,
            sentences_B=sentences_B,
            sense_label_A=sense_info["label_zh"],
            sense_label_B=sense_meta[word][derived_sense_id]["label_zh"],
            relation_type_zh=sense_info["relation_type_zh"]
        )


        all_questions.extend(questions)

    out_path = OUT_DIR / f"{word}.csv"
    save_csv(all_questions, out_path)

    print(f"[DONE] Q3 questions saved to {out_path}")


if __name__ == "__main__":
    main("拿")
