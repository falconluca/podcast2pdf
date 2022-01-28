import logging
import requests
from bs4 import BeautifulSoup
from podcast import Podcast

class PodcastCollector:
    page_num: int = None


    def __init__(self):
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        }


    def set_fetch_page_num(self, page_num):
        self.page_num = page_num


    def fetch(self):
        if self.page_num is None:
            logging.error('未设置播客抓取页')
            return []

        podcast_urls = []
        for page in range(1, self.page_num+1):
            response = requests.get(f'https://www.podgist.com/stuff-you-should-know/partials/{page}.html')
            status_code = response.status_code
            if status_code != 200:
                logging.warning(f'page({page}) 抓取失败, HTTP Status code: {status_code}')
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            podcast_type_list = soup.find_all('span')
            urls = soup.find_all('a')

            if len(podcast_type_list) != len(urls):
                logging.warning(f'播客类型列表的大小({len(podcast_type_list)})无法与播客地址列表的大小({len(urls)})相匹配')
            podcast_page = zip(podcast_type_list, urls)

            for podcast_url in podcast_page:
                p_type = podcast_url[0]['class']
                if 'icon-ghost' in p_type and 'icon-transcribed' in p_type:
                    podcast_urls.append(podcast_url[1].get('href'))

        podcasts = []
        for podcast_url in podcast_urls:
            podcast = self.fetch_by_url(podcast_url)
            if podcast is None:
                continue
            podcasts.append(podcast)
        logging.info(f'播客页面抓取完毕, page: {self.page_num}, total: {len(podcasts)}')
        return podcasts


    def fetch_by_url(self, url):
        response = requests.get(f'https://www.podgist.com{url}', headers=self._headers)
        status_code = response.status_code
        if status_code != 200:
            logging.warning(f'播客页面抓取失败, HTTP status code: {status_code}')
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        return Podcast(soup)

