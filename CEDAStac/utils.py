import asyncio
import warnings
import math

import aiohttp

warnings.simplefilter('ignore')


async def async_search(page: dict):
    pages = math.ceil(page.get('context').get('result_count') / page.get('context').get('limit'))
    url = page.get('links')[0].get('href')[:-1]

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        tasks = []
        for i in range(pages):
            task = asyncio.ensure_future(get_page_data(session, f"{url}{i + 1}"))
            tasks.append(task)

        collections_list = await asyncio.gather(*tasks)
        collection_set = set([])
        for collections in collections_list:
            collection_set.update(collections)
        return list(collection_set)


async def get_page_data(session, url):
    async with session.get(url) as response:
        result_data = await response.json()
        return get_item_collections(result_data)


def get_item_collections(result_data):
    collections = set([])
    collections.update([item.get('collection') for item in result_data.get('features')])
    return list(collections)
