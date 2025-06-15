# -*- coding: utf-8 -*-
# author: Seale
from async_retrying import retry
import math
import aiomysql
import asyncio
import aiohttp
import logging
from lxml import etree
import time
import re
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')


def fallback(*args, **kwargs):
    logging.warning(f'retry error -> argument:{args} | kw_argument:{kwargs}')


class MoDian:
    def __init__(self, pages=234):
        # 全部 all
        # 创意 idea
        # 预热 prehat
        # 众筹中 going
        # 众筹成功 success
        self.pages = pages
        self.headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.pool = 'aiomysql 连接池'

    async def entrance(self):
        loop = asyncio.get_event_loop()
        self.pool = await aiomysql.create_pool(
            host='127.0.0.1', port=3306,
            user='user', password='pwd',
            db='db_name', loop=loop)
        conn = aiohttp.TCPConnector(ssl=False)
        
        urls = [f'https://zhongchou.modian.com/all/top_comment/success/{page}' for page in range(1, self.pages + 1)]
        
        async with aiohttp.ClientSession(connector=conn, headers=self.headers) as session:
            project_list_tasks = [asyncio.create_task(self.fetch_list(session=session, url=url)) for url in urls]
            await asyncio.wait(project_list_tasks)
            logging.info('project list tasks is exec finish')
            
        self.pool.close()
        await self.pool.wait_closed()

    @retry(attempts=5, fallback=fallback)
    async def fetch_list(self, session, url):
        async with session.get(url=url) as response:
            text = await response.text(encoding='utf-8')
            logging.info(f'{url} response')
            await self.parse_list(text, session)

    async def parse_list(self, text, session):
        logging.info(f'parse url from list data')
        _etree = etree.HTML(text)
        detail_url = [url for url in _etree.xpath('//div[@class="pro_txt_field"]/a[1]/@href') if 'item' in url]
        if detail_url:
            detail_url_tasks = [asyncio.create_task(self.fetch_detail(session, url)) for url in detail_url]
            await asyncio.wait(detail_url_tasks)
            logging.info(f'find detail page url fetch all url int queue')

    @retry(attempts=5, fallback=fallback)
    async def fetch_detail(self, session, url):
        logging.info(f'detail {url} fetch')
        async with session.get(url=url) as response:
            text = await response.text(encoding='utf-8')
            await self.parse_detail(text, url, session)

    async def async_store(self, data, table):
        logging.info('insert data ....')
        try:
            sql_template = f'INSERT ignore INTO {table} ' \
                           f'({",".join(data[0].keys())})' \
                           f' VALUES ' \
                           f'({"".join(["%s," for _ in data[0]])[:-1]})'
        except:
            return
        insert_data = [tuple(record.values()) for record in data]
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.executemany(sql_template, insert_data)
                    await conn.commit()
                except:
                    logging.info('Duplicate entry')
                logging.info('insert data end....')

    async def parse_detail(self, text, url, session):
        _etree = etree.HTML(text)
        name = _etree.xpath('string(//h3[@class="title"])')
        team = _etree.xpath('string(//div[@class="name team clearfix"])')
        location = _etree.xpath('string(//span[@class="lower-string-submit"])')
        project_type = _etree.xpath('string(//p[@class="tags clearfix"]/span[3])')
        backer_money = _etree.xpath('string(//span[@backer_money])')
        goal_money = _etree.xpath('string(//span[@class="goal-money"])')
        percent = _etree.xpath('string(//span[@class="percent"])')
        try:
            begin_time = _etree.xpath('//div[@class="col2 remain-time"]/h3/@start_time')[0]
        except Exception as error:
            logging.info('begin time is none')
            begin_time = ''
        try:
            end_time = _etree.xpath('//div[@class="col2 remain-time"]/h3/@end_time')[0]
        except Exception as error:
            logging.info('end time is none')
            end_time = ''
        support_people = _etree.xpath('string(//div[@class="col3 support-people"]//span)')
        update_count = _etree.xpath('string(//li[@class="pro-gengxin"]/span)')
        optimistic = _etree.xpath('string(//li[@class="atten"])')
        comment_count = _etree.xpath('string(//a[@href="#comment"]/strong)')
        support_user = _etree.xpath('string(//li[@class="dialog_user_list support_user"]/span)')
        origin_id = _etree.xpath('//span[@backer_money]/@backer_money')[0]
        overview = {
            'origin_id': origin_id,
            'url': url,
            'name': name,
            'team': team,
            'location': location,
            'project_type': project_type,
            'backer_money': backer_money,
            'goal_money': goal_money,
            'percent': percent,
            'begin_time': begin_time,
            'end_time': end_time,
            'optimistic': optimistic,
            'support_people': support_people,
            'update_count': update_count,
            'comment_count': comment_count,
            'support_user': support_user
        }
        await self.async_store([overview], 'Project')
        try:
            order_post_id = _etree.xpath('//input[@name="order_post_id"]/@value')[0]
            await self.fetch_comment(origin_id, order_post_id, session)
        except:
            print(f'这种情况下,一般也不会有对应的情感词: url为{url}')
        print(overview)
        support_user_task = [asyncio.create_task(self.fetch_support_user(origin_id, page, session, 0))
                             for page in range(1, math.ceil(int(overview['support_people']) / 20) + 1)]
        await asyncio.wait(support_user_task)
        logging.info(f'{url} is crawl and store....')

    @retry(attempts=5, fallback=fallback)
    async def fetch_comment(self, origin_id, order_post_id, session):
        logging.info(f'support {origin_id}-{order_post_id} fetch')
        params = (
            ('post_id', order_post_id),
            ('type', ''),
            ('page', 1),
        )
        async with session.get('https://me.modian.com/order_rate/ajax_get_list',
                               params=params) as response:
            text = await response.text(encoding='utf-8')
            logging.info(f'{origin_id}-{order_post_id} response')
            await self.parse_rate_count(text, origin_id)

    async def parse_rate_count(self, text, origin_id):
        try:
            data = eval(re.findall('"rate_count":(.*?)}', text)[0] + '}')
            data['origin_id'] = origin_id
            await self.async_store([data], 'comment_score')
        except:
            return

    @retry(attempts=5, fallback=fallback)
    async def fetch_support_user(self, origin_id, page, session, count):
        if count < 3:
            logging.info(f'support {origin_id}-{page} fetch')
            params = (
                ('origin_id', origin_id),
                ('type', 'backer_list'),
                ('page', page),
                ('page_size', '20'),
            )
            async with session.get('https://zhongchou.modian.com/realtime/ajax_dialog_user_list',
                                   params=params) as response:
                text = await response.text(encoding='utf-8')
                logging.info(f'support {origin_id}-{page} response')
                await self.parse_support(text, origin_id, page, count, session)
        else:
            store_data = {
                'origin_id': origin_id,
                'page': page
            }
            await self.async_store([store_data], 'error')

    async def parse_support(self, text, origin_id, page, count, session):
        logging.info('parser support data')
        _tree = etree.HTML(text[40:].encode('utf-8').decode('unicode_escape').replace('\\', ''))
        user_id = _tree.xpath('//span[@class="add_gz toggle_follow"]/@data-user_id')
        user_name = [name.xpath('string(.)') for name in _tree.xpath('//span[@class="nick_name"]')]
        user_support = [support.xpath('string(.)') for support in _tree.xpath('//div[@class="name_bottom"]')]
        support_data = [{
            'user_id': user_id[index],
            'origin_id': origin_id,
            'user_name': user_name[index],
            'user_support': user_support[index]
        } for index in range(len(user_id))]
        if support_data:
            logging.info(f' support data parse end...{origin_id}-{page}-->{support_data}')
            await self.async_store(support_data, 'project_supporter')
            logging.info(f'support data store end')
        else:
            print(f're-get data from {origin_id} {page}')
            await self.fetch_support_user(origin_id, page, session, count + 1)


if __name__ == '__main__':
    s = time.time()
    MoDian_ins = MoDian()
    asyncio.run(MoDian_ins.entrance())
    print(time.time() - s)
