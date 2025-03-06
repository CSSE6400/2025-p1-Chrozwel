from todo import create_app
import unittest

class TodoTest(unittest.TestCase):
    # Called before each test and used to initialise the in-memory database.
    def setUp(self):
        self.app = create_app(config_overrides={
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'TESTING': True
        })
        
        self.client = self.app.test_client()
    
    # A helper method to compare the todo items from the API with those expected.
    def assertDictSubset(self, expected_subset: dict, whole: dict):
        for key, value in expected_subset.items():
            self.assertEqual(whole[key], value)