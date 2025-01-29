"""
    Utilities
"""
import json, os, dotenv, time
from datetime import datetime

# Loading .env values
dotenv.load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CONSOLE_URL = os.getenv('CONSOLE_URL')
ENV = os.getenv('ENV')
RETENTION_LOGS_DAYS = int(os.getenv('RETENTION_LOGS_DAYS'))

def writeJsonToFile(text):
    with open('debugOutput.json', 'w') as f:
        f.write(json.dumps(json.loads(text), indent=2))

def cleanupOldLogFiles():
    path = os.path.join(os.getcwd(), "logs")
    now = time.time()
    for filename in os.listdir(path):
        filestamp = os.stat(os.path.join(path, filename)).st_mtime
        if filestamp < now - RETENTION_LOGS_DAYS * 86400:
            os.remove(os.path.join(path, filename))

def writeToLogFile(text):
    filename = f"{str(datetime.today().year)}-{str(datetime.today().month)}-{str(datetime.today().day)}.log"
    with open(os.path.join("logs", filename), "w") as f:
        f.write(f"{str(datetime.today().hour)}:{str(datetime.today().second)} {text}")
    cleanupOldLogFiles()

def output(text, doExit = False):
    if ENV == "local":
        print(text)
    elif ENV == "prod":
        writeToLogFile(text + "\n")
    else:
        print("FATAL ERROR: Unknown ENV variable. Please use local|prod values.")
        writeToLogFile(f"FATAL ERROR: Unknown ENV variable. Please use local|prod values.")
        exit()
    if doExit:
        exit()