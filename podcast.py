import re
import logging

class Podcast:
    title: str
    attention: list[str]
    transcription: list[str]
    audio: str
    publish_at: str


    def __init__(self, soup):
        self._p = re.compile("//(.*?)/traffic.megaphone.fm/(.*)\?updated=(.*)")
        self._pa = re.compile('(.*?) | 🔗')
        self._post_content = soup.find_all('section', class_="post-content")[0]
        self._soup = soup


    def parse(self):
        self._parse_publish_at()
        self._parse_title()
        self._parse_attention()
        self._parse_transcription()
        self._parse_audio()
        logging.info(f'播客页面 {self.title} 解析完毕')


    def _parse_title(self):
        title = self._soup.find_all('h2', class_='post-title')[0].text
        self.title = f'{self.publish_at} {title}'


    def _parse_publish_at(self):
        publish_at = self._soup.find_all('header', class_='post-header')[0].find_all('span', class_='muted')[0].text
        self.publish_at = self._pa.search(publish_at).group(1)


    def _parse_attention(self):
        attention_list = self._post_content.find_all('div', class_='disclaimer')
        attention_content_list = []
        for attention in attention_list:
            attention = self._clean_paragraph(attention.text)
            attention_content_list.append(attention)
        self.attention = attention_content_list


    def _parse_transcription(self):
        transcription_list = self._post_content.find_all('div', class_='transcription')
        timemark_list = self._post_content.find_all('div', class_='timemark-container')
        if len(timemark_list) != len(transcription_list):
            logging.warning('timemark list may not match transcription list')
        transcription_list = zip(transcription_list, timemark_list)
        transcription_content_list = []
        for transcription in transcription_list:
            timemark = transcription[1].find('a').get('href')
            transcription_content = self._clean_paragraph(transcription[0].text)
            transcription_content_list.append(f'{timemark}\n{transcription_content}\n')
        self.transcription = transcription_content_list


    def _clean_paragraph(self, paragraph):
        #paragraph = re.sub(r'\s+', '', paragraph)
        return ' '.join(paragraph.strip().replace('\n', '').replace('\t', '').split()) + '\n\n'


    def _parse_audio(self):
        audio = self._post_content.find_all('div', class_='audio-container')[0].find_all('audio')[0].find_all('a', class_='download-link')[0].get('href')
        audio_name = self._p.search(audio).group(2)
        audio = f'https://dcs.megaphone.fm/{audio_name}'
        self.audio = audio
