import requests
import threading
import datetime
import sqlite3
import time


RUNNING_SCRIPT = True

previous_checkpoint=0
previous_block=0
invalid_checkpoint_list=[]

def get_list_past_checkpoints():
    checkpoint_list=[]
    for checkpoint in range(5313,12000):
        print(checkpoint)
        checkpoint_list.append(checkpoint)
    return checkpoint_list


def has_checkpoint_in_db(checkpoint):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
   
    consult_checkpoint_in_db = f'''
    SELECT checkpoint FROM checkpoints WHERE checkpoint = {checkpoint}
    '''
    cursor.execute(consult_checkpoint_in_db)
    checkpoints_list = cursor.fetchall()
       
    connection.close()
    if len(checkpoints_list) > 0 :
        return True
    
    return False


def delete_invalid_checkpoint(checkpoint_height):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
   
    delete_invalid_checkpoints = f'''
    DELETE FROM checkpoints WHERE checkpoint = {checkpoint_height}
    '''
    cursor.executescript(delete_invalid_checkpoints)    
    connection.close()


def check_invalid_checkpoints():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
   
    consult_invalid_checkpoints = '''
    SELECT checkpoint,COUNT(signer) FROM checkpoints GROUP BY checkpoint
    '''
    cursor.execute(consult_invalid_checkpoints)
    checkpoints_list = cursor.fetchall()
    invalid_checkpoints_list=[]
    for checkpoint in checkpoints_list:
        number_of_validators_not_siged = checkpoint[1]
        checkpoint_height=checkpoint[0]
        if number_of_validators_not_siged > 50 :
            print("The checkpoint",checkpoint_height,"is invalid!")
            invalid_checkpoints_list.append(checkpoint_height)

    connection.close()
    return invalid_checkpoints_list

def init_tables():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    checkpoints_table = '''
    CREATE TABLE IF NOT EXISTS checkpoints (
	signer VARCHAR(255) NOT NULL,
   	checkpoint INTEGER NOT NULL,
	signed_in TIMESTAMP NOT NULL,
	PRIMARY KEY(signer,checkpoint)
    );
    '''
   
    blocks_table = '''
    CREATE TABLE IF NOT EXISTS blocks (
	signer VARCHAR(255) NOT NULL,
   	block INTEGER NOT NULL,
	signed_in TIMESTAMP NOT NULL,
	PRIMARY KEY(signer,block)
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

def persistCheckpoint(signer,checkpoint,signed_in):
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("insert into checkpoints values (?, ?, ?)", (signer,checkpoint,signed_in) )
        cursor.connection.commit()
        connection.close()
    except Exception as e:
        print(e)

def persistBlock(signer,block,signed_in):
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("insert into blocks (signer,block,signed_in) values (?, ?, ?)", (signer,block,signed_in) )
        cursor.connection.commit()
        connection.close()
    except Exception as e:
        print(e)

def charge_validators():
    validators = []
    print('t='+str(datetime.datetime.now())+ ' type=Info message=CHARGING_VALIDATORS_FROM_DATABASE')
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM validators;")
    for validator in cursor.fetchall():
        #print(validator)
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
        block_time = r.json()['block']['header']['time']
        #print(signers)
        validators_db = charge_validators()
        validators_set = {}

        for signer in signers:
            try: 
                key='0x'+str(signer['validator_address']).lower()
                
                #print(key)
                validators_set[key]=True
            except Exception as e:
                print(e)
        #print(validators_set)
        for validator in validators_db:
            #print(validator)
            if validators_set.get(validator['signer'])==None:
                persistBlockTread = persistBlockDataThread(validator['signer'],self.block,block_time)
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
        checkpointsSignersNumber=0
        checkpointTime=datetime_now()
        for signer in signers:
            try:
                if signer['hasSigned']==True:
                    checkpointsSignersNumber=checkpointsSignersNumber + 1
                #print("SIGNER: ",signer['signerAddress'], signer['hasSigned'])
                validators_set[signer['signerAddress']]=signer['hasSigned']
            except Exception as e:
                print(e)
        print("Number of signers: ",checkpointsSignersNumber)
        if checkpointsSignersNumber > 50:
            getFirstSigner =False
            
            for validator in validators_db:            
                try:
                    if validators_set[validator['signer']]==True and getFirstSigner==False:
                        try:
                            getFirstSigner=True
                            validatorId=validator['validator_id']
                            url=f'''https://sentinel.matic.network/api/v2/validators/{validatorId}/checkpoints-signed?limit=1&offset=0'''
                            r2 = requests.get(url)
                            checkpointTime=r2.json()['result'][0]['timestamp']
                            checkpointTime=datetime.datetime.fromtimestamp(checkpointTime)
                            print("CHECKPOINT TIME",checkpointTime.strftime("%Y-%m-%d %H:%M:%S"),"BASED IN VALIDATOR",validator['name'])
                        except Exception as e:
                            print(e)

                    if validators_set[validator['signer']]==False:
                        persistCheckpointTread = persistCheckpointDataThread(validator['signer'],self.checkpoint,checkpointTime)
                        persistCheckpointTread.start()
                except Exception as e:
                    print(e)
        else:
            previous_checkpoint = previous_checkpoint - 1

class persistCheckpointDataThread(threading.Thread):
    def __init__(self,signer,checkpoint,signed_in):
        threading.Thread.__init__(self)
        self.signer = signer
        self.checkpoint = checkpoint
        self.signed_in = signed_in
    

    def run(self):
        print('RUNNING PERSIST MISSED CHECKPOINT '+ str(self.checkpoint) + ' ' +  str(self.signer))
        persistCheckpoint(self.signer,self.checkpoint,self.signed_in)

class persistBlockDataThread(threading.Thread):
    def __init__(self,signer,block,signed_in):
        threading.Thread.__init__(self)
        self.signer = signer
        self.block = block
        self.signed_in = signed_in    

    def run(self):
        print('RUNNING PERSIST MISSED BLOCK '+ str(self.block) + ' ' +  str(self.signer))
        persistBlock(self.signer,self.block,self.signed_in)

class collectNetworkInfoDataThread(threading.Thread):
    def __init__(self,previous_checkpoint,previous_block):
        threading.Thread.__init__(self)    
        self.previous_block = previous_block
        self.previous_checkpoint=previous_checkpoint
    def run(self):
        print("| Start Collect block Thread |")        
        while(RUNNING_SCRIPT):  
            #GET LAST INFO FROM POLYGON NETWORK
            try:
                r = requests.get('https://heimdall.api.matic.network/checkpoints/count')
                last_checkpoint = r.json()['result']['result']           
                last_block=r.json()['height']
                
                    
                if self.previous_checkpoint < int(last_checkpoint):

                    r3 = requests.get('https://sentinel.matic.network/api/v2/monitor/checkpoint-signatures/checkpoint/'+str(last_checkpoint))
                    signers = r3.json()['result']
                    checkpointsSignersNumber=0
                    for signer in signers:
                        try:
                            if signer['hasSigned']==True:
                                checkpointsSignersNumber=checkpointsSignersNumber + 1
                        except Exception as e:
                            print(e)
                    print("Number of signers: ",checkpointsSignersNumber)
                    if checkpointsSignersNumber > 50:
                        print('t='+datetime_now()+" type=Info message=NETWORK_CHANGE_TO_CHECKPOINT_"+str(last_checkpoint))
                        print('RUNNING THREAD GET CHECKPOINT DATA')
                        if has_checkpoint_in_db(int(self.previous_checkpoint)) == False and int(self.previous_checkpoint) != 0:
                            print("RUNNING THREAD GET PREVIOUS CHECKPOINT DATA")
                            getPreviousCheckpointThread = getNetworkCheckpointDataThread(self.previous_checkpoint)
                            getPreviousCheckpointThread.start()
                        else:
                            self.previous_checkpoint = int(last_checkpoint)
                            getCheckpointThread = getNetworkCheckpointDataThread(last_checkpoint)
                            getCheckpointThread.start()
                    else:
                        print("THE SIGNERS MINIMUM HAS NOT BEEN REACHED")           
                
                #print('t='+datetime_now()+" type=Info message=NETWORK_COLLECTED_CHECKPOINT_"+str(last_checkpoint))
                
                #print('t='+datetime_now()+" type=Info message=NETWORK_COLLECTED_BLOCK_"+str(last_block))
                if self.previous_block < int(last_block):
                    print('RUNNING THREAD GET BLOCK DATA')
                    print('t='+datetime_now()+" type=Info message=NETWORK_CHANGE_TO_BLOCK_"+str(last_block))
                    self.previous_block = int(last_block)
                    getBlockThread = getNetworkBlockDataThread(last_block)
                    getBlockThread.start()         
            
                time.sleep(1)
            except Exception as e:
                print(e)
        print("| Finish Thread |")

class checkInvalidCheckpoints(threading.Thread):
    def __init__(self,invalid_checkpoint_list):

        threading.Thread.__init__(self)    
        self.invalid_checkpoint_list = invalid_checkpoint_list
    def run(self):
        print("| Start checkInvalidCheckpoints |")
        invalid_checkpoints=check_invalid_checkpoints()
        print(invalid_checkpoints)
        for checkpoint in invalid_checkpoints:
            print(checkpoint)
            checkpoint_height=checkpoint[0]
            print("RUNNING_DELETE_INVALID_CHECKPOINT_"+str(checkpoint_height))
            delete_invalid_checkpoint(checkpoint_height)
            
            getNetworkCheckpointDataThread(checkpoint_height)
        time.sleep(30)

class getPastCheckpoints(threading.Thread):
    def __init__(self,):
        threading.Thread.__init__(self)
    
    def run(self):
        print("| Start getPastCheckpoints |")
        list_of_checkpoints = get_list_past_checkpoints()
        while list_of_checkpoints.__len__() > 0:
            checkpoint =  list_of_checkpoints.pop()
            tcheckpointpast = getNetworkCheckpointDataThread(checkpoint)
            tcheckpointpast.start()
            time.sleep(4)
            



netthread = collectNetworkInfoDataThread(previous_checkpoint,previous_block)
invalid_checkpoit_thread= checkInvalidCheckpoints(invalid_checkpoint_list)
#t_get_past_checkpoint = getPastCheckpoints()

netthread.start()
invalid_checkpoit_thread.start()
#t_get_past_checkpoint.start()
