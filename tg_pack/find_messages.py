import re

from tg_pack.hyperlinks import add_hyperlink


def from_name_find(message):
    if from_name := message.find("div", class_="from_name"):
        return from_name.text.strip()
    return None


def reply_to_find(message, soup):
    if reply_to := message.find("div", class_="reply_to details"):
        reply_to_mess = reply_to.find("a")
        if reply_to_mess:
            reply_to_mess = reply_to_mess["href"].split("_")[-1]
        mess_reply = soup.find("div", id=reply_to_mess)
        if mess_reply:
            mess_text = mess_reply.find("div", class_="text")
            mess_video_file = mess_reply.find("a", class_="video_file_wrap clearfix pull_left")
            mess_photo = mess_reply.find("a", class_="photo_wrap clearfix pull_left")
            for mess_r in [mess_text, mess_photo, mess_video_file]:
                if mess_r:
                    if mess_r == mess_text:
                        return mess_r.text.strip()
                    return mess_r["href"]
    return None


def text_find(message):
    media_wrap = message.find("div", class_="media_wrap clearfix")
    if text := message.find("div", class_="text"):
        if links := text.find_all("a"):
            text = text.text.strip()
            for link in links:
                lnk = f"{link.text.strip()}: {link['href']}"
                text += f'\n{lnk}'
            return text.strip()
        return text.text.strip()
    if poll := media_wrap.find("div", class_="media_poll"):
        poll_struct = []
        if question := poll.find("div", class_="question bold"):
            poll_struct.append(question.text.strip())
        if details := poll.find("div", class_="details"):
            poll_struct.append(details.text.strip())
        if answers := poll.find_all("div", class_="answer"):
            for answer in answers:
                poll_struct.append(answer.text.strip())
        if total_details := poll.find("div", class_="total details"):
            poll_struct.append(total_details.text.strip())
        if poll_struct:
            return "\n".join(poll_struct)
    return None


def day_message_find(message):
    if date_mess := message.find("div", class_="pull_right date details"):
        return f'{date_mess["title"].split()[0].strip()} {date_mess["title"].split()[1].strip()}'
    return None


def media_wrap_find(message):
    classes = ["video_file_wrap clearfix pull_left", "photo_wrap clearfix pull_left",
               "media clearfix pull_left block_link media_file",
               "media clearfix pull_left block_link media_audio_file",
               "media clearfix pull_left block_link media_voice_message",
               "media clearfix pull_left block_link media_video"]
    if media_wrap := message.find("div", class_="media_wrap clearfix"):
        for cls in classes:
            if media := media_wrap.find("a", class_=cls):
                return media["href"]
    return None


def process_text_with_links(doc, text):
    """
    Обрабатывает текст, добавляя обычные фрагменты и активные ссылки.
    :param doc: Объект Document
    :param text: текст с URL
    """
    url_pattern = r'(https?://[^\s]+)'
    parts = re.split(url_pattern, text)
    seen_urls = set()

    for part in parts:
        if re.match(url_pattern, part):
            clean_url = part.rstrip(':,.!?;')
            if clean_url not in seen_urls:
                p = doc.add_paragraph()
                add_hyperlink(p, clean_url, clean_url)
                seen_urls.add(clean_url)  # Помечаем как добавленную
        else:
            if part.strip():
                doc.add_paragraph(part.strip())
