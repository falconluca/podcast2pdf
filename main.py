import os
import logging
import sys

from collector import PodcastCollector
from pdf import PodcastPDF

if __name__ == '__main__':
    fmt = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)

    try:
        page_num = int(os.getenv('FETCH_PAGE_NUM'))
    except ValueError as e:
        logging.error(f'FETCH_PAGE_NUM必须是一个1-40的整数{str(e)})')
        sys.exit(-1)
    if page_num is None or page_num <= 0:
        page_num = 1
    elif page_num > 40:
        page_num = 40

    podcast_collector = PodcastCollector()
    podcast_collector.set_fetch_page_num(page_num)
    podcasts = podcast_collector.fetch()
    for podcast in podcasts:
        podcast.parse()
        podcast_pdf = PodcastPDF(podcast, './samples/Stuff You Should Know')
        podcast_pdf.download()
        podcast_pdf.download_audio()
    logging.info(f'播客解析完毕, {podcast_collector.page_num} page, total: {len(podcasts)}')



