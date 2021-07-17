from baseCrawler import BaseCrawler

import re
from pyquery import PyQuery as pq


BASE_URL = 'https://www.kuaidaili.com/free/inha/{page}/'
MAX_PAGE = 300


class KuaidailiCrawler(BaseCrawler):
    """
    kuaidaili crawler, https://www.kuaidaili.com/
    """
    urls = [BASE_URL.format(page=page)   for page in range(1, MAX_PAGE + 1)]
    
    def parse(self, html):
        """
        parse html file to get proxies
        :return:
        """
        doc = pq(html)
        for item in doc('table tr').items():
            td_ip = item.find('td[data-title="IP"]').text()
            td_port = item.find('td[data-title="PORT"]').text()
            if td_ip and td_port:
                yield td_ip+':'+str(td_port)


if __name__ == '__main__':
    crawler = KuaidailiCrawler()
    for proxy in crawler.crawl():
        print(proxy)
