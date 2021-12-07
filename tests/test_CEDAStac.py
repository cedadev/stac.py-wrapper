#!/usr/bin/env python

"""Tests for `client` package."""

__author__ = """Mahir Rahman"""
__contact__ = 'kazi.mahir@stfc.ac.uk'
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import pytest
import requests

from client.client import StacPyClient

url = 'https://stac-elasticsearch-master.130.246.131.9.nip.io'
collection_id = 'Fj3reHsBhuk7QqVbt7P-'
item_id = '5ad82e4c683d7dd9865c3849677b135e'
Client = StacPyClient(url=url)


class TestClient:
    def test_get_collections(self):
        collections = Client.get_collections()
        response = requests.get(f"{url}/collections", verify=False)
        response = response.json()
        assert collections == response.get('collections')

    def test_get_collection(self):
        collection = Client.get_collection(collection_id=collection_id)
        response = requests.get(f"{url}/collections/{collection_id}", verify=False)
        response = response.json()
        assert collection == response

    def test_get_itemcollection(self):
        itemcollection = Client.get_itemcollection(collection_id=collection_id)
        response = requests.get(f"{url}/collections/{collection_id}/items", verify=False)
        response = response.json()
        assert itemcollection == response

    def test_get_item(self):
        item = Client.get_item(collection_id=collection_id, item_id=item_id)
        response = requests.get(f"{url}/collections/{collection_id}/items/{item_id}", verify=False)
        response = response.json()
        assert item == response


class TestSearch:
    def test_free_text_search(self):
        res1 = Client.search(q="AerChemMIP").get('features')
        res2 = Client.search("AerChemMIP").get('features')
        res3 = Client.search(q="AerChem*").get('features')
        res4 = Client.search(q="aerchemmip").get('features')
        assert res1 == res2 == res3 == res4

    def test_facet_search(self):
        filter = {
             "eq": [
                 {"property": "institution_id"},
                 "CNRM-CERFACS"
             ]
          }
        res1 = Client.search(filter=filter)
        res2 = requests.post(url=f"{url}/search", json={'filter': filter}, verify=False)
        res2 = res2.json()
        assert res1 == res2

    def test_object_search(self):
        collections = Client.get_collections()
        res1 = Client.search(collections=collections)
        assert len(res1.get('context').get('collections')) == len(collections)
