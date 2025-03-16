import spacy

# Load spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

def extract_entities(user_message):
    """
    Extracts entities using spaCy.
    """
    doc = nlp(user_message)
    entities = {ent.label_: ent.text for ent in doc.ents}
    return entities

# --- TEST FUNCTION ---
def test_entity_extraction():
    test_messages = [
        "What's the weather in Phoenix?",  # Should extract {"GPE": "Phoenix"}
        "Barack Obama was the 44th President of the United States.",  # Should extract {"PERSON": "Barack Obama"}
        "Apple Inc. was founded in 1976.",  # Should extract {"ORG": "Apple Inc.", "DATE": "1976"}
        "I have a meeting on Monday.",  # Should extract {"DATE": "Monday"}
    ]

    for message in test_messages:
        entities = extract_entities(message)
        print(f"📩 Message: {message} → 🎯 Entities: {entities}")

if __name__ == "__main__":
    test_entity_extraction()