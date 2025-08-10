"""
Test script to verify user metadata extraction from Flutter client.
"""

import json
from loguru import logger


def test_metadata_parsing():
    """Test parsing of Flutter metadata."""
    
    # Simulate the metadata format from Flutter
    flutter_metadata = '{"userId": "user123", "userName": "John Doe"}'
    
    try:
        # Parse the JSON metadata
        metadata = json.loads(flutter_metadata)
        user_id = metadata.get('userId')
        user_name = metadata.get('userName')
        
        logger.info(f"Successfully parsed metadata:")
        logger.info(f"  User ID: {user_id}")
        logger.info(f"  User Name: {user_name}")
        
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse metadata: {e}")
        return False
    except Exception as e:
        logger.error(f"Error processing metadata: {e}")
        return False


def test_invalid_metadata():
    """Test handling of invalid metadata."""
    
    # Test with invalid JSON
    invalid_metadata = '{"userId": "user123", "userName": "John Doe"'  # Missing closing brace
    
    try:
        metadata = json.loads(invalid_metadata)
        logger.error("Should have failed to parse invalid JSON")
        return False
        
    except json.JSONDecodeError as e:
        logger.info(f"Correctly caught JSON decode error: {e}")
        return True
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def test_missing_fields():
    """Test handling of metadata with missing fields."""
    
    # Test with missing userName
    metadata_without_name = '{"userId": "user123"}'
    
    try:
        metadata = json.loads(metadata_without_name)
        user_id = metadata.get('userId')
        user_name = metadata.get('userName')
        
        logger.info(f"Metadata with missing fields:")
        logger.info(f"  User ID: {user_id}")
        logger.info(f"  User Name: {user_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing metadata with missing fields: {e}")
        return False


def main():
    """Main test function."""
    logger.info("Testing user metadata extraction...")
    
    # Test valid metadata
    logger.info("\n1. Testing valid metadata parsing:")
    test_metadata_parsing()
    
    # Test invalid metadata
    logger.info("\n2. Testing invalid metadata handling:")
    test_invalid_metadata()
    
    # Test missing fields
    logger.info("\n3. Testing metadata with missing fields:")
    test_missing_fields()
    
    logger.info("\n" + "="*50)
    logger.info("METADATA EXTRACTION TESTS COMPLETE")
    logger.info("="*50)


if __name__ == "__main__":
    main()