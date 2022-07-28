import csv
import sqlite3
import requests
  
  
try:
    r = requests.get('https://heimdall.api.matic.network/checkpoints/count')
    print(r.json())
    # Import csv and extract data
    with open('dummy_blocks.csv', 'r') as fin:
        dr = csv.DictReader(fin)
        block_info = [(i['network'], i['block'], i['signed_in'], i['signed']) for i in dr]
        print(block_info)
  
    # Connect to SQLite
    sqliteConnection = sqlite3.connect('database.db')
    cursor = sqliteConnection.cursor()
  
    # Create student table
    #cursor.execute('create table student(name varchar2(10), age int);')
  
    # Insert data into table
    cursor.executemany(
        "insert into blocks (network, block, signed_in, signed) VALUES (?, ?, ?, ?);", block_info)
  
    # Show student table
    #cursor.execute('select * from student;')
  
    # View result
    result = cursor.fetchall()
    print(result)
  
    # Commit work and close connection
    sqliteConnection.commit()
    cursor.connection.commit()
    cursor.close()
  
except sqlite3.Error as error:
    print('Error occured - ', error)
  
finally:
    if sqliteConnection:
        sqliteConnection.close()
        print('SQLite Connection closed')