from typing import List, Dict


def generate(
    word: str,
    sense_id: str,
    sentences_A: List[str],
    sentences_B: List[str],
    sense_label_A: str,
    sense_label_B: str,
    relation_type_zh: str
) -> List[Dict]:

    instruction_text = (
        "Instruction (Semantic Linkage).\n"
        "（a）意象图式（image schema）是人类在日常身体经验中形成的动态、抽象的认知结构。\n"
        "意象图式转换指的是在同一经验领域内，一个图式在认知层面发生系统性的重组或聚焦变化。\n"
        "（b）隐喻连接（metaphorical connection）是指通过结构映射，将具身体经验基础的始源域投射到抽象目标域。\n"
        "在本任务中，我们区分上述两种语义关联机制。\n"
    )

    options = [
        "语义 A 通过意象图式转换从概念 B 中衍生而来",
        "语义 A 通过隐喻连接从概念 B 中衍生而来",
        "语义 B 通过意象图式转换从概念 A 中衍生而来",
        "语义 B 通过隐喻连接从概念 A 中衍生而来"
    ]

    if relation_type_zh == "意象图式转换":
        gold_text = options[0]
        gold_option = "A"
    elif relation_type_zh == "隐喻连接":
        gold_text = options[1]
        gold_option = "B"
    else:
        raise ValueError(f"Unknown relation_type_zh: {relation_type_zh}")

    questions = []

    for idx, sent_A in enumerate(sentences_A):
        sent_B = sentences_B[idx % len(sentences_B)]

        question_text = (
            f"（多义字：“{word}”）在以下两个句子中：\n"
            f"（1）{sent_A}\n"
            f"（2）{sent_B}\n"
            "请判断该多义字在这两个句子中所体现的不同语义是通过哪一种语义关联机制建立的。\n"
            "（第一个例句中的多义字的语义为语义A，第二个的为语义B）"
        )

        # ✅ 每道题只保存这一对句子到 sentence 列
        questions.append({
            "question_type": "Q3",
            "word": word,
            "sense_id": sense_id,
            "instruction": instruction_text,
            "question": question_text,
            "options": options,
            "gold_text": gold_text,
            "gold_option": gold_option,
            "relation_type": relation_type_zh,
            "sentence": f"{sent_A}\n{sent_B}"  # 这里直接生成 sentence
        })

    return questions
