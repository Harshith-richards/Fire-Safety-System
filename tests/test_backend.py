import unittest
import sys
import os
import json
from io import BytesIO
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    # --- 7.1 Unit Testing ---
    # Testing individual components in isolation

    @patch('app.routes.prediction_routes.yolo_model')
    def test_yolo_model_loading(self, mock_model):
        """Test if YOLO model is 'loaded' (mocked check)"""
        # In the actual code, we check if yolo_model is None. 
        # Here we mock it to be something.
        self.assertIsNotNone(mock_model)

    def test_config_loading(self):
        """Test if app configuration loads correctly"""
        self.assertTrue(self.app.config['TESTING'])

    # --- 7.2 Integration Testing ---
    # Testing interaction between API and Services

    @patch('app.routes.prediction_routes.predict_image')
    @patch('app.database.users_collection')
    @patch('app.database.logs_collection')
    @patch('app.routes.prediction_routes.Image.open')
    def test_predict_endpoint_integration(self, mock_image_open, mock_logs, mock_users, mock_predict):
        """Test /predict endpoint integration with mocked services"""
        
        # Mock Image.open to return a dummy object
        mock_image_open.return_value = MagicMock()

        # Mock prediction result
        mock_predict.return_value = {
            'names': {0: 'Fire', 1: 'Normal'},
            'top5_ids': [0],
            'top5_confs': [0.95],
            'predicted_class': 'Fire',
            'predicted_confidence': 0.95,
            'class_confidences': {'Fire': 0.95},
            'recommendation': 'Evacuate'
        }

        # Mock User DB
        mock_users.find_one.return_value = {
            'email': 'test@example.com',
            'phone': '1234567890',
            'address': '123 Test St'
        }

        # Create a dummy image
        img_byte_arr = BytesIO()
        img_byte_arr.write(b'fake_image_data')
        img_byte_arr.seek(0)

        data = {
            'image': (img_byte_arr, 'test.jpg'),
            'user_email': 'test@example.com'
        }

        response = self.client.post('/predict', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_predict.called)
        self.assertTrue(mock_logs.insert_one.called)

    # --- 7.4 Output Testing ---
    # Validating the output format and correctness

    @patch('app.routes.prediction_routes.predict_image')
    @patch('app.database.logs_collection')
    @patch('app.routes.prediction_routes.Image.open')
    def test_predict_output_structure(self, mock_image_open, mock_logs, mock_predict):
        """Verify the JSON output structure of /predict"""
        
        mock_image_open.return_value = MagicMock()
        
        mock_predict.return_value = {
            'names': {0: 'Normal'},
            'top5_ids': [0],
            'top5_confs': [0.99],
            'predicted_class': 'Normal',
            'predicted_confidence': 0.99,
            'class_confidences': {'Normal': 0.99},
            'recommendation': 'None'
        }

        img_byte_arr = BytesIO()
        img_byte_arr.write(b'fake_image_data')
        img_byte_arr.seek(0)

        data = {'image': (img_byte_arr, 'test.jpg')}
        
        response = self.client.post('/predict', data=data, content_type='multipart/form-data')
        json_data = response.get_json()

        # Check required fields
        required_fields = ['success', 'predicted_class', 'predicted_confidence', 'recommendation']
        for field in required_fields:
            self.assertIn(field, json_data)
        
        # Check data types
        self.assertIsInstance(json_data['success'], bool)
        self.assertIsInstance(json_data['predicted_class'], str)
        self.assertIsInstance(json_data['predicted_confidence'], float)

if __name__ == '__main__':
    unittest.main()
