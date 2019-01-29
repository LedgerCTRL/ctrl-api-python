# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.inventory_item import InventoryItem  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDevelopersController(BaseTestCase):
    """DevelopersController integration test stubs"""

    def test_add_inventory(self):
        """Test case for add_inventory

        adds an inventory item
        """
        data = dict(upfile=(BytesIO(b'some file data'), 'file.txt'),
                    inventoryItem='inventoryItem_example',
                    userId='userId_example')
        response = self.client.open(
            '/vaas/vaas2/1.0.0/inventory',
            method='POST',
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_file(self):
        """Test case for get_file

        fetches file associated with item ID
        """
        response = self.client.open(
            '/vaas/vaas2/1.0.0/file/{id}'.format(id='id_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_item(self):
        """Test case for get_item

        fetches individual item by id
        """
        response = self.client.open(
            '/vaas/vaas2/1.0.0/inventory/{id}'.format(id='id_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
