from openai._client import OpenAI
import os, json, db
import RPi.GPIO as GPIO

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
previousPrompt = {"prompt": None, "response": None}

numPastLogs = int(os.environ.get("NUM_PAST_MESSAGES"))

# These prompts force ChatGPT to give us a parseable output for processing database-related commands
deviceOnOffPrompt = """If the user is asking to turn a device on or off, output JSON as follows: {"type": "device_change", "alias": "device name", "on": true/false}"""
deviceStatusPrompt = """If the user is asking for the status of a pin, output JSON as follows: {"type": "device_status", "alias": "device name"}"""
pinAssignmentPrompt = """If the user is asking to assign a pin to a device, output JSON as follows: {"type": "pin_change", "alias": "device name", "pin": pin number}"""
pinUnassignmentPrompt = """If the user is asking to unassign a pin, output JSON as follows: {"type": "pin_unassign", "pin": pin number}"""
defaultPrompt = """In all other cases, output a text response as a helpful assistant. Follow these guidelines when creating your responses:
                   Pretend you are having a conversation with a friend.
                   You are a virtual friend that lives inside a device.
                   Write your responses as if you are a virtual person.
                   Output factual/accurate responses when appropriate.
                """

# Call this at the beginning of the main program; establishes aliasable pins as outputs so they can be modified by voice commands
def pin_setup():
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  # Set pins to output
  for pinNumber in range(db.MIN_PIN_NUMBER, db.MAX_PIN_NUMBER):
    GPIO.setup(pinNumber, GPIO.OUT)
  # Set default values based on database configuration on bootup
  response = db.getPinConfig()
  if response.success:
    for pinString in response.data:
      pinNumber = int(pinString)
      GPIO.output(pinNumber, response.data[pinString])
  else:
    print(f"Error getting pin configuration: {response.data}")

# call at the end of main function to reset all pins
def pin_cleanup():
  response = db.getPinConfig()
  if response.success:
    for pinString in response.data:
      pinNumber = int(pinString)
      GPIO.output(pinNumber, False)
  else:
    print(f"Error getting pin configuration: {response.data}")

# call to API to get a response that incorporates memory (does not return anything b/c we run it in a thread)
def full_memory_response(inputlist, user_msg):
  msgs = []
  # Inject previous conversation history
  if numPastLogs > 0:
    logs = db.getLogs(numPastLogs)
    if logs.success:
      print("message logs:")
      for log in logs.data:
        print("     " + log["role"] + " : " + log["content"])
        msgs.append(log)
  msgs.append({"role": "user", "content": user_msg})
  msgs.append({"role": "system", "content": f"{defaultPrompt}"})
  
  completion = client.chat.completions.create(
    model="gpt-4",
    messages=msgs
  )
  
  content = completion.choices[0].message.content
  inputlist.append(content)
    
# The main voice command processing function; call this directly with user input as text, and it will perform appropriate actions and produce ChatGPT output
def process_prompt(user_msg):
  msgs = []
  content = None
  if previousPrompt["prompt"] is not None and previousPrompt["prompt"] == user_msg:
    # Skip request to ChatGPT if we get identical back-to-back prompts
    content = previousPrompt["response"]
  else:
    msgs.append({"role": "user", "content": user_msg})
    msgs.append({"role": "system", "content": f"{deviceOnOffPrompt}. {deviceStatusPrompt}. {pinAssignmentPrompt}. {pinUnassignmentPrompt}. {defaultPrompt}"})
    
    completion = client.chat.completions.create(
      model="gpt-4",
      messages=msgs
    )
    
    content = completion.choices[0].message.content
    previousPrompt["prompt"] = user_msg
    previousPrompt["response"] = content
  
  try:
    # Parse the JSON passed from ChatGPT, assuming the default prompt was not selected.
    response = json.loads(content)
    if response.get("type") == "device_change":
      return process_on_off_prompt(response) , False
    elif response.get("type") == "device_status":
      return process_status_prompt(response) , False
    elif response.get("type") == "pin_change":
      return process_assign_prompt(response) , False
    elif response.get("type") == "pin_unassign":
      return process_unassign_prompt(response) , False
    # This should only return if we got JSON without a valid request type. It does not run if the default was used
    return "I'm sorry, I was unable to process that request. Try rephrasing and asking again." , False
  except Exception as e: # Default prompt; text response provided
    return content , True
  
# Set the on/off status of a device and output confirmation as a ChatGPT response
def process_on_off_prompt(options):
  response = db.setPinEnabled(name=sanitize_alias(options.get('alias')), enabled=options.get('on'))
  if response.success:
    for pinNumber in response.data:
      GPIO.output(pinNumber, options.get('on'))
    return f"Ok, I've turned \"{options.get('alias')}\" {'on' if options.get('on') else 'off'}."
  else:
    return process_database_error(response, options)
    
# Get the on/off status of a device and output as a ChatGPT response
def process_status_prompt(options):
  response = db.getPinEnabled(name=sanitize_alias(options.get('alias')))
  if response.success:
    return f"\"{options.get('alias')}\" is currently {'on' if response.data else 'off'}."
  else:
    return process_database_error(response, options)

# Alias a pin specified by options and output ChatGPT-like response
def process_assign_prompt(options):
  response = db.aliasPin(name=sanitize_alias(options.get('alias')), pinNumber=options.get('pin'))
  if response.success:
    GPIO.output(options.get('pin'), False)
    return f"Ok, I've assigned pin {options.get('pin')} to \"{options.get('alias')}\"."
  else:
    return process_database_error(response, options)

# Unalias a pin specified by options and output ChatGPT-like response
def process_unassign_prompt(options):
  response = db.unsetPin(pinNumber=options.get('pin'))
  if response.success:
    GPIO.output(options.get('pin'), False)
    return f"Ok, I've unassigned pin {options.get('pin')}."
  else:
    return process_database_error(response, options)

# Catches db.py response errors and outputs a response as if it comes from ChatGPT
def process_database_error(response, options):
  print(f"Error accessing the database: f{response.data}")
  if response.error == db.DBError.FAILED_TO_CONNECT:
    return "I'm sorry, I couldn't access saved configuration options. Please try again later."
  elif response.error == db.DBError.INVALID_PIN:
    return "I'm sorry, you can't assign to that pin number. Try a different number."
  elif response.error == db.DBError.NO_ALIAS_FOUND:
    return f"I'm sorry, there is no configuration for \"{options.get('alias')}\". Try assigning it to a pin."
  else:
    return f"I'm sorry, there was an error updating the configuration. Please try again later."

# Make the formatting of aliases in the database consistent to increase the odds that ChatGPT recognizes an alias
def sanitize_alias(alias):
  return alias.lower()
