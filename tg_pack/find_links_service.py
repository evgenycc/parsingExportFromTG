import re


def find_youtube_links(text):
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    matches = re.findall(pattern, text)
    links = []
    for video_id in matches:
        full_link = f'https://www.youtube.com/watch?v={video_id}'
        links.append(full_link.strip(":").strip())
    return links


def find_rutube_links(text):
    # Регулярное выражение для поиска ссылок Rutube
    rutube_pattern = re.compile(
        r'https?://rutube\.ru/video/[a-fA-F0-9]{32}/',
        re.IGNORECASE
    )
    links = rutube_pattern.findall(text)
    return links


def extract_vk_video_links(text):
    pattern = r'https?://vkvideo\.ru/video[-\w_]+'
    matches = re.findall(pattern, text)
    return matches


def find_links_excluding_platforms(text):
    url_pattern = r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    all_urls = re.findall(url_pattern, text)
    excluded_domains = [
        'youtube.com',
        'youtu.be',
        'rutube.ru',
        'vk.com/video',
        't.me'
    ]
    filtered_urls = []
    for url in all_urls:
        if not any(excluded in url for excluded in excluded_domains):
            filtered_urls.append(url.strip(":").strip())
    return filtered_urls
