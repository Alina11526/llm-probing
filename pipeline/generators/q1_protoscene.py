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
    生成 Q1（Protoscene）题型的原始题目字典
    - 不打乱选项
    - 不分配 ABC
    """
    instruction_text = (
        "Instruction (Protoscene).\n"
        "初始含义（protoscene）指的是一个词项在人类认知中所对应的最基本、"
        "具身体经验基础的空间构型，它为该词的其他语义用法提供概念基础。\n"
    )

    questions = []

    for sent in sentences:
        question_dict = {
            "question_type": "Q1",
            "word": word,
            "sense_id": sense_id,  # 仍然保留 sense_id，便于统一分析
            "sentence": sent,
            "instruction": instruction_text,
            "question": (
                f"（多义字：“{word}”）在下列句子中：“{sent}”，"
                f"请判断该多义字所对应的原型语义（protoscene / core embodied meaning）是哪一个。"
            ),
            "options": options_list.copy(),
            "gold_sense_id": "PROTO",          # 明确标记为 protoscene
            "gold_text": options_list[0]       # 约定：第一个选项永远是 protoscene
        }
        questions.append(question_dict)

    return questions
