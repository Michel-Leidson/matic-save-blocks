import csv
import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

query = '''
    SELECT v.name,c."Date checkpoint",c."Checkpoints number","[" || "'" || v.name || "'," || c."checkpoints number" || "]" as "validator-checkpoint"
    FROM
    (SELECT signer,DATE(checkpoints.signed_in) as "Date checkpoint",COUNT(checkpoints.checkpoint) as "Checkpoints number" FROM checkpoints GROUP BY signer,"Date checkpoint") c
    LEFT JOIN
    validators v
    ON
    v.signer=c.signer
    ORDER BY name,c."Date Checkpoint" DESC;
    '''

rows = cursor.execute(query).fetchall()
# open the file in the write mode
f = open('./result_checkpoints.csv', 'w',encoding='UTF-8')

# create the csv writer
writer = csv.writer(f,delimiter=";")
headers = ['Validator','Date','Checkpoints','validator-checkpoints']
writer.writerow(headers)
# write a row to the csv file
for row in rows:
    writer.writerow(row)

# close the file
f.close()