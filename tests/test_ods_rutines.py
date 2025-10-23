import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import ods_rutines
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestODSRoutines:
    """Essential tests for ODS routines module using pytest"""

    @pytest.fixture
    def test_data(self):
        """Test data fixture"""
        return {
            'date': datetime.now(),
            'user': "test_user",
            'action': "test_action",
            'docsymbol': "A/RES/75/1",
            'job_number': "UN123456",
            'data': [{"key": "value"}]
        }

    def test_add_log_success(self, test_data):
        """Test successful log creation - Core functionality test"""
        # Mock all dependencies before importing
        with patch.dict('os.environ', {'DLX_REST_TESTING': 'true'}):
            with patch('pymongo.MongoClient') as mock_mongo_client:
                with patch('dlx.DB'):
                    with patch('boto3.client'):
                        with patch('decouple.config') as mock_config:
                            mock_config.side_effect = lambda key, default=None: {
                                'BASE_URL': 'https://test-api.com/',
                                'ODS_USERNAME': 'test_user',
                                'PASSWORD': 'test_pass',
                                'CLIENT_ID': 'test_client',
                                'CLIENT_SECRET': 'test_secret',
                                'CONN': 'mongodb://test'
                            }.get(key, default)
                            
                            # Mock the database and collection
                            mock_client = MagicMock()
                            mock_mongo_client.return_value = mock_client
                            mock_database = MagicMock()
                            mock_client.__getitem__.return_value = mock_database
                            mock_collection = MagicMock()
                            mock_database.__getitem__.return_value = mock_collection
                            mock_collection.insert_one.return_value = MagicMock()
                            
                            # Import the function after mocking
                            from ods.ods_rutines import add_log
                            
                            # Act
                            result = add_log(test_data['date'], test_data['user'], test_data['action'])
                            
                            # Assert
                            assert result == 0
                            mock_collection.insert_one.assert_called_once()
                            
                            # Verify the log object structure
                            call_args = mock_collection.insert_one.call_args[0][0]
                            assert call_args["user"] == test_data['user']
                            assert call_args["action"] == test_data['action']
                            assert call_args["date"] == test_data['date']

    def test_check_if_docsymbol_exists(self, test_data):
        """Test docsymbol existence check - API integration test"""
        # Mock all dependencies before importing
        with patch.dict('os.environ', {'DLX_REST_TESTING': 'true'}):
            with patch('pymongo.MongoClient'):
                with patch('dlx.DB'):
                    with patch('boto3.client'):
                        with patch('decouple.config') as mock_config:
                            mock_config.side_effect = lambda key, default=None: {
                                'BASE_URL': 'https://test-api.com/',
                                'ODS_USERNAME': 'test_user',
                                'PASSWORD': 'test_pass',
                                'CLIENT_ID': 'test_client',
                                'CLIENT_SECRET': 'test_secret',
                                'CONN': 'mongodb://test'
                            }.get(key, default)
                            
                            # Import the functions after mocking
                            from ods.ods_rutines import check_if_docsymbol_exists, ods_get_loading_symbol
                            
                            # Mock the API call
                            with patch('ods.ods_rutines.ods_get_loading_symbol') as mock_ods_get:
                                # Arrange
                                mock_response = {
                                    "body": {
                                        "meta": {"matches": 1},
                                        "data": [{"job_numbers": ["UN123456", "UN123457"]}]
                                    }
                                }
                                mock_ods_get.return_value = mock_response
                                
                                # Act
                                exists, job_numbers = check_if_docsymbol_exists(test_data['docsymbol'])
                                
                                # Assert
                                assert exists is True
                                assert job_numbers == ["UN123456", "UN123457"]
                                # The function calls ods_get_loading_symbol twice (lines 143 and 146)
                                assert mock_ods_get.call_count == 2
                                mock_ods_get.assert_has_calls([
                                    call(test_data['docsymbol']),
                                    call(test_data['docsymbol'])
                                ])


if __name__ == "__main__":
    # Run pytest with specific options
    pytest.main([__file__, "-v", "--tb=short"])