# CraftyBot

## Configuration
### Crafty Controller setup requirements:
1) Create a new role
2) Create a new user
3) Assign user to role

For each server that you want CraftyBot to have access to and control, check 'Access?' and 'COMMANDS'. Optionally, check 'SCHEDULE' if you wish for a task to automatically start and stop with the server.

### CraftyBot setup requirements:
Open `config.py` to update and configure your CraftyBot. 

## Setup
### Docker (Recommended)
1. Install [Docker Engine](https://docs.docker.com/engine/install/) and run `sudo apt install git` if things are not already installed.
2. Run the following command to download the bot:
```bash
git clone https://github.com/Nexumi/CraftyBot.git
```
3. Run the following command to start the bot:
```bash
sudo docker compose up -d --build
```
4. Run the following command to stop the bot:
```bash
sudo docker compose down
```

### Direct
1. Install [Python3](https://www.python.org/downloads/) if it isn't already installed.
2. Run the following command to install the require packages (required once):
```
pip install -U py-cord requests
```
3. Run the following command to start the bot:
```
python main.py
```

### Running As A Service
There is an excellent [guide](https://jmusicbot.com/running-as-a-service/) for running JMusicBot as a service.
The only thing that is really different aside from the the name is the execution command:
```
python main.py
```
