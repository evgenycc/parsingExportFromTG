import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from linkpreview import link_preview

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}


def get_yt_preview(path, video_url):
    query = urlparse(video_url)
    video_id = None
    if query.hostname == 'youtu.be':
        video_id = query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            video_id =  p['v'][0]
        if query.path[:7] == '/embed/':
            video_id =  query.path.split('/')[2]
        if query.path[:3] == '/v/':
            video_id =  query.path.split('/')[2]
    if video_id:
        sizes = ['mqdefault', 'default', 'hqdefault', 'sddefault']
        for size in sizes:
            url = f'https://i.ytimg.com/vi/{video_id}/{size}.jpg'
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                with open(Path(path) / 'preview.jpg', 'wb') as f:
                    f.write(response.content)
                return str(Path(path) / 'preview.jpg')
    return None


def get_rt_preview(path, video_url):
    # Извлекаем ID видео из URL
    parsed_url = urlparse(video_url)
    video_id = parse_qs(parsed_url.query).get('id', [None])[0]

    if not video_id:
        # Если ID не найден в параметрах, берем из пути
        path_parts = parsed_url.path.strip('/').split('/')
        video_id = path_parts[-1]

    # Формируем URL для получения информации о видео
    api_url = f'https://rutube.ru/api/video/{video_id}'

    try:
        # Получаем данные о видео
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Получаем URL превью
        thumbnail_url = data.get('thumbnail_url')

        if thumbnail_url:
            # Загружаем изображение превью
            preview_response = requests.get(thumbnail_url, headers=headers, timeout=10)
            preview_response.raise_for_status()
            with open(Path(path) / 'preview.webp', 'wb') as f:
                f.write(preview_response.content)
            return str(Path(path) / 'preview.webp')
        return None
    except requests.RequestException as e:
        return None


def get_vk_video_thumbnail(path, video_url, output_filename='vk_preview.jpg'):
    try:
        response = requests.get(video_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Парсим HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Ищем Open Graph тег og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = og_image['content']
            return download_vk_image(path, img_url, output_filename)

        # 2. Ищем тег meta с name="image"
        meta_image = soup.find('meta', attrs={'name': 'image'})
        if meta_image and meta_image.get('content'):
            img_url = meta_image['content']
            return download_vk_image(path, img_url, output_filename)

        # 3. Ищем изображение в теге <img> с классом, содержащим "thumb" или "preview"
        img_tag = soup.find('img', class_=re.compile(r'thumb|preview', re.I))
        if img_tag and img_tag.get('src'):
            img_url = img_tag['src']
            return download_vk_image(path, img_url, output_filename)

        # 4. Ищем URL изображения в JavaScript-коде (наиболее надёжный способ для VK)
        script_text = soup.find('script', text=re.compile(r'photo_800'))
        if script_text:
            # Ищем строку вида photo_800: "https://..."
            match = re.search(r'photo_800\s*:\s*"([^"]+)"', script_text.text)
            if match:
                img_url = match.group(1)
                return download_vk_image(path, img_url, output_filename)
        return None

    except requests.RequestException:
        return None
    except Exception:
        return None


def download_vk_image(path, img_url, filename):
    try:
        response = requests.get(img_url, stream=True, headers=headers, timeout=10)
        response.raise_for_status()

        # Определяем расширение файла
        ext = Path(img_url).suffix.lower().split("?")[0].strip()
        if not ext or ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            ext = '.jpg'

        filepath = filename if filename.endswith(ext) else filename + ext

        with open(Path(path) / filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return str(Path(path) / filepath)
    except Exception:
        return None


def get_vk_preview(path, video_url):
    result = get_vk_video_thumbnail(path, video_url)
    if result:
        return result
    return None


def get_other_preview(path, url, filename="preview"):
    try:
        preview = link_preview(url, headers=headers, initial_timeout=10, receive_timeout=10, parser="lxml")
        if preview:
            img_url = preview.absolute_image
            title = preview.title
            filepath = ""
            try:
                response = requests.get(img_url, stream=True, timeout=10, headers=headers)
                response.raise_for_status()
                ext = Path(img_url).suffix.lower().split("?")[0].strip()
                if not ext or ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                    ext = '.jpg'
                filepath = filename if filename.endswith(ext) else filename + ext
                with open(Path(path) / filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return str(Path(path) / filepath), title
            except Exception:
                (Path(path) / filepath).unlink()
                return None, None
        return None, None
    except Exception:
        return None, None
