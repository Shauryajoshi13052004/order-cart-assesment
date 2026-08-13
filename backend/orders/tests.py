from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status
from .models import MenuItem, Order


class OrderApiTests(APITestCase):
    def setUp(self):
        self.pizza = MenuItem.objects.create(name='Pizza', description='Cheesy', price=Decimal('12.50'))

    def test_menu_endpoint_returns_available_items(self):
        MenuItem.objects.create(name='Hidden', description='Nope', price=10, available=False)
        response = self.client.get('/api/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Pizza')

    def test_menu_can_search_sort_and_paginate(self):
        MenuItem.objects.create(name='Burger', description='Juicy', price=Decimal('9.00'))
        response = self.client.get('/api/menu-items/?search=burger&ordering=price&page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Burger')

    def test_place_order_calculates_total_and_creates_items(self):
        response = self.client.post('/api/orders/', {'customer_name': 'Ava', 'customer_address': '1 Main St', 'customer_phone': '5551234567', 'items': [{'menu_item_id': self.pizza.id, 'quantity': 2}]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_amount'], '25.00')
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().items.count(), 1)

    def test_order_validation_rejects_empty_or_invalid_items(self):
        base = {'customer_name': 'Ava', 'customer_address': '1 Main St', 'customer_phone': '5551234567'}
        empty = self.client.post('/api/orders/', {**base, 'items': []}, format='json')
        invalid = self.client.post('/api/orders/', {**base, 'items': [{'menu_item_id': 9999, 'quantity': 0}]}, format='json')
        self.assertEqual(empty.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_status_can_be_updated_and_tracked(self):
        order = Order.objects.create(customer_name='Ava', customer_address='1 Main St', customer_phone='5551234567')
        update = self.client.patch(f'/api/orders/{order.id}/update_status/', {'status': 'preparing'}, format='json')
        tracking = self.client.get(f'/api/orders/{order.id}/track/')
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertEqual(tracking.data['status'], 'preparing')

    def test_order_insights_returns_operational_totals(self):
        Order.objects.create(customer_name='Ava', customer_address='1 Main St', customer_phone='5551234567', status='preparing', total_amount=Decimal('24.00'))
        Order.objects.create(customer_name='Ben', customer_address='2 Main St', customer_phone='5551234568', status='delivered', total_amount=Decimal('10.00'))
        response = self.client.get('/api/orders/insights/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 2)
        self.assertEqual(Decimal(str(response.data['total_revenue'])), Decimal('34.00'))
        self.assertEqual(response.data['active_orders'], 1)
        self.assertEqual(response.data['status_counts']['preparing'], 1)
