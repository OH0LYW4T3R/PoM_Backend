import os
from openai import OpenAI
from rest_framework import status
from rest_framework.response import Response
from config.settings import get_env_variable
import json

def add_question(extract_content):
    question = extract_content[0] + "\n" + extract_content[1] + "\n\n"
    shape =  """
        {
            title : 다음 내용의 주제,
            content : 다음 내용의 3줄 요약
        }
    """
    request = "앞서 주어진 내용에 대해서 다음과 같은 형식으로 응답해줘"

    total_question = question
    word = total_question.split()
    select_word = word[-2750:]

    total_question = ' '.join(select_word)

    total_question += (request + shape)

    print(total_question)

    return total_question


def gpt_summary(string, title, thumb_nail_url):
    try: 
        dict_data = {}
        
        client = OpenAI(
            api_key = get_env_variable('API_KEY'),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": string
                }
            ],
            model="gpt-4",
        )
        print(chat_completion.choices[0].message.content)
        if chat_completion.choices[0].message.content[0] == "{" and chat_completion.choices[0].message.content[-1] == "}":
            dict_data = json.loads(chat_completion.choices[0].message.content)

            print(dict_data)

            if thumb_nail_url:
                dict_data['thumbnail'] = thumb_nail_url    
            else:
                dict_data['thumbnail'] = "None" 

            if title:
                dict_data['title'] = title

            return dict_data
        else:
            return dict_data
    except:
        return Response({"Error : GPT API Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)