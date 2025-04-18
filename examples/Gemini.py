'''
谷歌Gemini API 示例代码
API获取见 https://aistudio.google.com/apikey
模型价格见 https://aistudio.google.com/plan_information
'''

from google import genai
import os
import dotenv
dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_response(prompt, model_name="gemini-2.0-flash"):
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    return response.text

def get_response_with_stream(prompt, model_name="gemini-2.0-flash"):
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content_stream(
        model=model_name,
        contents=[prompt]
    )
    for chunk in response:
        print(chunk.text, end="")

def generate_chat():
    client = genai.Client(api_key=GEMINI_API_KEY)
    chat = client.chats.create(model="gemini-2.0-flash")

    response = chat.send_message("I have 2 dogs in my house.")
    print(response.text)

    response = chat.send_message("How many paws are in my house?")
    print(response.text)

    for message in chat.get_history():
        print(f'role - {message.role}',end=": ")
        print(message.parts[0].text)

if __name__ == "__main__":
    
    # response = get_response("What is the capital of France?")
    # print(f"Response: {response}")

    # get_response_with_stream("Explain the theory of relativity in simple terms.")

    generate_chat()