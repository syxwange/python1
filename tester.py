import asyncio
import aiohttp
from loguru import logger

from proxyRedis import RedisClient
from aiohttp import ClientProxyConnectionError, ServerDisconnectedError, ClientOSError, ClientHttpProxyError
from asyncio import TimeoutError
import requests

# definition of tester
TEST_URL = 'http://www.baidu.com'
IP_URL = 'https://httpbin.org/ip'
TEST_TIMEOUT = 5
TEST_BATCH =  20
# only save anonymous proxy
TEST_ANONYMOUS = True
# TEST_HEADERS = env.json('TEST_HEADERS', {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
# })
TEST_VALID_STATUS = [200, 206, 302]


EXCEPTIONS = (
    ClientProxyConnectionError,
    ConnectionRefusedError,
    TimeoutError,
    ServerDisconnectedError,
    ClientOSError,
    ClientHttpProxyError,
    AssertionError
)


class Tester(object):
    """
    tester for testing proxies in queue
    """
    
    def __init__(self):
        """
        init redis
        """
      
        self.redis = RedisClient()
        self.loop = asyncio.get_event_loop()
        self.origin_ip = requests.get(IP_URL).json()['origin']
       
    async def testBD(self, proxy):
        """
        test single proxy
        :param proxy: Proxy object
        :return:
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                #logger.debug(f'testing {proxy}')
                # if TEST_ANONYMOUS is True, make sure that
                # the proxy has the effect of hiding the real IP
                if TEST_ANONYMOUS:                    
                    async with session.get(IP_URL, proxy=f'http://{proxy}', timeout=TEST_TIMEOUT) as response:
                        resp_json = await response.json()
                        anonymous_ip = resp_json['origin']
                    assert self.origin_ip != anonymous_ip
                    assert proxy.split(':')[0] == anonymous_ip
                async with session.get(TEST_URL, proxy=f'http://{proxy}', timeout=TEST_TIMEOUT,
                                       allow_redirects=False) as response:
                    if response.status in TEST_VALID_STATUS:
                        self.redis.max(proxy)
                        logger.debug(f'proxy {proxy} is valid, set max score')
                    else:
                        self.redis.decrease(proxy)
                        logger.debug(f'proxy {proxy} is invalid, decrease score')
            except EXCEPTIONS as e:
                self.redis.decrease(proxy)                
                #logger.debug(f'proxy {proxy} is invalid in exceptions, decrease score')

    async def testIP(self, proxy):
        """
        test single proxy
        :param proxy: Proxy object
        :return:
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                #logger.debug(f'testing {proxy}')
                # if TEST_ANONYMOUS is True, make sure that
                # the proxy has the effect of hiding the real IP
                if TEST_ANONYMOUS:                    
                    async with session.get(IP_URL, proxy=f'http://{proxy}', timeout=TEST_TIMEOUT) as response:
                        if response.status in TEST_VALID_STATUS:
                            resp_json = await response.json()
                            anonymous_ip = resp_json['origin']
                            assert self.origin_ip != anonymous_ip
                            assert proxy.split(':')[0] == anonymous_ip
                            self.redis.max(proxy)
                            logger.debug(f'proxy {proxy} is valid, set max score')    
                        else:
                            self.redis.decrease(proxy)
                            logger.debug(f'proxy {proxy} is invalid, decrease score')
            except EXCEPTIONS as e:
                self.redis.decrease(proxy)                
                #logger.debug(f'proxy {proxy} is invalid in exceptions, decrease score')
    
    @logger.catch
    def run(self):
        """
        test main method
        :return:
        """
        # event loop of aiohttp
        logger.info('stating tester...')
        count = self.redis.count()
        logger.debug(f'{count} proxies to test')
        cursor = 0
        while True:
            logger.debug(f'testing proxies use cursor {cursor}, count {TEST_BATCH}')
            cursor, proxies = self.redis.batch(cursor, count=TEST_BATCH)
            if proxies:
                tasks = [self.testIP(proxy) for proxy,_ in proxies]
                self.loop.run_until_complete(asyncio.wait(tasks))
            if not cursor:
                break


if __name__ == '__main__':
    tester = Tester()
    tester.run()


