"""Main module."""

__author__ = """Mahir Rahman"""
__contact__ = 'kazi.mahir@stfc.ac.uk'
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import json

import requests
from stac.stac import STAC
import warnings


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
            self.loop_results(result)
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

    def loop_results(self, page: dict, collections: set = set([])):
        collections.update([item.get('collection') for item in page.get('features')])
        if len(collections) == len(self.catalog()):
            return list(collections)
        if page.get('links'):
            link = page.get('links')[-1]
            if link.get('rel') == 'next':
                response = requests.get(url=link.get('href'), verify=False)
                response = response.json()
                return self.loop_results(page=response, collections=collections)
        print(collections)
        return collections

    def queryables(self):
        response = requests.get(f"{self._url}/queryables", verify=False)
        return response.json()

    def collection_queryables(self, collection_id: str):
        response = requests.get(f"{self._url}/collections/{collection_id}/queryables", verify=False)
        return response.json()

    def conformance_classes(self):
        return self.Client.conformance
