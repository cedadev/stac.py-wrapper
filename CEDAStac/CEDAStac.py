"""Main module."""

__author__ = """Mahir Rahman"""
__contact__ = 'kazi.mahir@stfc.ac.uk'
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import json
import requests
from stac.stac import STAC
import warnings

import asyncio
import aiohttp

from CEDAStac.utils import async_search


class CEDAStacClient:
    """
    This class implements a Python API Client for STAC utilising stac.py
    """

    def __init__(self):
        self._url = "https://stac-elasticsearch-master.130.246.131.9.nip.io"
        self.Client = STAC(url=self._url, verify=False)
        self._headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        warnings.simplefilter('ignore')

    def catalog(self):
        return self.Client.catalog

    def get_collections(self):
        collections = self.Client.collections
        collections = list(collections.values())
        return collections

    def get_collection(self, collection_id: str):
        return self.Client.collection(collection_id=collection_id)

    def get_item(self, collection_id: str, item_id: str, **query):
        collection = self.get_collection(collection_id=collection_id)
        items = collection.get_items(item_id=item_id, filter=query)
        return items

    def get_itemcollection(self, collection_id: str, **query):
        collection = self.get_collection(collection_id=collection_id)
        itemcollection = collection.get_items(filter=query)
        return itemcollection

    def search(self, freetext: str = None, doctype: str = 'item', **query):
        if freetext:
            return self.search(q=freetext, doctype=doctype, **query)

        if 'properties' in query.keys():
            filter = query.pop('properties', None)
            return self.post_search(query=query, filter=filter, doctype=doctype)

        if {'bbox', 'intersects'}.intersection(query.keys()):
            return self.post_search(query=query, doctype=doctype)

        result = self.Client.search(filter=query)
        if doctype == 'collection':
            return asyncio.run(async_search(result))
        else:
            return result

    def post_search(self, query: dict, filter: dict = None, doctype: str = 'item'):
        if filter:
            query['filter'] = filter
        data = json.dumps(query)
        response = requests.post(url=f"{self._url}/search", data=data, verify=False, headers=self._headers)
        result = response.json()
        if doctype == 'collection':
            self.loop_results(result)
        else:
            return result

    def queryables(self):
        response = requests.get(f"{self._url}/queryables", verify=False)
        return response.json()

    def collection_queryables(self, collection_id: str):
        response = requests.get(f"{self._url}/collections/{collection_id}/queryables", verify=False)
        return response.json()

    def conformance_classes(self):
        return self.Client.conformance
