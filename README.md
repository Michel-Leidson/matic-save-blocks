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

### 9 - Add the networks you want to monitor, the signer key and the query api url. Type .quit to exit sqlite3 application

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
