import logging
import os
import uuid
import requests
from fpdf import FPDF
from podcast import Podcast

class PodcastPDF:
    _podcast: Podcast
    _download_folder: str


    def __init__(self, podcast, download_folder):
        self._podcast = podcast

        self._download_folder = f'{download_folder}/{self._podcast.title}'
        if not os.path.exists(self._download_folder):
            os.makedirs(self._download_folder)

        self._runtime_folder = './runtime'
        if not os.path.exists(self._runtime_folder):
            os.makedirs(self._runtime_folder)


    def download(self):
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font('Arial', size=16, style='B')
        pdf.multi_cell(0, 5, txt='[Stuff You Should Know]\n\n' + self._podcast.title)
        pdf.multi_cell(0, 5, txt='\n')

        pdf.set_font("Arial", size=14, style='U')
        link_text = '[DOWNLOAD AUDIO]'
        pdf.text(x=11, y=32, txt=link_text)
        pdf.link(x=11, y=27, w=pdf.get_string_width(link_text), h=5, link=self._podcast.audio)

        cover_path = self._download_cover()
        if cover_path is None:
            pdf.image(name='./default_cover.jpeg', type='JPG', x=11, y=38, w=188, h=94)
        else:
            pdf.image(name=cover_path, type='JPG', x=11, y=38, w=188, h=94)
            self._release_cover(cover_path)

        pdf.set_xy(10, 140)
        pdf.set_font('Arial', size=16, style='B')
        pdf.multi_cell(0, 5, txt='Transcription:\n\n')

        pdf.set_font('Arial', size=14)
        for tr in self._podcast.transcription:
            pdf.multi_cell(0, 7, txt=tr)

        pdf.set_font('Arial', size=16, style='B')
        pdf.multi_cell(0, 5, txt='Attention:\n\n')

        pdf.set_font('Arial', size=14, style='I')
        for att in self._podcast.attention:
            pdf.multi_cell(0, 5, txt=att, align='C')

        pdf_filename = f'{self._download_folder}/{self._podcast.title}.pdf'
        try:
            pdf.output(pdf_filename)
            logging.info(f'播客 {self._podcast.title} 转PDF成功')
            pdf.close()
        except UnicodeEncodeError as e:
            logging.error(f'播客转PDF失败, PDF文件名({pdf_filename})不合法, caused by: {str(e)}\n使用UUID替代...')
            pdf_filename = uuid.uuid4().hex
            pdf.output(pdf_filename)
            logging.info(f'播客 {self._podcast.title}({pdf_filename}) 转PDF成功')
        finally:
            pdf.close()


    def _download_cover(self):
        try:
            response = requests.get('https://picsum.photos/600/300', timeout=3)
            status_code = response.status_code
            if status_code != 200:
                logging.error(f'播客封面图下载失败, HTTP status code: {status_code}')
                return None

            cover_path = f'./runtime/{uuid.uuid4().hex}.jpeg'
            with open(cover_path, 'wb') as f:
                f.write(response.content)
            return cover_path
        except Exception as e:
            logging.info(f'播客封面图下载失败, caused by: {str(e)}')
            return None


    def _release_cover(self, cover_path):
        os.remove(cover_path) if os.path.exists(cover_path) else None


    def download_audio(self):
        try:
            response = requests.get(self._podcast.audio, timeout=3)
            status_code = response.status_code
            if response.status_code != 200:
                logging.error(f'播客配套音频下载失败, HTTP status code: {status_code}')
                return

            with open(f'{self._download_folder}/{self._podcast.title}.mp3', 'wb') as f:
                f.write(response.content)
        except Exception as e:
            logging.error(f'播客配套音频下载失败, caused by: {str(e)}')