import unittest
import json
from app import app

class BankApiTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client before each test."""
        self.app = app.test_client()
        self.app.testing = True

    def test_1_get_banks(self):
        """Test if the /api/banks endpoint returns a list of banks."""
        print("\nTesting Bank List...")
        response = self.app.get('/api/banks')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0, "bank list should not be empty")
        print(" bank list test Passed")

    def test_2_get_branch_details(self):
        """Test if a valid IFSC code returns the correct details."""
        print("\nTesting Branch Details...")
        test_ifsc = 'ABHY0065001'
        response = self.app.get(f'/api/branches/{test_ifsc}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['ifsc'], test_ifsc)
        self.assertEqual(data['city'], 'MUMBAI')
        self.assertIn('bank_name', data) 
        print("branch details test Passed")

    def test_3_branch_not_found(self):
        """test if incorrect IFSC code : 404 error."""
        print("\ntesting Invalid Branch...")
        response = self.app.get('/api/branches/INVALID_CODE_999')
        
        self.assertEqual(response.status_code, 404)
        print("Error handling test Passed")

if __name__ == '__main__':
    unittest.main()
