import re
from pathlib import Path

from bs4 import BeautifulSoup

from tg_pack.parsers import parse


def main():
    link_page = input("path dir >>> ").replace("'", "").replace('"', '')
    files = [fl for fl in Path(link_page).iterdir() if Path(fl).is_file() and Path(fl).suffix.lower() == ".html"]
    for file in files:
        if (Path(file).parent / f"{Path(file).stem}.docx").exists():
            continue
        with open(file, "r", encoding="utf-8") as lp:
            html_cleaned = re.sub(r'<br\s*/?>', '\n', lp.read(), flags=re.IGNORECASE)
            soup = BeautifulSoup(html_cleaned, "lxml")
            parse(soup, Path(file).parent, Path(file).stem)


if __name__ == '__main__':
    main()
