from datetime import datetime
from fpdf import FPDF
import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

query = '''
    SELECT v.name as "Validator",c."Date Signed", c."Checkpoints Count" FROM 
    (SELECT signer,STRFTIME('%Y-%m-%d',signed_in) as "Date Signed",signed_in,COUNT(checkpoint) as "Checkpoints Count" 
    FROM checkpoints 
    GROUP BY signer,"Date Signed" ) as c,
    validators as v
    WHERE v.signer = c.signer
    ORDER BY v.name,c.signed_in DESC;
    '''

rows = cursor.execute(query).fetchall()

pdf = FPDF()
pdf.add_page()
pdf.image('logo.png',10,10,10)
pdf.set_font('Arial', 'B', 14)
pdf.cell(15, 8, '')
pdf.cell(65, 8, 'Missed Checkpoints Report',0,1,"L",0,"")
pdf.set_font('Arial', '', 8)
pdf.cell(15, 4, '')
pdf.cell(70, 4, 'Generated in: '+datetime.now().strftime("%Y-%m-%d %H:%M:%S") ,0,1,"L",0,"")

pdf.set_font('Arial', 'B', 11)
pdf.ln(10)
pdf.cell(80, 7, 'Validator',1)
pdf.cell(40, 7, 'Date',1)
pdf.cell(40, 7, 'Checkpoints ',1,1)

pdf.set_font('Arial', '', 8)

for row in rows:
    print(row[0],row[1],row[2])
    pdf.cell(80,7,str(row[0]),1)
    pdf.cell(40,7,str(row[1]),1)
    pdf.cell(40,7,str(row[2]),1,1,'C',0,'C')


pdf.output('report'+str(datetime.now())+'.pdf', 'F')