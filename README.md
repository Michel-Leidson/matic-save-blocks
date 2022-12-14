#  Missed Blocks and Checkpoints Report

### Update the system

```
sudo apt update && sudo apt upgrade -y
```
### 1 - Download project

```
git clone https://github.com/Michel-Leidson/matic-save-blocks.git
```

### Enter in directory
```
cd matic-save-blocks
```
### 2 - Install pyhton3-venv

```
sudo apt install python3-venv
```
### 3 - Create virtual environment for the project

```
python3 -m venv venv
```

### 4 - Activate virtual environment

```
source venv/bin/activate
```

### 5 - Install project dependencies

```
pip install -r requirements.txt
```

### 6 - Run the project for the first time to create the database

```
python3 main.py
```

### Exit in the service
```
Stop the service by typing 'ctrl' + 'c' on the keyboard.
```
### 7 - Install sqlite3 to manipulate the database

```
sudo apt install sqlite3
```

### 8 - Access database

```
sqlite3 database.db
```

### 9 - Add the validators you want to monitor, the subscriber key, and the Query API URL. Type .quit to exit the sqlite3 application

```
sqlite> INSERT INTO validators (name,validator_id,signer) VALUES('StakePool',32,'0x02f70172f7f490653665c9bfac0666147c8af1f5');
sqlite> .quit
```
### 10 - Create matic-save-blocks service file and running

Create a running file

```
nano running-matic-save-blocks.sh
```

Put this content in the file (replace '/your-absolute-path-to-project' with the absolute path where your project is)

```
#!/bin/bash

cd /your-absolute-path-to-project/matic-save-blocks/
source venv/bin/activate
python3 main.py
```

Make this script executable

```
chmod +x running-matic-save-blocks.sh
```
Create service file

```
nano /etc/systemd/system/matic-save-blocks.service
```

Put this content in the file (replace '/your-absolute-path-to-running-file' with the absolute path where your running file is)

```
[Unit]
Description=Matic Save Blocks
After=syslog.target network.target

[Service]
Type=simple
User=root
ExecStart=/your-absolute-path-to-running-file/running-matic-save-blocks.sh
Restart=on-failure

StandardOutput=append:/var/log/matic-save-blocks-out.log
StandardError=append:/var/log/matic-save-blocks-err.log

[Install]
WantedBy=multi-user.target
```

Create log files for service

```
cd /var/log
touch matic-save-blocks-out.log
touch matic-save-blocks-err.log
```

Reload service files

```
sudo systemctl daemon-reload
```

Start service

```
sudo service matic-save-blocks start
```

Enable start service in boot

```
sudo enable matic-save-blocks
```
### 11 - Verify status service

```
sudo systemctl status cosmos-save-blocks
● cosmos-save-blocks.service - Cosmos Save Blocks
     Loaded: loaded (/etc/systemd/system/matic-save-blocks.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2022-08-17 02:58:26 UTC; 3 days ago
   Main PID: 894191 (running-matic-)
      Tasks: 26 (limit: 19190)
     Memory: 161.4M
     CGroup: /system.slice/matic-save-blocks.service
             ├─894191 /bin/bash /your-absolute-path-to-running-file/running-matic-save-blocks.sh
             └─894195 python3 main.py
```

### 12 - Check application logs. If everything is working fine you will see records like these
```
RUNNING PERSIST MISSED BLOCK 10187313 0x33cc92f536f7523ba52ae8eb8a162e1ab87f8285
RUNNING PERSIST MISSED BLOCK 10187313 0x77ee14d1a9ba7130b686b736a316b5bf1d3ccb36
RUNNING THREAD GET BLOCK DATA
t=2022-07-19 14:03:20.806021 type=Info message=NETWORK_CHANGE_TO_BLOCK_10187314
RUNNING GET NETWORK BLOCK DATA: 10187314
t=2022-07-19 14:03:20.911371 type=Info message=CHARGING_VALIDATORS_FROM_DATABASE
t=2022-07-19 14:03:20.911839 type=Info message=FINISH_CHARGE_NETWORKS_FROM_DATABASE
'NoneType' object is not subscriptable
'NoneType' object is not subscriptable
```

### 13 - To generate the report just activate the python virtual environment again and run the report generation script

Enter in your project directory

```
cd matic-save-blocks
```
```
source venv/bin/activate
```
### Generating Blocks report
```
python3 generate_report_blocks.py
```
### Generating Checkpoints report
```
python3 generate_report_checkpoints.py
```
