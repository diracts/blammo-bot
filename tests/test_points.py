#!/usr/bin/env python3
"""
Test cases for the points system
"""
import unittest
import sys
import os
import tempfile
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.points import PointData


class TestPointsSystem(unittest.TestCase):
    """Test the PointData class and points management"""
    
    def setUp(self):
        """Set up test fixtures with temporary CSV file"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False)
        self.temp_file.write('username,points,gamble_loss\n')
        self.temp_file.write('testuser,200,0\n')
        self.temp_file.write('pooruser,50,10\n')
        self.temp_file.close()
        
        # Create PointData instance with test file
        self.points = PointData(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test files"""
        os.unlink(self.temp_file.name)
    
    def test_points_initialization(self):
        """Test that points system initializes correctly"""
        self.assertIsInstance(self.points.df, pd.DataFrame)
        self.assertEqual(len(self.points.df), 2)
        
    def test_get_user_points(self):
        """Test retrieving user points"""
        points = self.points.get_points('testuser')
        self.assertEqual(points, 200)
        
        # New users start with 0 points, not 200
        points = self.points.get_points('nonexistent')
        self.assertEqual(points, 0)  # New users get 0 points
        
    def test_add_points(self):
        """Test adding points to user"""
        initial_points = self.points.get_points('testuser')
        self.points.add_points('testuser', 50)
        new_points = self.points.get_points('testuser')
        self.assertEqual(new_points, initial_points + 50)
        
    def test_subtract_points(self):
        """Test subtracting points from user"""
        initial_points = self.points.get_points('testuser')
        self.points.sub_points('testuser', 30)
        new_points = self.points.get_points('testuser')
        self.assertEqual(new_points, initial_points - 30)
        
    def test_points_validation(self):
        """Test points validation logic"""
        # Test that points can't go negative (if implemented)
        poor_points = self.points.get_points('pooruser')
        self.assertGreaterEqual(poor_points, 0)
        
    def test_user_creation(self):
        """Test creating new user when they don't exist"""
        new_user_points = self.points.get_points('newuser')
        self.assertEqual(new_user_points, 0)  # New users start with 0


class TestPointsValidation(unittest.TestCase):
    """Test points validation functions"""
    
    def test_point_amount_validation(self):
        """Test that point amounts are validated correctly"""
        # These would test any validation functions in the points module
        pass
        
    def test_username_validation(self):
        """Test that usernames are validated correctly"""
        # These would test username validation in points system
        pass


if __name__ == '__main__':
    unittest.main()