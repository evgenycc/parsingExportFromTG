import re
import secrets
import shutil
import string
from pathlib import Path


def transliterate_cyrillic(text):
    """
    Заменяет кириллические буквы на латинские по стандартной схеме.
    Не трогает цифры, знаки препинания и уже латинские символы.
    """
    # Словарь транслитерации
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya',

        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'E', 'Ж': 'Zh', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
        'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    return ''.join(translit_map.get(char, char) for char in text)


def generate_code():
    chars = string.ascii_uppercase + string.digits
    password = ''.join(secrets.choice(chars) for _ in range(5))
    return password


def copy_file_name(filename, path, val, folders):
    cleaned = re.sub(r'[^a-zA-Zа-яА-Я0-9_.()\- ]', '', filename)
    cleaned = cleaned.rstrip(' .').strip("_").strip().replace(" ", "_")
    cleaned = transliterate_cyrillic(cleaned)
    code = generate_code()
    cleaned = f"{Path(cleaned).stem} [{code}]{Path(cleaned).suffix}"
    v_path = Path(path) / folders
    v_path.mkdir(exist_ok=True)
    if (Path(path) / val).exists():
        if not (v_path / cleaned).exists():
            shutil.copy(str(Path(path) / val), str(v_path / cleaned))
            (Path(path) / val).unlink()
        return str(Path(folders) / cleaned)
    else:
        for fls in v_path.iterdir():
            if Path(cleaned).stem.split("[")[0].strip() == fls.stem.split("[")[0].strip():
                return str(Path(folders) / Path(fls).name)
        return None
