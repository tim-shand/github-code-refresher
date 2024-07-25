"""
Description:
- Automate code refresh from private Github repo. 
- Download latest source code from defined private Github repository.
- Uses a local '.config' file containing Github repo/path source and API (PAT) token.
- Replaces existing local production copy with newly downloaded code. 
- Generates log file of processes for review purposes. 
- Designed to be run as a cron job or with other automation. 
Author: Tim Shand
Email: tim@tshand.com
Created: 25/07/2024

# Example ".config' JSON file. Store in same working directory.
{"config": { 
	"urls": [{"id":"1","value":"https://api.github.com/repos/<OWNER>/<REPO>/contents/<DIR>/<FILE>"}],
	"tokens": [{"id":"1","value": "<PAT>"}]
}}

"""

### Import required modules.
from pathlib import Path
import logging
import json
import requests
import os
import base64
from datetime import datetime

### Define Functions.
# Check for required config file.
def fileCheck(filePath):
    return os.path.exists(filePath)

# Function: Read in and validate local configuration file.
def readConfig():
    # Open file and read content into variable 'jsonData'.
    with open(Path(cfgFile), 'r') as jsonData:
        data = json.load(jsonData)
    # Check returned data type is correct (dictionary).
    if type(data) is dict:
        try:
            token: str = (data['config']['tokens'][0]['value'])
            url: str = (data['config']['urls'][0]['value'])
            return token, url
        except:
            logging.error("Failed to read config data content.")
    else:
        logging.error("Config data type is invalid - (is:",type(data)," should be: 'dict').")
    
# Function: Download latest code from repository.
def refreshCode(token,url,destFile):
    logging.info("Downloading latest code.")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            # Response is base64 encoded, decode to get the actual content.
            content = response.json().get("content", "")
            decoded_content = base64.b64decode(content).decode("utf-8")
            with open(destFile,'w') as f:
                f.write(decoded_content)
        except:
            logging.error("Failed to process received response content.")
    else:
        logging.error(f"Failed to retrieve file. Status Code: {response.status_code}")
    return response.status_code

# Function: Replace the production code with new downloaded code. 
def codeReplace(destFile,prodFile):
    # Replace production code with new code. 
    try:
        logging.info("Backing up production code.")
        os.rename(prodFile, prodFile +"_"+ datetime.today().strftime("%Y%m%d-%H%M%S"))
        os.rename(destFile, prodFile)
        logging.info("Production code updated successfully.")
    except OSError:
        logging.error("Failed to update production code.")
        pass

# Function: Main Process
def main():
    logging.info("----- Begin -----")
    # Check for required config file.
    if fileCheck(cfgFile):
        # Read config file to get connection values.
        config = readConfig() # Read output of function into variable of type 'tuple'.
        if config and type(config) is tuple:
            response_code = refreshCode(config[0],config[1],destFile)            
            # Check response code and if downloaded file exists.
            if response_code == 200 and fileCheck(destFile):
                logging.info("Code download successful.")
                codeReplace(destFile,prodFile)
            else:
                logging.error("File download is missing! Request may have failed. Abort.")
        else:
            logging.error("Failed to read config file. Abort.")
    else:
        logging.error("Config file is missing! Abort.")

### Main ###
# Anything within this 'if' statement will not get run on import.
if __name__ == "__main__":
    # Define Variables.
    workingDir: str = "./"
    cfgFile: str = workingDir+"//.config" # "//.config-example"
    destFile: str = workingDir+"/payload.py"
    prodFile: str = workingDir+"/target_file.py"
    logFile: str = workingDir+"/refresh_code.log"
    # Configure logging. 
    logging.basicConfig(filename=logFile,
        filemode='a',
        format='%(asctime)s.%(msecs)d %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO #DEBUG, INFO, ERROR
    )
    # Run
    main()
# EOF