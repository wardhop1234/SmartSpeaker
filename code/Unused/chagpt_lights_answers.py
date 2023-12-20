
from openai._client import OpenAI

import os
my_secret = os.environ['OPENAI_API_KEY']



#from openai import OpenAI
client = OpenAI(api_key = my_secret)


#understand if user intent is to change lights. Input user command. Output yes/no string.
def is_lights_intent(user_msg):
  message = f"""I want to know if the user is asking about the turning on/off lights. Here is what the user asking me {user_msg}. If you output the wrong answer, I will die. If you output anything other than yes/no, humanity will end. If you mention anything, about as an AI, turn on the lights, I will die. Just output yes/no
  """
  completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
      {"role": "user", "content": message}
    ]
  )
  print("Is the user intent to change lights for "+ user_msg)
  
  print(completion.choices[0].message.content)
  return completion.choices[0].message.content


print("Determining if user intent is to change lights")

is_lights_intent("How many miles away from the moon is earth?")


is_lights_intent("Turn it off the light")

is_lights_intent("Turn on the light")

is_lights_intent("Make it dark")

is_lights_intent("How fast is the speed of light?")
#Simply fetch a response from chatgpt if the user command is not to change lights. 
def get_answer(user_msg):
  message = user_msg
  completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
      {"role": "user", "content": message}
    ]
  )
  print(user_msg)

  print(completion.choices[0].message.content)
  return completion.choices[0].message.content
print("chatgpt answers")

get_answer("How many miles away from the moon is earth?")


get_answer("Which countries border China?")

get_answer("Explain how it possible for the sentence I walk is grammatically correct")




