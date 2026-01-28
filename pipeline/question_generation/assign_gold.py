# pipeline/assign_gold.py
import random
import pandas as pd

def assign_gold(questions: list):
    """
    给每道题打乱选项顺序，分配 A/B/C/D，并标注 gold_option
    """
    all_questions = []

    for q in questions:
        opts = q['options']
        random.shuffle(opts)  # 打乱顺序

        # 分配字母
        labels = ['A', 'B', 'C', 'D'][:len(opts)]
        option_map = dict(zip(labels, opts))

        # 找到 gold 的字母
        # 找到 gold 的字母
        gold_option = None
        for label, text in option_map.items():
            if text == q['gold_text']:
                gold_option = label
                break


        q['option_map'] = option_map
        q['gold_option'] = gold_option
        all_questions.append(q)

    return all_questions

def save_csv(questions: list, filepath: str):
    """
    保存为 CSV，每题一行
    """
    rows = []
    for idx, q in enumerate(questions):
        option_map = q.get("option_map")

        # ✅ 如果没有 option_map（Q3），就从 options 顺序构造
        if option_map is None:
            options = q.get("options", [])
            option_map = {
                "A": options[0] if len(options) > 0 else "",
                "B": options[1] if len(options) > 1 else "",
                "C": options[2] if len(options) > 2 else "",
                "D": options[3] if len(options) > 3 else "",
            }

        row = {
            "question_type": q.get("question_type", ""),
            "word": q.get("word", ""),
            "sense_id": q.get("sense_id", ""),
            "sentence": q.get("sentence", ""),
            "instruction": q.get("instruction", ""),
            "question": q.get("question", ""),
            "option_A": option_map.get("A", ""),
            "option_B": option_map.get("B", ""),
            "option_C": option_map.get("C", ""),
            "option_D": option_map.get("D", ""),
            "gold_text": q.get("gold_text", ""),
            "relation_type": q.get("relation_type", "")
        }

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"Saved {len(rows)} questions to {filepath}")
