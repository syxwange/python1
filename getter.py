from loguru import logger
from proxyRedis import RedisClient
from crawlers import __all__ as crawlers_cls


PROXY_NUMBER_MAX=10000
class Getter(object):
    """
    getter of proxypool
    """
    
    def __init__(self):
        """
        init db and crawlers        """
        self.redis = RedisClient()
        self.crawlers_cls = crawlers_cls
        self.crawlers = [crawler_cls() for crawler_cls in self.crawlers_cls]
    
    def is_full(self):
        """
        if proxypool if full
        return: bool
        """
        return self.redis.count() >= PROXY_NUMBER_MAX
    
    @logger.catch
    def run(self):
        """
        run crawlers to get proxy
        :return:
        """
        if self.is_full():
            logger.info('数据库中ip数量到达最大值，不爬取IP')
            return
        for crawler in self.crawlers:
            logger.info(f'crawler {crawler} to get proxy')
            for proxy in crawler.crawl():
                self.redis.add(proxy)


if __name__ == '__main__':
    getter = Getter()
    getter.run()
