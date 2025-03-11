import mysql.connector 
import os
from dotenv import load_dotenv

load_dotenv()

try: 

  conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"), 
    user=os.getenv("DB_USER"), 
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
  )

  cursor = conn.cursor()
  cursor.execute("SELECT * FROM etudiant")
  result = cursor.fetchall()

  for row in result: 
    print(row)

except mysql.connect.Error as error: 
  print(f'Error occurred: {error}')

finally: 
  cursor.close()
  conn.close()