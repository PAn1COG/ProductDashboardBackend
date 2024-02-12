from django.test import TestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from api.serializers import CategorySerializer
from .models import Item, Category
from .views import createCategory, createItem, getAllCategories, getAllItems, getItem

class GetAllItemsAPITest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='test_user')
        self.token = Token.objects.create(user=self.user)
        self.token_key = self.token.key


    def test_get_all_items_positive(self):
        # Creating some items for testing
        category1 = Category.objects.create(name = 'Category1')
        category2 = Category.objects.create(name = 'Category2')
        Item.objects.create(SKU='SKU123', name='Item 1', category=category1, stock_status='In Stock', available_stock=10)
        Item.objects.create(SKU='SKU456', name='Item 2', category=category2, stock_status='Out of Stock', available_stock=0)
        Item.objects.create(SKU='SKU789', name='Item 3', category=category1, stock_status='Backordered', available_stock=5)



        # Making a GET request to the API
        request = self.factory.get('/api/item-list/')
        force_authenticate(request, user=self.user, token=self.token)
        response = getAllItems(request)

        # Asserting that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Asserting that the correct number of items is returned
        self.assertEqual(len(response.data), 3)  # Corrected to expect 3 items

    def test_get_all_items_negative(self):
        # Making a GET request to the API without creating any items
        request = self.factory.get('/api/item-list/')
        response = getAllItems(request)

        # Asserting that the response status code is 404
        self.assertEqual(response.status_code, 401)

    def test_filter_items_by_category(self):
        # Creating items with different categories
        category1 = Category.objects.create(name = 'Category1')
        category2 = Category.objects.create(name = 'Category2')
        Item.objects.create(SKU='SKU123', name='Item 1', category= category1, stock_status='In Stock', available_stock=10)
        Item.objects.create(SKU='SKU789', name='Item 3', category= category1, stock_status='Backordered', available_stock=5)
        Item.objects.create(SKU='SKU456', name='Item 2', category= category2, stock_status='Out of Stock', available_stock=0)

        # Making a GET request to the API with category filter
        request = self.factory.get('/api/item-list/?category=Category1')
        force_authenticate(request, user=self.user, token=self.token)
        response = getAllItems(request)

        # Asserting that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Asserting that only items with the specified category are returned
        self.assertEqual(len(response.data), 2)
class GetAllCategoriesAPITest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='test_user')
        self.token = Token.objects.create(user=self.user)
        self.token_key = self.token.key

    def test_get_all_categories(self):
        # Creating some categories for testing
        Category.objects.create(name='Category1')
        Category.objects.create(name='Category2')
        Category.objects.create(name='Category3')

        # Making a GET request to the API
        request = self.factory.get('/api/category-list/')
        force_authenticate(request, user=self.user, token=self.token)
        response = getAllCategories(request)

        # Asserting that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Asserting that the correct number of categories is returned
        self.assertEqual(len(response.data), 3)

    def test_get_all_categories_unauthenticated(self):
        # Making a GET request to the API without authentication
        request = self.factory.get('/api/category-list/')
        response = getAllCategories(request)

        # Asserting that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, 401)

    # Add more tests for sorting and pagination if needed
class GetItemAPITest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='test_user')
        self.token = Token.objects.create(user=self.user)
        self.token_key = self.token.key

    def test_get_item(self):
        # Creating an item for testing
        category = Category.objects.create(name='Category1')
        item = Item.objects.create(SKU='SKU123', name='Item 1', category=category, stock_status='In Stock', available_stock=10)

        # Making a GET request to the API with SKU parameter
        request = self.factory.get('/api/item-detail/', {'SKU': 'SKU123'})
        force_authenticate(request, user=self.user, token=self.token)
        response = getItem(request)

        # Asserting that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Asserting that the correct item is returned
        self.assertEqual(response.data['SKU'], 'SKU123')
        self.assertEqual(response.data['name'], 'Item 1')

    def test_get_item_missing_sku(self):
        # Making a GET request to the API without providing SKU
        request = self.factory.get('/api/item-detail/')
        force_authenticate(request, user=self.user, token=self.token)
        response = getItem(request)

        # Asserting that the response status code is 400 and contains appropriate message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, 'Please provide SKU')

    def test_get_item_unauthenticated(self):
        # Creating an item for testing
        category = Category.objects.create(name='Category1')
        item = Item.objects.create(SKU='SKU123', name='Item 1', category=category, stock_status='In Stock', available_stock=10)

        # Making a GET request to the API without authentication
        request = self.factory.get('/api/item-detail/', {'SKU': 'SKU123'})
        response = getItem(request)

        # Asserting that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, 401)


class CreateCategoryAPITest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='test_user')
        self.token = Token.objects.create(user=self.user)
        self.token_key = self.token.key

    def test_create_category(self):
        # Creating a POST request to create a category
        request = self.factory.post('/api/createCategory/', {'name': 'New Category'})
        force_authenticate(request, user=self.user, token=self.token)
        response = createCategory(request)

        # Asserting that the response status code is 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Asserting that the category is created and returned in the response data
        category = Category.objects.get(name='New Category')
        self.assertEqual(response.data, CategorySerializer(category).data)

    def test_create_category_invalid_data(self):
        # Creating a POST request with invalid data
        request = self.factory.post('/api/createCategory/', {'name': ''})
        force_authenticate(request, user=self.user, token=self.token)
        response = createCategory(request)

        # Asserting that the response status code is 400 and contains appropriate error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)  # Assuming the serializer returns 'name' as error field

    def test_create_category_unauthenticated(self):
        # Creating a POST request without authentication
        request = self.factory.post('/api/createCategory/', {'name': 'New Category'})
        response = createCategory(request)

        # Asserting that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CreateItemAPITest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='test_user')
        self.token = Token.objects.create(user=self.user)
        self.token_key = self.token.key

    def test_create_item(self):
        # Creating a category for testing
        category = Category.objects.create(name='Test Category')

        # Creating a POST request to create an item
        data = {
            'SKU': 'SKU123',
            'name': 'New Item',
            'category': category.name,
            'stock_status': 'In Stock',
            'available_stock': 10
        }
        request = self.factory.post('/api/createItem/', data)
        force_authenticate(request, user=self.user, token=self.token)
        response = createItem(request)

        # Asserting that the response status code is 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Asserting that the item is created
        self.assertTrue(Item.objects.filter(SKU='SKU123').exists())

    def test_create_item_invalid_data(self):
        # Creating a POST request with invalid data
        request = self.factory.post('/api/createItem/', {})
        force_authenticate(request, user=self.user, token=self.token)
        response = createItem(request)

        # Asserting that the response status code is 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_unauthenticated(self):
        # Creating a POST request without authentication
        request = self.factory.post('/api/createItem/', {})
        response = createItem(request)

        # Asserting that the response status code is 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


