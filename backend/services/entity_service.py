import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_entities(user_message):
    """
    Extracts various entities from user messages using spaCy.
    Returns a dictionary of extracted entities.
    """
    doc = nlp(user_message)
    
    entities = {
        "GPE": None,  # Location (City, Country, etc.)
        "PERSON": None,  # Names (e.g., John, Barack Obama)
        "TIME": None,  # Time expressions (e.g., "tomorrow", "3 PM")
        "DATE": None,  # Dates (e.g., "Monday", "March 5")
        "ORG": None,  # Organizations (e.g., Google, NASA)
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_] = ent.text  # Store first occurrence

    return entities

# --- TEST FUNCTION ---
def test_entity_extraction():
    test_messages = [
        "What's the weather in Phoenix?",  # {"GPE": "Phoenix"}
        "Barack Obama was the 44th President of the United States.",  # {"PERSON": "Barack Obama"}
        "I have a meeting on Monday at 3 PM.",  # {"DATE": "Monday", "TIME": "3 PM"}
        "Google is one of the biggest tech companies.",  # {"ORG": "Google"}
        "What is the temperature in London?"  # {"GPE": "London"}
    ]

    for message in test_messages:
        entities = extract_entities(message)
        print(f"📩 Message: {message} → 🎯 Entities: {entities}")

if __name__ == "__main__":
    test_entity_extraction()
