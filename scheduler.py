import time
import multiprocessing
from getter import Getter
from tester import Tester
from loguru import logger


#if IS_WINDOWS:
#    multiprocessing.freeze_support()

tester_process, getter_process, server_process = None, None, None


class Scheduler():
    """
    scheduler
    """    
    def run_tester(self):
        """
        run tester
        """       
        tester = Tester()
        loop = 0
        while True:
            logger.debug(f'tester loop {loop} start...')
            tester.run()
            loop += 1
            time.sleep(20)
    
    def run_getter(self):
        """
        run getter
        """        
        getter = Getter()
        loop = 0
        while True:
            logger.debug(f'getter loop {loop} start...')
            getter.run()
            loop += 1
            time.sleep(20)
      
    def run(self):
        global tester_process, getter_process, server_process
        try:
            logger.info('starting proxypool...')
            tester_process = multiprocessing.Process(target=self.run_tester)
            logger.info(f'starting tester, pid {tester_process.pid}...')
            tester_process.start()
            
         
            getter_process = multiprocessing.Process(target=self.run_getter)
            logger.info(f'starting getter, pid{getter_process.pid}...')
            getter_process.start()            
                       
            tester_process.join()
            getter_process.join()
         
        except KeyboardInterrupt:
            logger.info('received keyboard interrupt signal')
            tester_process.terminate()
            getter_process.terminate()         
        finally:
            # must call join method before calling is_alive
            tester_process.join()
            getter_process.join()
         
            logger.info(f'tester is {"alive" if tester_process.is_alive() else "dead"}')
            logger.info(f'getter is {"alive" if getter_process.is_alive() else "dead"}')            
            logger.info('proxy terminated')


if __name__ == '__main__':
    logger.add('log.txt',level=['info','warning'])
    logger.info('获取代理开始')    
    gett = Getter()
    gett.run()
    logger.info('测试代理开始')
    test = Tester()
    test.run()
    logger.info('全部结束')