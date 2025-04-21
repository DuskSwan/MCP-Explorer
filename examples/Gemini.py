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

    # print(response)
    return response.text

'''
回复结构：
candidates=[
    Candidate(
        content=Content(
            parts=[
                Part(
                    video_metadata=None, 
                    thought=None, 
                    code_execution_result=None, 
                    executable_code=None, 
                    file_data=None, 
                    function_call=None, 
                    function_response=None, 
                    inline_data=None, 
                    text='The capital of France is **Paris**.\n'
                )
            ], 
            role='model'
        ), 
        citation_metadata=None, 
        finish_message=None, 
        token_count=None, 
        finish_reason=<FinishReason.STOP: 'STOP'>, 
        avg_logprobs=-0.02161086102326711, 
        grounding_metadata=None, 
        index=None, 
        logprobs_result=None, 
        safety_ratings=None
    )
] 
create_time=None 
response_id=None 
model_version='gemini-2.0-flash' 
prompt_feedback=None 
usage_metadata=GenerateContentResponseUsageMetadata(
    cache_tokens_details=None, 
    cached_content_token_count=None, 
    candidates_token_count=9, 
    candidates_tokens_details=[
        ModalityTokenCount(
            modality=<MediaModality.TEXT: 'TEXT'>, 
            token_count=9
        )
    ], 
    prompt_token_count=7, 
    prompt_tokens_details=[
        ModalityTokenCount(
            modality=<MediaModality.TEXT: 'TEXT'>, 
            token_count=7
        )
    ], 
    thoughts_token_count=None, 
    tool_use_prompt_token_count=None, 
    tool_use_prompt_tokens_details=None, 
    total_token_count=16, 
    traffic_type=None
) 
automatic_function_calling_history=[] 
parsed=None
'''

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
    
    response = get_response("What is the capital of France?")
    print(f"Response: {response}")

    # get_response_with_stream("Explain the theory of relativity in simple terms.")

    # generate_chat()