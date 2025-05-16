def local_save(img_bytes: bytes, name: str):
    name = name.strip().replace(" ", "_")
    path = f"images/{name}.jpg"
    
    with open(path, "wb") as f:
        f.write(img_bytes)
        
    return path, name


def transliterate(text: str, direction='en2ru'):
    en2ru = {
        'a': 'а', 'b': 'б', 'c': 'ц', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'х',
        'i': 'и', 'j': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п',
        'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'v': 'в', 'w': 'в', 'x': 'кс', 'y': 'ы',
        'z': 'з', 'sh': 'ш', 'ch': 'ч', 'zh': 'ж', 'ya': 'я', 'yu': 'ю'
    }
    
    ru2en = {v: k for k, v in en2ru.items() if k not in ['sh', 'ch', 'zh', 'ya', 'yu']}
    ru2en.update({'ш': 'sh', 'ч': 'ch', 'ж': 'zh', 'я': 'ya', 'ю': 'yu'})

    result = ""
    i = 0
    text = text.lower()

    if direction == 'en2ru':
        while i < len(text):
            if i + 1 < len(text) and text[i:i+2] in en2ru:
                result += en2ru[text[i:i+2]]
                i += 2
            else:
                result += en2ru.get(text[i], text[i])
                i += 1
    elif direction == 'ru2en':
        while i < len(text):
            result += ru2en.get(text[i], text[i])
            i += 1

    return result

