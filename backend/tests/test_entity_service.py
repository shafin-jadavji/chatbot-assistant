import pytest
import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.entity_service import extract_entities

class TestEntityService:
    """Test suite for the entity extraction service"""

    def test_location_extraction(self):
        """Test extraction of location (GPE) entities"""
        # Test with explicit locations
        message = "What's the weather in Phoenix?"
        entities = extract_entities(message, intent="weather")
        assert "GPE" in entities
        assert "Phoenix" in entities["GPE"]
        
        # Test with multiple locations
        message = "Is Phoenix a city in Arizona?"
        entities = extract_entities(message)
        assert "GPE" in entities
        assert "Phoenix" in entities["GPE"]
        assert "Arizona" in entities["GPE"]

    def test_person_extraction(self):
        """Test extraction of person entities"""
        message = "Barack Obama was the 44th President of the United States."
        entities = extract_entities(message)
        assert "PERSON" in entities
        assert "Barack Obama" in entities["PERSON"]
        
        # Test with a common name
        message = "Tell me about John Smith"
        entities = extract_entities(message)
        assert "PERSON" in entities
        assert "John Smith" in entities["PERSON"]

    def test_time_extraction(self):
        """Test extraction of time entities"""
        message = "I have a meeting at 3 PM."
        entities = extract_entities(message)
        assert "TIME" in entities
        assert "3 PM" in entities["TIME"]

    def test_date_extraction(self):
        """Test extraction of date entities"""
        message = "I have a meeting on Monday."
        entities = extract_entities(message)
        assert "DATE" in entities
        assert "Monday" in entities["DATE"]

    def test_organization_extraction(self):
        """Test extraction of organization entities"""
        message = "Google is one of the biggest tech companies."
        entities = extract_entities(message)
        assert "ORG" in entities
        assert "Google" in entities["ORG"]

    def test_city_name_reclassification(self):
        """Test reclassification of city names from PERSON to GPE"""
        # Test with common city names that might be misclassified
        for city in ["Mesa", "Chandler", "Gilbert", "Tempe"]:
            message = f"What's the weather in {city}?"
            entities = extract_entities(message, intent="weather")
            assert "GPE" in entities
            assert city in entities["GPE"]
            assert city not in entities.get("PERSON", [])

    def test_context_aware_extraction(self):
        """Test context-aware entity extraction based on intent"""
        # Test with weather intent - should classify Gilbert as a location
        message = "What's the weather in Gilbert today?"
        entities = extract_entities(message, intent="weather")
        assert "GPE" in entities
        assert "Gilbert" in entities["GPE"]
        assert "DATE" in entities
        assert "today" in entities["DATE"]
        
        # Test with general intent - using a well-known location that spaCy will recognize
        message = "New York City is a nice place to visit."
        entities = extract_entities(message, intent="general")
        assert "GPE" in entities
        assert any("New York" in loc for loc in entities["GPE"])
        
        # Test with general intent - person entity
        message = "Dr. Gilbert Smith gave an interesting lecture yesterday."
        entities = extract_entities(message, intent="general")
        assert "PERSON" in entities
        assert any("Gilbert" in person for person in entities["PERSON"])

    def test_empty_message(self):
        """Test with empty message"""
        message = ""
        entities = extract_entities(message)
        assert all(len(entity_list) == 0 for entity_list in entities.values())

    def test_no_entities(self):
        """Test with message containing no recognizable entities"""
        message = "hello there how are you"
        entities = extract_entities(message)
        assert all(len(entity_list) == 0 for entity_list in entities.values())

    def test_location_indicators(self):
        """Test extraction of locations using preposition indicators"""
        indicators = ["in", "for", "at", "near"]
        for indicator in indicators:
            message = f"What's the weather {indicator} Tempe?"
            entities = extract_entities(message, intent="weather")
            assert "GPE" in entities
            assert "Tempe" in entities["GPE"] or "Tempe" in [e.lower() for e in entities["GPE"]]
            
    # def test_ambiguous_gilbert_cases(self):
    #     """Test handling of 'Gilbert' in different contexts"""
        
    #     # Test 1: Gilbert as a person name with 'in' after it
    #     message = "Is there anyone named Gilbert in acting?"
        
    #     # With general intent
    #     entities = extract_entities(message, intent="general")
    #     # Gilbert should be recognized as a person
    #     assert "PERSON" in entities
    #     assert any("Gilbert" in person for person in entities["PERSON"])
    #     # Gilbert should not be classified as a location
    #     assert not any("Gilbert" in loc for loc in entities.get("GPE", []))
        
    #     # Test 2: Gilbert as a location with state name
    #     message = "What is the temperature in Gilbert Arizona?"
        
    #     # With weather intent
    #     entities = extract_entities(message, intent="weather")
    #     # Gilbert should be recognized as a location
    #     assert "GPE" in entities
    #     assert any("Gilbert" in loc for loc in entities["GPE"])
    #     # Gilbert should not be classified as a person
    #     assert not any("Gilbert" in person for person in entities.get("PERSON", []))
        
    #     # Test 3: Melissa Gilbert as a person name
    #     message = "Was Melissa Gilbert in Little House on the Prairie?"
        
    #     # With general intent
    #     entities = extract_entities(message, intent="general")
    #     # Melissa Gilbert should be recognized as a person
    #     assert "PERSON" in entities
    #     assert any("Gilbert" in person for person in entities["PERSON"])
    #     # Gilbert should not be classified as a location
    #     assert not any("Gilbert" in loc for loc in entities.get("GPE", []))
        
    #     # With weather intent (should still recognize as person)
    #     entities = extract_entities(message, intent="weather")
    #     # Even with weather intent, "Melissa Gilbert" should stay as a person
    #     assert "PERSON" in entities
    #     assert any("Gilbert" in person for person in entities["PERSON"])
