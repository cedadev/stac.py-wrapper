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

from client.utils import async_search


class StacPyClient:
    """
    This class implements a Python API Client for STAC utilising stac.py.

    :param url: URL for the Root STAC Catalog.
    """

    def __init__(self, url=str):
        """
        Create a STAC client linked to given host address URL.

        :param url: URL for the Root STAC Catalog.
        """
        self._url = url
        self.Client = STAC(url=self._url, verify=False)
        warnings.simplefilter('ignore')

    def catalog(self):
        """
        Get the catalog of collection IDs from the STAC Catalog.

        :returns: list of available collection IDs.
        """
        return self.Client.catalog

    def get_collections(self):
        """
        Get the collections available from the STAC Catalog.

        :returns: list of collection JSON objects.
        """
        collections = self.Client.collections
        collections = list(collections.values())
        return collections

    def get_collection(self, collection_id: str):
        """
        Get a collection of a specific ID.

        :param collection_id: the collection ID of a specific collection to get.
        :returns: dict of a collection JSON.
        """
        return self.Client.collection(collection_id=collection_id)

    def get_item(self, collection_id: str, item_id: str, **query):
        """
        Get an item of a specific collection with item ID.

        :param collection_id: the collection ID of a specific collection.
        :param item_id: the item ID of a specific item to get.
        :returns: dict of an item JSON object.
        """
        collection = self.get_collection(collection_id=collection_id)
        items = collection.get_items(item_id=item_id, filter=query)
        return items

    def get_itemcollection(self, collection_id: str, **query):
        """
        Get a list of items of a specific collection.

        :param collection_id: the collection ID of a specific collection.
        :return: list of items JSON objects of a specific collection ID.
        """
        collection = self.get_collection(collection_id=collection_id)
        itemcollection = collection.get_items(filter=query)
        return itemcollection

    def search(self, freetext: str = None, doctype: str = 'item', **query):
        """
        Search the STAC Catalog for a specific items.

        :param freetext: free text search feature to find item of any given string.
        :param doctype: choice of item or collection to retrieve from search result.
        :param query: **kwargs to add filters to search.
        :returns: dict of the JSON search result.
        """
        if freetext:
            return self.search(q=freetext, doctype=doctype, **query)

        if 'collections' in query:
            collections = query['collections']
            query['collections'] = [getattr(collection, 'id', collection) for collection in collections]

        result = self.Client.search(**query)

        if doctype == 'collection':
            return asyncio.run(async_search(result))
        else:
            return result

    def post_search(self, query: dict, filter: dict = None, doctype: str = 'item'):
        if filter:
            query['filter'] = filter
        data = json.dumps(query)
        response = requests.post(url=f"{self._url}/search", json=data, verify=False)
        result = response.json()
        if doctype == 'collection':
            return asyncio.run(async_search(result))
        else:
            return result

    def queryables(self):
        """
        Get the queryables of available properties to search.

        :returns: dict of queryables JSON
        """
        response = requests.get(f"{self._url}/queryables", verify=False)
        return response.json()

    def collection_queryables(self, collection_id: str):
        """
        Get the queryables of available properties of a specific collection.

        :returns: dict of queryables JSON
        """
        response = requests.get(f"{self._url}/collections/{collection_id}/queryables", verify=False)
        return response.json()

    def conformance_classes(self):
        """
        Get a list of STAC capabilities available at the initialised endpoint.

        :returns: list of conformance URLs
        """
        return self.Client.conformance
