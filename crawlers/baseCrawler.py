from retrying import retry
import requests
from loguru import logger 
from fake_headers import Headers
import time

GET_TIMEOUT=10

class BaseCrawler(object):
    urls = []

    @retry(stop_max_attempt_number=3, retry_on_result=lambda x: x is None, wait_fixed=2000)
    def fetch(self, url, **kwargs):
        try:
            headers = Headers(headers=True).generate()
            kwargs.setdefault('timeout', GET_TIMEOUT)
            kwargs.setdefault('verify', False)
            kwargs.setdefault('headers', headers)
            response = requests.get(url ,**kwargs)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                return response.text
        except requests.ConnectionError:
            return

    @logger.catch
    def crawl(self):
        """
        crawl main method
        """
        for url in self.urls:
            logger.debug(f'fetching {url}')
            html = self.fetch(url)
            time.sleep(.5)
            for proxy in self.parse(html):
                #logger.debug(f'fetched proxy {proxy} from {url}')
                yield proxy

if __name__=='__main__':
    pass