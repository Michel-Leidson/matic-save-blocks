#  Missed Blocks and Checkpoints Report

### Update the system

```
sudo apt update && sudo apt upgrade -y
```
### 1 - Download project

```
git clone git@github.com:Michel-Leidson/matic-save-blocks.git
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
### If everything is working fine you will see records like these
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
RUNNING PERSIST MISSED BLOCK 10187314 0x33cc92f536f7523ba52ae8eb8a162e1ab87f8285
RUNNING PERSIST MISSED BLOCK 10187314 0x77ee14d1a9ba7130b686b736a316b5bf1d3ccb36
RUNNING THREAD GET BLOCK DATA
t=2022-07-19 14:03:28.215604 type=Info message=NETWORK_CHANGE_TO_BLOCK_10187315
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
### 10 - Install screen

```
sudo apt install screen
```

### 11 - Open screen session to let it run in background

```
screen
```
### run
```
python3 main.py
```
### 12 - Exit screen session without closing


Type 'ctrl' + 'a' in keyboard, after type 'd'


### 13 - To generate the report just activate the python virtual environment again and run the report generation script

```
pip install fpdf
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
