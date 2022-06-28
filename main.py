import requests
import threading
import datetime
import sqlite3
import time


RUNNING_SCRIPT = True

previous_checkpoint=0
previous_block=0

def init_tables():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    checkpoints_table = '''
    CREATE TABLE IF NOT EXISTS checkpoints (
	signer VARCHAR(255) NOT NULL,
   	checkpoint INTEGER NOT NULL,
	signed_in TIMESTAMP NOT NULL,
	PRIMARY KEY(signer,checkpoint,signed_in)
    );
    '''
   
    blocks_table = '''
    CREATE TABLE IF NOT EXISTS blocks (
	signer VARCHAR(255) NOT NULL,
   	block INTEGER NOT NULL,
	signed_in TIMESTAMP NOT NULL,
	PRIMARY KEY(signer,block,signed_in)
    );
    '''

    networks_table = '''
    CREATE TABLE IF NOT EXISTS  validators
    (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    validator_id INTEGER UNIQUE NOT NULL,
    signer VARCHAR(255) NOT NULL);
    '''
    cursor.execute(blocks_table)
    cursor.execute(networks_table)
    cursor.execute(checkpoints_table)
    cursor.connection.commit()
    connection.close()

init_tables()

def datetime_now():
    return str(datetime.datetime.now())

def persistCheckpoint(signer,checkpoint):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("insert into checkpoints values (?, ?, ?)", (signer,checkpoint,datetime_now()) )
    cursor.connection.commit()
    connection.close()

def persistBlock(signer,block):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("insert into blocks (signer,block,signed_in) values (?, ?, ?)", (signer,block,datetime_now()) )
    cursor.connection.commit()
    connection.close()

def charge_validators():
    validators = []
    print('t='+str(datetime.datetime.now())+ ' type=Info message=CHARGING_VALIDATORS_FROM_DATABASE')
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM validators;")
    for validator in cursor.fetchall():
        print(validator)
        validator_instance={
            'name':validator[1],
            'validator_id':validator[2],
            'signer':validator[3]
        }
        validators.append(validator_instance)
    
    connection.close()

    print('t='+str(datetime.datetime.now())+ ' type=Info message=FINISH_CHARGE_NETWORKS_FROM_DATABASE')
    return validators

charge_validators()

class getNetworkBlockDataThread(threading.Thread):
    def __init__(self,block):
        threading.Thread.__init__(self)
        self.block = block
    

    def run(self):
        print('RUNNING GET NETWORK BLOCK DATA: '+ str(self.block))
        r = requests.get('https://heimdall.api.matic.network/blocks/'+str(self.block))
        signers = r.json()['block']['last_commit']['precommits']
        validators_db = charge_validators()
        validators_set = {}

        for signer in signers:
            key='0x'+str(signer['validator_address']).lower()
            print(key)
            validators_set[key]=True
        print(validators_set)
        for validator in validators_db:
            print(validators_set.get(validator['signer']))
            if validators_set.get(validator['signer'])==None:
                persistBlockTread = persistBlockDataThread(validator['signer'],self.block,datetime_now())
                persistBlockTread.start()
        
        

class getNetworkCheckpointDataThread(threading.Thread):
    def __init__(self,checkpoint):
        threading.Thread.__init__(self)
        self.checkpoint = checkpoint
    

    def run(self):
        print('RUNNING GET NETWORK CHECKPOINT DATA: '+ str(self.checkpoint))
        r = requests.get('https://sentinel.matic.network/api/v2/monitor/checkpoint-signatures/checkpoint/'+str(self.checkpoint))
        signers = r.json()['result']
        validators_db = charge_validators()
        validators_set = {}

        for signer in signers:
            validators_set[signer['signerAddress']]=signer['hasSigned']
        '''
        '''
        for validator in validators_db:
            if bool(validators_set[validator['signer']])==False:
                persistCheckpointTread = persistCheckpointDataThread(validator['signer'],self.checkpoint,datetime_now())
                persistCheckpointTread.start()

class persistCheckpointDataThread(threading.Thread):
    def __init__(self,signer,checkpoint,signed_in):
        threading.Thread.__init__(self)
        self.signer = signer
        self.checkpoint = checkpoint
        self.signed_in = signed_in
    

    def run(self):
        print('RUNNING PERSIST MISSED CHECKPOINT '+ str(self.checkpoint) + ' ' +  str(self.signer))
        persistCheckpoint(self.signer,self.checkpoint)

class persistBlockDataThread(threading.Thread):
    def __init__(self,signer,block,signed_in):
        threading.Thread.__init__(self)
        self.signer = signer
        self.block = block
        self.signed_in = signed_in    

    def run(self):
        print('RUNNING PERSIST MISSED BLOCK '+ str(self.block) + ' ' +  str(self.signer))
        persistBlock(self.signer,self.block)

class collectNetworkInfoDataThread(threading.Thread):
    def __init__(self,previous_checkpoint,previous_block):
        threading.Thread.__init__(self)    
        self.previous_block = previous_block
        self.previous_checkpoint=previous_checkpoint
    def run(self):
        print("| Start Collect block Thread |")        
        while(RUNNING_SCRIPT):  
            #GET LAST INFO FROM POLYGON NETWORK
            r = requests.get('https://heimdall.api.matic.network/checkpoints/count')
            last_block = r.json()['height']
            last_checkpoint = r.json()['result']['result']           
            

            if self.previous_checkpoint < int(last_checkpoint):
                print('t='+datetime_now()+" type=Info message=NETWORK_CHANGE_TO_CHECKPOINT_"+str(last_checkpoint))
                print('RUNNING THREAD GET CHECKPOINT DATA')
                self.previous_checkpoint = int(last_checkpoint)
                getCheckpointThread = getNetworkCheckpointDataThread(last_checkpoint)
                getCheckpointThread.start()

            if self.previous_block < int(last_block):
                print('RUNNING THREAD GET BLOCK DATA')
                print('t='+datetime_now()+" type=Info message=NETWORK_CHANGE_TO_BLOCK_"+str(last_block))
                self.previous_block = int(last_block)
                getBlockThread = getNetworkBlockDataThread(last_block)
                getBlockThread.start()
            
            '''
            block_signed=False
            for signature in signatures_blocks:
                if signature['validator_address']==networkObject['signer']:
                    print('t='+str(datetime.datetime.now())+ ' type=Info signed=true block='+str(block)+ ' network='+networkObject['name'] + ' signed_in=' + signature['timestamp'] )
                    block = block
                    network = networkObject['name']
                    signed = True
                    signed_in  = signature['timestamp']
                    #row_timestamp = datetime.datetime.strptime(signature['timestamp'],'%d/%m/%Y').__str__()
                    try:
                        
                        connection = sqlite3.connect('database.db')
                        cursor = connection.cursor()
                        cursor.execute("insert into blocks values (?, ?, ?, ?)", (network,block,signed,signed_in) )
                        cursor.connection.commit()
                        connection.close()
                       
                    except Exception as e:
                        print('t='+str(datetime.datetime.now())+" type=Error message="+str(e))
                    block_signed=True
            
            if(block_signed==False):
                print('t='+str(datetime.datetime.now())+ ' type=Info signed=false block='+str(block)+ ' network='+networkObject['name'] + ' signed_in=' + block_time )
                block = block
                network = networkObject['name']
                signed = False
                signed_in = block_time
                try:
                    connection = sqlite3.connect('database.db')
                    cursor = connection.cursor()
                    cursor.execute("insert into blocks values (?, ?, ?, ?)", (network,block,signed,signed_in) )
                    cursor.connection.commit()
                    connection.close()
                except Exception as e:
                    print('t='+str(datetime.datetime.now())+" type=Error message="+str(e))
            '''    
            time.sleep(1)
        print("| Finish Thread |")


netthread = collectNetworkInfoDataThread(previous_checkpoint,previous_block)
netthread.start()