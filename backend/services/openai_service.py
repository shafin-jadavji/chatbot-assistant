import openai
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI API client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_chatbot_response(user_message):
    """
    Calls OpenAI's GPT-4 API to get chatbot response.
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message},
            ],
            model="gpt-4",
            temperature=0.7
        )

        print(f"✅ OpenAI Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
 
    return response.choices[0].message.content

if __name__ == "__main__":
    get_chatbot_response("what is the meaning of life?")
