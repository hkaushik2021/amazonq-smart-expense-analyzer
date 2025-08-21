import unittest
import sys
import os
from decimal import Decimal
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from process_document import (
    extract_expense_info,
    categorize_expense,
    extract_description,
    extract_date,
    validate_expense_data
)

class TestProcessDocument(unittest.TestCase):
    
    def test_amount_extraction(self):
        """Test amount extraction with various patterns"""
        test_cases = [
            ("Total: $25.50", Decimal('25.50')),
            ("Amount $45.00", Decimal('45.00')),
            ("$89.99", Decimal('89.99')),
            ("15.75", Decimal('15.75')),
            ("Total: 100.00", Decimal('100.00')),
            ("No amount here", Decimal('0.00'))
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_expense_info(text, "test.txt")
                self.assertEqual(result['amount'], expected)
    
    def test_categorization(self):
        """Test expense categorization"""
        test_cases = [
            ("Starbucks Coffee", "food"),
            ("Uber ride to airport", "transport"),
            ("Office supplies from Staples", "office"),
            ("Hotel booking", "travel"),
            ("CVS Pharmacy", "healthcare"),
            ("Random expense", "other")
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = categorize_expense(text)
                self.assertEqual(result, expected)
    
    def test_date_extraction(self):
        """Test date extraction with various formats"""
        test_cases = [
            ("Date: 01/15/2024", "2024-01-15"),
            ("12/25/2023", "2023-12-25"),
            ("2024-03-10", "2024-03-10"),
            ("Date: 01/15/24", "2024-01-15"),  # 2-digit year
            ("No date here", datetime.now().strftime('%Y-%m-%d'))
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_date(text)
                if "No date" not in text:
                    self.assertEqual(result, expected)
                else:
                    # For current date, just check format
                    self.assertRegex(result, r'\d{4}-\d{2}-\d{2}')
    
    def test_description_extraction(self):
        """Test description extraction"""
        test_cases = [
            ("Starbucks\n123 Main St\nTotal: $5.50", "Starbucks"),
            ("McDonald's Restaurant\nOrder #123", "McDonald's Restaurant"),
            ("", "test_receipt.jpg")  # Fallback to filename
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = extract_description(text, "test_receipt.jpg")
                if text:
                    self.assertEqual(result, expected)
                else:
                    self.assertEqual(result, "test receipt.jpg")
    
    def test_validation(self):
        """Test expense data validation"""
        valid_data = {
            'expense_id': 'test-123',
            'amount': Decimal('25.50'),
            'category': 'food',
            'description': 'Coffee Shop',
            'date': '2024-01-15'
        }
        
        # Valid data should pass
        self.assertTrue(validate_expense_data(valid_data))
        
        # Missing fields should fail
        invalid_data = valid_data.copy()
        del invalid_data['amount']
        self.assertFalse(validate_expense_data(invalid_data))
        
        # Zero amount should fail
        invalid_data = valid_data.copy()
        invalid_data['amount'] = Decimal('0.00')
        self.assertFalse(validate_expense_data(invalid_data))
        
        # Invalid date should fail
        invalid_data = valid_data.copy()
        invalid_data['date'] = 'invalid-date'
        self.assertFalse(validate_expense_data(invalid_data))
    
    def test_complete_extraction(self):
        """Test complete expense information extraction"""
        receipt_text = """
        Starbucks Coffee
        123 Main Street
        Date: 01/15/2024
        
        Coffee - Grande    $4.50
        Tax               $0.35
        Total:            $4.85
        
        Thank you!
        """
        
        result = extract_expense_info(receipt_text, "starbucks_receipt.jpg")
        
        self.assertEqual(result['amount'], Decimal('4.85'))
        self.assertEqual(result['category'], 'food')
        self.assertEqual(result['date'], '2024-01-15')
        self.assertEqual(result['description'], 'Starbucks Coffee')
        self.assertTrue(validate_expense_data(result))

if __name__ == '__main__':
    unittest.main()