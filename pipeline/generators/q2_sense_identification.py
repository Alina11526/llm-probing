'''
import random

def generate(
    word: str,
    sense_id: str,
    sentences: list[str],
    word_meta: dict,
    sense_meta: dict,
    n: int | None = None,
):
    ...

    sense_info = sense_meta[word][sense_id]

    all_senses = list(sense_meta[word].keys())
    distractors = [s for s in all_senses if s != sense_id]

    

    if n is None:
        n = len(sentences)

    questions = []

    for sent in sentences[:n]:
        options = [sense_id] + random.sample(distractors, min(3, len(distractors)))
        random.shuffle(options)

        option_texts = [
            sense_meta[word][s]["label_zh"] for s in options
        ]

        questions.append({
            "question_type": "Q2",
            "word": word,
            "sense_id": sense_id,
            "sentence": sent,
            "options": option_texts,
            "gold_sense_id": sense_id
        })

    return questions
'''

# generators/q2_sense_identification.py

from typing import List, Dict

def generate(
    word: str,
    sense_id: str,
    sentences: List[str],
    word_meta: Dict,
    sense_meta: Dict,
    options_list: List[str],
    
) -> List[Dict]:
    """
    生成 Q2 题型原始题目字典（未打乱选项，未分配 ABC）。
    """
    instruction_text = (
        "Instruction (Sense).\n"
        "具体语义（sense）指的是一个多义词在给定语境中所实际表达的语义用法。\n"
    )

    questions = []

    for sent in sentences:
        question_dict = {
            "question_type": "Q2",
            "word": word,
            "sense_id": sense_id,
            "sentence": sent,
            "instruction": instruction_text,
            "question": f"（多义字：“{word}”）在下列句子中：“{sent}”，该多义字在该语境下所表达的具体语义（sense）是哪一个？",
            "options": options_list.copy(),  # 保留原始顺序
            "gold_sense_id": sense_id,
            "gold_text": options_list[0]  # 假设第一个选项就是正确答案文字
        }
        questions.append(question_dict)

    return questions
