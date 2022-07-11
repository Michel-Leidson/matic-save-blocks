
import sqlite3



def has_chekckpoint_in_db(checkpoint):
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


print(has_chekckpoint_in_db(33598))
print(has_chekckpoint_in_db(5657))