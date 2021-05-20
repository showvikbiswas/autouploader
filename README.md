# AutoUploader v1.0

Python automation script I made for work. Uploads checked answer scripts to Google Drive easily and efficiently.

1. Python
2. pip
3. Google Drive API

We'll look at how to properly configure your computer so that you can run the Python script. If you have these installed, please skip to [**Using the Script**](#using-the-script).

## Python ##
Download the latest version of Python from https://www.python.org/downloads/ and install. This should not be a problem. Restart your computer to ensure that .py files are associated with the Python interpreter.

## pip ##
Download pip from https://bootstrap.pypa.io/. You should download the get-pip.py file. Once downloaded, run the file to install pip. (Note: This step depends on proper completion of the last step.)

## Google Drive API ##
To install the Google Drive API, open Command Prompt and run the following command:
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
