import sqlite3


def check_invalid_checkpoints():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
   
    consult_invalid_checkpoints = '''
    SELECT checkpoint,COUNT(signer) FROM checkpoints GROUP BY checkpoint
    '''
    cursor.execute(consult_invalid_checkpoints)
    invalid_checkpoints_list = cursor.fetchall()
    for checkpoint in invalid_checkpoints_list:
        number_of_validators_not_siged = checkpoint[1]
        checkpoint_height=checkpoint[0]
        if number_of_validators_not_siged > 50 :
            print("The checkpoint",checkpoint_height,"is invalid!")

    connection.close()
    return invalid_checkpoints_list

check_invalid_checkpoints()