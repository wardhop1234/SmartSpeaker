| Week 4          | Planned meeting date 10/26                                         |                                                                           |                                                   |
|:----------------|:-------------------------------------------------------------------|:--------------------------------------------------------------------------|:--------------------------------------------------|
| **Participant** | **Done from last time**                                            | **TODO's**                                                                | **Blockers**                                      |
| Irreflexive     | Researched SQL database deployment on Raspberry Pi                 | Implement the actual database                                             | Need to figure out how to simulate a Raspberry Pi |
| madhav_ucsb     | Wrote boilerplate starter code for text to speech component.       | Figure out text to speech.                                                | None right now                                    |
| awesomebob35    | Made progress on figuring out how to interact with audio in python | Continue working on the code. Should also try to acquire a USB microphone |                                                   |
|                 |                                                                    |                                                                           |                                                   |

| Week 5          | Planned meeting date 11/2                                              |                                                                            |                                          |
|:----------------|:-----------------------------------------------------------------------|:---------------------------------------------------------------------------|:-----------------------------------------|
| **Participant** | **Done from last time**                                                | **TODO's**                                                                 | **Blockers**                             |
| Irreflexive     | Looked into simulating Raspberry Pi to start implementing database     | Still need to do the actual database (will do this weekend) implementation |                                          |
| madhav_ucsb     |                                                                        |                                                                            |                                          |
| awesomebob35    | Ordered the microphone/speaker and uploaded a few new files to test on | Still need to ensure audio i/o is working (cannot do until devices arrive) | Waiting on arrival of microphone/speaker |
|                 |                                                                        |                                                                            |                                          |

| Week 6          | Planned meeting date 11/9                                              |                                                                                 |                                                      |
|:----------------|:-----------------------------------------------------------------------|:--------------------------------------------------------------------------------|:-----------------------------------------------------|
| **Participant** | **Done from last time**                                                | **TODO's**                                                                      | **Blockers**                                         |
| Irreflexive     | Implemented postgres database management in python                     | Research ways to detect a database-related command in ChatGPT                   | Need to ssh into Pi to install postgres/setup tables |
| madhav_ucsb     |                                                                        |                                                                                 |                                                      |
| awesomebob35    | Microphone and speaker arrived, successfully tested audio input output | Will move on to more complex code to enable constant recording/playing of audio |                                                      |

| Week 7          | Planned meeting date 11/16                                                                             |                                                   |              |
|:----------------|:-------------------------------------------------------------------------------------------------------|:--------------------------------------------------|:-------------|
| **Participant** | **Done from last time**                                                                                | **TODO's**                                        | **Blockers** |
| Irreflexive     | Added prompts to ChatGPT for database commands (in special_prompts.py)                                 | Use prompts to ask ChatGPT questions              |              |
| madhav_ucsb     |                                                                                                        |                                                   |              |
| awesomebob35    | Setup the microphone and uploaded video of tests. Tested reading audio input and playing it as output. | Integrate with text to speech and speech to text. |              |

| Week 8          | Planned meeting date 11/23                                                                                                                                                |                                                                                                                     |              |
|:----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|:-------------|
| **Participant** | **Done from last time**                                                                                                                                                   | **TODO's**                                                                                                          | **Blockers** |
| Irreflexive     | Added full command processing to prompts.py. Text input will now be processed by ChatGPT, and commands to toggle/assign pins will be processed with human-friendly output | Constrain assignable pins to those not in use (for mic/speakers/etc). Work with Joseph to figure out speech to text |              |
| madhav_ucsb     |                                                                                                                                                                           |                                                                                                                     |              |
| awesomebob35    | Integrated audio code with text to speech. We should now be able to playback ChatGPT responses as audio.                                                                  | Have not yet figured out how to setup speech to text                                                                |              |

| Week 9          | Planned meeting date 11/30                                                                                                                                                                                                                                                                   |                                                                                                                                         |              |
|:----------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------|:-------------|
| **Participant** | **Done from last time**                                                                                                                                                                                                                                                                      | **TODO's**                                                                                                                              | **Blockers** |
| Irreflexive     | Added configuration options to prevent certain pin numbers from being modified/accessed in the database. At our meeting, discussed with Joseph how we are currently determining when to accept user input.                                                                                   | Manipulate Raspberry Pi GPIO pins in prompt callbacks directly, and initialize pins based on database configuration on program startup. |              |
| madhav_ucsb     |                                                                                                                                                                                                                                                                                              |                                                                                                                                         |              |
| awesomebob35    | Made system more user friendly by adding audio output to signify when recording stops/starts, although this may be changed if we figure out how to implement a voice activation command. Also created dedicated function for playing audio, which should make code easier to read/work with. | Continue working on integrating speech to text                                                                                          |              |

| Week 10         | Planned meeting date 12/7                                                                                                                                                                                                                                                                                  |                                                     |              |
|:----------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------|:-------------|
| **Participant** | **Done from last time**                                                                                                                                                                                                                                                                                    | **TODO's**                                          | **Blockers** |
| Irreflexive     | Implemented setup script for Raspberry Pi GPIO pins and manipulated pins on voice command. Moved local memory conversation data storage to a persistent PostgresSQL table. Cached the most recent response so duplicate back-to-back requests do not need to be sent to ChatGPT. Worked on final write-up. | Complete documentation and record final demo video. |              |
| madhav_ucsb     |                                                                                                                                                                                                                                                                                                            |                                                     |              |
| awesomebob35    | Set up the lights hardware to and integrated with the device. Also added finishing touches to device including voice activation and indicator lights. | Device is completed |              |