from transformers import pipeline

# Load a lightweight model for intent classification
intent_classifier = pipeline("text-classification", model="distilbert-base-uncased")

# Define known intent categories
INTENT_LABELS = {
    "weather": ["what's the weather", "how is the weather", "temperature in"],
    "news": ["latest news", "update on", "tell me news"],
    "casual": ["how are you", "tell me a joke", "who are you"]
}

def detect_intent(user_message):
    """
    Classifies user intent using a transformer model.
    """
    prediction = intent_classifier(user_message)
    label = prediction[0]["label"].lower()

    # Match predefined intent categories
    for key, phrases in INTENT_LABELS.items():
        if any(phrase in user_message.lower() for phrase in phrases):
            return key

    return "general"  # Default intent

# --- TEST FUNCTION ---
def test_intent_detection():
    test_messages = [
        "What's the weather in Phoenix?",  # Should detect as "weather"
        "Tell me the latest news!",  # Should detect as "news"
        "Who are you?",  # Should detect as "casual"
        "I love programming!",  # Should detect as "general"
    ]

    for message in test_messages:
        intent = detect_intent(message)
        print(f"📩 Message: {message} → 🔍 Intent: {intent}")

if __name__ == "__main__":
    test_intent_detection()