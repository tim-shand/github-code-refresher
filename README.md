# Github Code Refresher
**_Automate the download of the latest target file from private Github repository._**   
- Uses a local '.config' file containing Github repo/path source and API (PAT) token.
- Renames original local production target file with newly downloaded code. 
- Generates log file of processes for audit/review purposes. 
- Designed to be run as a cron job or used with other automation/scripts. 

### Example ".config' JSON file. 
- Store in same working directory, or set as environment variable and modify script to use that.   
```
{"config": { 
	"urls": [{"id":"1","value":"https://api.github.com/repos/<OWNER>/<REPO>/contents/<DIR>/<FILE>"}],
	"tokens": [{"id":"1","value": "<PAT>"}]
}}
```

### Usage
```
> python refresh_code.py
```