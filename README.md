# CS190B-F23-VoiceGPT
VoiceGPT is a home assistant integrated with ChatGPT-4 capabilities. It can be used to control lighting systems and ask questions directly to the ChatGPT API via voice command. It is also equipped with a database to store user-friendly output names and previous conversation history.

### Contributors
- Joseph Yue - Hardware physical setup and programming
- Carson Kopper - Database controls and command processing
- Madhav Rai - Web request API call programming

## System Requirements
See `requirements.txt` for Python library requirements.
- Raspberry PiZero
- Breadboard and wires
- LEDs (at least 1)
- Micro USB to USB [adapter](https://www.amazon.com/LoveRPi-MicroUSB-Port-Black-Raspberry/dp/B01HYJLZH6/ref=sr_1_3?keywords=raspberry+pi+zero+usb&qid=1702573960&sr=8-3)
- USB [speaker](https://www.amazon.com/Computer-Speaker-Enhanced-Portable-Windows/dp/B086JXJ1LF/ref=sr_1_3?keywords=USB+speaker&qid=1702153611&sr=8-3) and [microphone](https://www.amazon.com/Microphone-Condenser-Recording-Streaming-669B/dp/B06XCKGLTP/ref=sr_1_5?crid=3M4DVJ7ECS5J5&keywords=usb%2Bmicrophone&qid=1702153620&sprefix=usb%2Bmicr%2Caps%2C174&sr=8-5&th=1) 
- Python 3.9+
- PostgresSQL

## Hardware Setup
Plug the USB speaker and microphone into the adapter and connect the adapter to the micro USB port on the PiZero before powering the device on. For attaching LEDs, use the BCM port numbers on the Pi. A diagram for the BCM numbers on the PiZero we used can be found [here](https://pi4j.com/getting-started/understanding-the-pins/). Connect 1 LED to BCM port 22, this will serve as the indicator light. You may also connect additional LEDs, but keep in mind these will need to be assigned manually (details for how to do this are listed in the Example Usage section).

## API Keys

Before you begin make sure to copy the .env.Sample file as .env


VoiceGPT also requires a working OpenAI API key with access to ChatGPT-4 as well as a DeepGram API key.  
To get the OpenAI key follow these steps:  
1. Go to [this](https://openai.com/product) page and login. You can also register a new account and associate it with a phone number that has never been used for OpenAI APIs before and recieve $18 of free credits.
3. There should be two options, ChatGPT or API, click API
<img src="https://github.com/ucsb/CS190B-F23-Project-Carson_Madhav_Joseph/assets/97574232/dd76127f-d018-495f-a4f5-9cad80152728" alt="image" width="500" height="auto">

4. Once logged in, navigate to the menu of the far left of the screen and click API keys
5. Click create new secret key
6. Copy this key into the OPENAI_API_KEY field in the .env file

To get the DeepGram key follow these steps:  
1. Go to [this](https://deepgram.com/) page and login. Unlike with OpenAI, new accounts with DeepGram automatically get $200 of free credits.
2. Navigate to API keys and click "Create a New API Key"
3. Name the key and click create
4. Copy this key into the TRANSCRIPTION field in the .env file

## Installation
First clone the repository to the Raspberry Pi:
```bash
git clone git@github.com:ucsb/CS190B-F23-Project-Carson_Madhav_Joseph.git voicegpt
cd voicegpt/code
```

Run these commands in the root directory of the repository:  
```bash
sudo apt-get install vlc  
sudo apt-get install ffmpeg  
sudo apt-get install postgresql
python3 -m pip install -r requirements.txt
```
### PostgreSQL setup
To set up the database tables, run the following commands:
```bash
sudo su postgres
createuser pi -P --interactive
```
You will be asked to enter a password for the database user. Add the fields
```
DATABASE_USERNAME=pi
DATABASE_PASSWORD=YOUR_DATABASE_PASSWORD
```
to ``.env`` (and create the file at the root of the project if it does not exist). Enter 'Y' when asked if the new role should be a superuser. Once created, type `exit` to return to the pi user. To create and initialize our database, enter the following commands:
```bash
psql
CREATE DATABASE main;
\q
python db.py
```
The script should respond stating that the pin table and log table setup are successful. If either table already exists in the database, the script will state this. The status of the data base can be checked by running SQL commands after executing ``psql -d main``.

## Example Usage
The program is run using `python app.py` in the `code` folder. The program is in passive mode until a speaker says "Activate". VoiceGPT will then listen for a request, send the content to ChatGPT, and output a response. After 5 seconds of silence the device returns to passive mode. Saying "Exit" will terminate the program.

### Assigning names to lights
As an example, the speaker can say "Assign the blue light to pin 15". The entry for pin ID 15 in the database will contain the alias "blue light" and be off by default. The speaker can remove this assignment by saying "Unassign pin 15". VoiceGPT should provide a user-friendly message stating that the action was performed successfully. Please note that our code uses the BCM numbers to identify the GPIO pins on the Pi. For the PiZero that we used, the link [here](https://pi4j.com/getting-started/understanding-the-pins/) provides a diagram for the BCM numbers of each pin. In the unlikely event that there are issues with assigning PINs verbally, it is also possible to do so by modifying the database using ``psql -d main``.

### Turning lights on and off
Lights are addressed by name, as assigned in the above instructions. Saying "Turn on the blue light" with it assigned as above will output high voltage to pin 15 and any other pins that are assigned to "blue light". Similarly, saying "turn off the blue light" will output low voltage to the same GPIO pins. VoiceGPT should provide a user-friendly message stating that the action was performed successfully.
