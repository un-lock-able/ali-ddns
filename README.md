# ali-ddns
A python script used for ddns on aliyun.
# Usage
## Download from the release

* Running the .exe file in the release does not need python installed on your computer, 
so it may be useful if you want to use ddns on a server.
1. Download the latest release in the release section and unpack the .zip file into any directory.
Be sure to keep the `aliddns.exe` and `aliddnsSettings.json.example` in the same folder.
2. Copy the `aliddnsSettings.json.example` to a new file and rename the new file into `aliddnsSettings.json`.
3. Open the `aliddnsSettings.json` with any text editor and fill in all the information.
Remember to fill in the `accessKeyId` and `accessSecrect` field and delete any extra entries in the `domainSettings` list.

## Using the python .py script directly

1. Install the packages listed in `requirements.txt`.
2. Open `aliddnsSettings.json` using any text editor and fill in the information.
It is recommended to backup the original file.
Be sure to fill in `accessKeyId` and `accessSecrect`.
3. Run main.py using python interpreter.
* Since the script will not output anything into the console but write the
outcomes of the running into the logfile, you may want to change the script's
extension from .py into .pyw so the script will run in th background.

# Todos
- [x] A new class for managing settings
- [ ] New function: read configuration file name from command line arguments list
