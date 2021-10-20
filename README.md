# ali-ddns
A python script used for ddns on aliyun.
# Usage
## Download from the release

* Running the .exe file in the release does not python installed on your computer, 
so it may be useful if you want to use ddns on a server.
* 1. Download the latest release in the and unpack the .zip file into any directory.
Be sure to keep the `aliddns.exe` and `settings.json` in the same folder.
* 2. Open the `settings.json` with any text editor and fill in all the information.
Remember to fill in the `accessKeyId` and `accessSecrect` field.

## Using the python .py script directly

* 1. Install the packages listed in `requirements.txt`.
* 2. Open `settings.json` using any text editor and fill in the information.
Be sure to fill in `accessKeyId` and `accessSecrect`.
* 3. Since the script will not output anything into the console but write the
outcomes of the running into the logfile, you may want to change the script's
extension from .py into .pyw so the script will run in th background.

# Todos
1. A new class for managing settings
