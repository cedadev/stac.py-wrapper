"""Main module."""

__author__ = """Mahir Rahman"""
__contact__ = 'kazi.mahir@stfc.ac.uk'
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

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
        warnings.simplefilter('ignore')

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

    def search(self, **query):
        return self.Client.search(query)

    def queryables(self):
        response = requests.get(f"{self._url}/queryables")
        return response.json()

    def collection_queryables(self, collection_id: str):
        response = requests.get(f"{self._url}/collections/{collection_id}/queryables")
        return response.json()

    def conformance_classes(self):
        return self.Client.conformance
