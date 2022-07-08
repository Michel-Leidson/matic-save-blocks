import csv
import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

query = '''
    SELECT v.name,b."Date block",b."Blocks number","[" || "'" || v.name || "'," || b."Blocks number" || "]" as "validator-block"
    FROM
    (SELECT signer,DATE(blocks.signed_in) as "Date block",COUNT(blocks.block) as "Blocks number" FROM blocks GROUP BY "Date block") b
    LEFT JOIN
    validators v
    ON
    v.signer=b.signer
    ORDER BY name,b."Date block";
    '''

rows = cursor.execute(query).fetchall()
# open the file in the write mode
f = open('./result_blocks.csv', 'w',encoding='UTF-8')

# create the csv writer
writer = csv.writer(f,delimiter=";")
headers = ['Validator','Date','Blocks','validator-blocks']
writer.writerow(headers)
# write a row to the csv file
for row in rows:
    writer.writerow(row)

# close the file
f.close()