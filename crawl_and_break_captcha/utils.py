"""
    Created by @namhainguyen2803 in 25/11/2023
"""

import re
def remove_diacritics(vietnamese_word):
    diacritic_chars = 'àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ'
    plain_chars = 'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyydAAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD'
    cleaned_word = ''.join(
        plain_chars[diacritic_chars.index(c)] if c in diacritic_chars else c for c in vietnamese_word)
    return cleaned_word

def map_to_vietnamese(animal_name):
    translation_dict = {
        "cow": "bò",
        "bird": "chim",
        "dog": "chó",
        "mouse": "chuột",
        "chicken": "gà",
        "pig": "heo",
        "tiger": "hổ",
        "cat": "mèo",
        "horse": "ngựa",
        "rabbit": "thỏ",
        "buffalo": "trâu",
        "duck": "vịt",
        "elephant": "voi"
    }
    return translation_dict.get(animal_name.lower(), "Translation not found")

def post_process_result(res):
    list_decision = list()
    num_question = 0
    for i in range(len(res)):
        num_question += 1
        for j in range(len(res[i])):
            list_decision.append([res[i][j]["label"], res[i][j]["score"], i])
    list_decision.sort(reverse=True, key=lambda x: x[1])
    used_answer = set()
    answered_yet = [False] * num_question
    question_answered = [''] * num_question
    for decision in list_decision:
        if answered_yet[decision[2]] == False:
            if decision[0] not in used_answer:
                question_answered[decision[2]] = decision[0]
                answered_yet[decision[2]] = True
                used_answer.add(decision[0])
    return question_answered

def extract_number(string):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", string)
    return float(numbers[0]) if numbers else None