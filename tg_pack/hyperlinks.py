from urllib.parse import quote

from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn


def add_file_hyperlink(paragraph, text, file_path, is_relative=True):
    """Добавляет гиперссылку на файл в параграф.
    Args:
        paragraph: Параграф для добавления ссылки
        text: Текст ссылки
        file_path: Путь к файлу (может быть относительным или абсолютным)
        is_relative: True - относительный путь, False - абсолютный путь
    """
    # Кодируем путь для URL
    if is_relative:
        # Для относительного пути, просто используем его как есть
        url_path = file_path.replace('\\', '/')
    else:
        # Для абсолютного пути, добавляем file://
        url_path = 'file:///' + quote(file_path.replace('\\', '/'))

    # Создаем элемент гиперссылки
    hyperlink = OxmlElement('w:hyperlink')

    # Добавляем relationship для ссылки
    part = paragraph.part
    r_id = part.relate_to(
        url_path,
        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
        is_external=True
    )

    # Устанавливаем атрибут r:id для ссылки
    hyperlink.set(qn('r:id'), r_id)

    # Создаем новый run ВНУТРИ гиперссылки
    run = OxmlElement('w:r')

    # Создаем элемент для текста (w:t)
    text_elem = OxmlElement('w:t')
    text_elem.text = text

    # Создаем элемент форматирования (w:rPr)
    rpr = OxmlElement('w:rPr')

    # Добавляем цвет (синий)
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0000FF')  # RGB в HEX: 0000FF = синий
    rpr.append(color)

    # Добавляем подчеркивание
    underline = OxmlElement('w:u')
    underline.set(qn('w:val'), 'single')
    rpr.append(underline)

    # Собираем структуру: run -> rpr + text
    run.append(rpr)
    run.append(text_elem)

    # Добавляем run в гиперссылку
    hyperlink.append(run)

    # Добавляем гиперссылку в параграф
    paragraph._p.append(hyperlink)

    return hyperlink


def add_hyperlink(paragraph, url, text):
    """Добавляет активную гиперссылку в абзац Word.
    Args:
       paragraph: Параграф для добавления ссылки
       url: Ссылка
       text: Текст ссылки
    """
    p = paragraph._p
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), paragraph.part.relate_to(
        url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True
    ))

    run = OxmlElement('w:r')
    rpr = OxmlElement('w:rPr')

    # Стили: синий цвет и подчёркивание
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0000FF')
    underline = OxmlElement('w:u')
    underline.set(qn('w:val'), 'single')

    rpr.append(color)
    rpr.append(underline)
    run.append(rpr)

    text_elem = OxmlElement('w:t')
    text_elem.text = text
    run.append(text_elem)

    hyperlink.append(run)
    p.append(hyperlink)
