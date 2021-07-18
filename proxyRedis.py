import redis
from random import choice
from loguru import logger

REDIS_CLIENT_VERSION = redis.__version__
IS_REDIS_VERSION_2 = REDIS_CLIENT_VERSION.startswith('2.')
PROXY_SCORE_MAX = 100
PROXY_SCORE_MIN = 0
PROXY_SCORE_INIT = 10
REDIS_KEY = 'proxies'


class PoolEmptyException(Exception):
    def __str__(self):
        """
        proxypool is used out
        :return:
        """
        return repr('no proxy in proxypool')


class RedisClient(object):
    """    
    """
    def __init__(self,host='127.0.0.1',port =6379,password=None,db=0,**kwargs) -> None:
        self.db = redis.StrictRedis(host=host,port=port,password=password,db=db,decode_responses=True, **kwargs)

    def is_valid_proxy(self,data):
        if data.__contains__(':'):
            ip = data.split(':')[0]
            port = data.split(':')[1]
            return self.is_ip_valid(ip) and port.isdigit()
        else:
            return self.is_ip_valid(data)

    def is_ip_valid(SELF,ip):
        a = ip.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    def add(self,proxy,score=PROXY_SCORE_INIT)->int:
        """
        """
        if not self.is_valid_proxy(proxy):
            logger.info(f'invalid proxy {proxy}, throw it')
            return
        if self.db.zscore(REDIS_KEY, proxy) is None:            
            return self.db.zadd(REDIS_KEY, {proxy : score})
        
    def random(self):
        """
  
        """
        # try to get proxy with max score
        proxies = self.db.zrangebyscore(REDIS_KEY, PROXY_SCORE_MAX , PROXY_SCORE_MAX)
        if len(proxies):
            return choice(proxies)
        # else get proxy by rank
        proxies = self.db.zrevrange(REDIS_KEY, PROXY_SCORE_MIN , PROXY_SCORE_MAX)
        if len(proxies):
            return choice(proxies)
        # else raise error
        raise PoolEmptyException
    
    def decrease(self, proxy) -> int:
        """
        decrease score of proxy, if small than PROXY_SCORE_MIN, delete it
        :param proxy: proxy
        :return: new score
        """
        self.db.zincrby(REDIS_KEY, -1, proxy)
        score = self.db.zscore(REDIS_KEY, proxy)
        logger.info(f'{proxy} score decrease 1, current {score}')
        if score <= PROXY_SCORE_MIN:
            logger.info(f'{proxy} current score {score}, remove')
            self.db.zrem(REDIS_KEY, proxy)

    def max(self, proxy) -> int:
        """
        set proxy to max score
        :param proxy: proxy
        :return: new score
        """
        logger.info(f'{proxy} is valid, set to {PROXY_SCORE_MAX}')        
        return self.db.zadd(REDIS_KEY, {proxy: PROXY_SCORE_MAX})
    
    def count(self):
        """
        get count of proxies
        :return: count, int
        """
        return self.db.zcard(REDIS_KEY)

    def getValidproxies(self):
        """
        get count of proxies
        :return: count, int
        """
        return   self.db.zrangebyscore(REDIS_KEY, PROXY_SCORE_MAX , PROXY_SCORE_MAX)

    def all(self):
        """
        get all proxies
        :return: list of proxies
        """
        return self.db.zrangebyscore(REDIS_KEY, PROXY_SCORE_MIN, PROXY_SCORE_MAX)

    def batch(self, cursor, count):
        """
        get batch of proxies
        :param cursor: scan cursor
        :param count: scan count
        :return: list of proxies
        """
        return self.db.zscan(REDIS_KEY, cursor, count=count)
     
