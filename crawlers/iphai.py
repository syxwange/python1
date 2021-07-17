from baseCrawler import BaseCrawler

import re


BASE_URL = 'http://www.iphai.com/'

class IPHaiCrawler(BaseCrawler):
    """
    iphai crawler, http://www.iphai.com/打不开了
    """
    urls = [BASE_URL]
    ignore = True
    
    def parse(self, html):
        """
        parse html file to get proxies
        :return:
        """
        find_tr = re.compile('<tr>(.*?)</tr>', re.S)
        trs = find_tr.findall(html)
        for s in range(1, len(trs)):
            find_ip = re.compile('<td>\s+(\d+\.\d+\.\d+\.\d+)\s+</td>', re.S)
            re_ip_address = find_ip.findall(trs[s])
            find_port = re.compile('<td>\s+(\d+)\s+</td>', re.S)
            re_port = find_port.findall(trs[s])
            for address, port in zip(re_ip_address, re_port):
                proxy = address.strip()+':'+(port.strip())
                yield proxy

if __name__ == '__main__':
    crawler = IPHaiCrawler()
    for proxy in crawler.crawl():
        print(proxy)

