from transformers import pipeline

# Load a pre-trained transformer model for intent classification
intent_classifier = pipeline("text-classification", model="facebook/bart-large-mnli")

# Known intents
INTENT_LABELS = {
    "weather": ["weather", "temperature", "forecast"],
    "news": ["news", "update"],
    "casual": ["joke", "who are you"]
}

def detect_intent(user_message):
    """
    Uses transformer model to classify user intent.
    """
    prediction = intent_classifier(user_message)[0]
    label = prediction["label"].lower()

    # Match detected label to predefined intents
    for key, keywords in INTENT_LABELS.items():
        if any(word in user_message.lower() for word in keywords):
            return key
    return "general"  # Default category

# --- TEST FUNCTION ---
def test_intent_detection():
    test_messages = [
        "What's the weather in Phoenix?",  # Should detect as "weather"
        "Whats the temperature?",  # Should detect as "weather"
        "Tell me the latest news!",  # Should detect as "news"
        "Who are you?",  # Should detect as "casual"
        "I love programming!",  # Should detect as "general"
    ]

    for message in test_messages:
        intent = detect_intent(message)
        print(f"📩 Message: {message} → 🔍 Intent: {intent}")

if __name__ == "__main__":
    test_intent_detection()