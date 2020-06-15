# PyKeeSAP

The PyKeeSAP is SAP Password Manager. All SAP passwords stored in the [KeePass Database](https://keepass.info/). 

Main features:
* The password to the KeePass Database file you can enter each time using PyKeeSAP or set password in PyKeeSAP configuration file (settings.ini).
* Create or delete entries in the KeePass Database.
* Passwords stored in the KeePass Database. You can manually see SAP users and passwords in the KeePass Database at any time.
* Automatically log in to SAP system specifing only SAP system ID with account from KeePass Database. No need to start SAP Logon, find connection, retrieve the passwords. For security reasons user passwords must contain digits, specials, upper- and lowercase letters. So it's difficult to remember. Do not forget each user account should has own password (not same). 
* If needed to change password while login PyKeeSAP set new password and update the entry in KeePass Database.
* Change password to SAP user in one command (using transaction SU3). Password generator is integrated. In case of compromise, the password may be quickly changed in SAP system at any time in few seconds.
* Automatically log in to SAP systems using all user accounts in the KeePass Database. Thus productive passwords won't never be expired by inactive password period (set by login/password_max_idle_productive).
* Automatically change passwords to all user accounts in the KeePass file. Usually for security reasons the passwords of technical and service accounts must be changed at specifyed period of time (for example annually). SAP NetWeaver platform doesn't control and promt it.


## Table of contents

* [ToC](#table-of-contents)
* [Python installation](#python-installation)
* [Install](#install)
* [Before running](#before-running)
* [Usage](#usage)

## Python installation
1. Download [last version of Python 3.x installer](https://www.python.org/downloads/)
2. Run the installer
3. While installation choose folowing option:
    - Add python 3.x to PATH

## Install

### Pip installation (recomended)
Installation is easy. Run in windows console (command line interpreter - cmd):
```sh
pip install PyKeeSAP
```
If your computer is behind a proxy set additional option --proxy in following format: 
```sh
pip install sapsec --proxy http://user:password@proxyserver:port
```

### Installation from github
If for some reason the installation was not successful (with pip) there is an opportunity to install sapsec from github source files.
1. Download [zip archive](https://github.com/gutskodv/PyKeeSAP/archive/master.zip) with project source codes. Or use git clone:
```sh
git clone https://github.com/gutskodv/PyKeeSAP.git
```
2. Unpack files from dowloaded zip archive. And go to project directory with setup.py file.
3. Ugrade pip, Install Wheel package, Collect sapsec package:
```sh
python -m pip install --upgrade pip
pip install wheel
python setup.py bdist_wheel
```
4. Install sapsec package from generaed python wheel in dist subdirectory:
```sh
python setup.py dist\PyKeeSAP*.whl
```

### Requirements
You can manually intall requirements if they were not installed in automatic mode.
1. PyWin32 (Python extensions for Microsoft Windows Provides access to much of the Win32 API, the ability to create and use COM objects, and the Pythonwin environment).
```sh
pip install pywin32
```
2. PySapGUI (SAP GUI Scripting Library).
```sh
pip install PySapGUI
```

## Before running
1. Download and install [KeePass](https://keepass.info/) software.
2. Manualy create KeePass Database file. Set strong password to Database and may specify additional key file.
3. Run PyKeeSAP and understand path to settings.ini file
```sh
pykeesap -h
```
4. Configure settings.ini file:
  - Set LocalSaplogonINI - Path to local saplogon.ini file
  - Set (optionally) GlobalSaplogonINI - Path to cashed additional saplogon.ini file from server
  - Set SaplogonEXE - Path to saplogon.exe file (SAP Logon Application)
  - Set KeePassFile - Path to the created KeePass Database file
  - Set (optionaally) KeePassPassword - Password to open the created KeePass Database file
  - Set (optionally) KeePassKeyFile - Path to key file (if used) 
  - Modify (optionally) password policy to generated passwords
5. Enable SAP GUI scripting to entire SAP system or some users.
  
  ## Usage
  1. To print accounts in the KeePass Database execute one of the following commands:
```sh
pykeesap print
pykeesap print -s TST
```
2. To create new user account in the KeePass Database execute one of the following commands:
```sh
pykeesap create TST -u TESTUSER01 -p password123
pykeesap create TST -c 000 -u TESTUSER02 -p password123
```
3. To log in to SAP (using user account in the KeePass Database file) execute one of the following commands:
```sh
pykeesap login TST
pykeesap login TST -c 001
pykeesap login TST -t TESTUSER01-TST
pykeesap login TST -t TESTUSER02-TST-000
```
4. To multi log in to SAP execute (reset inactive password counters):
```sh
pykeesap multilogin
```

5. To multi change the user passwords:
```sh
pykeesap multichangepwd
```
