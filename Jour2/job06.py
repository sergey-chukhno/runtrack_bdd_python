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
  cursor.execute("SELECT SUM(capacite) FROM salle")
  result = cursor.fetchone()

  capacite_totale = int(result[0]) if result[0] is not None else 0

  print(f'La superficie de la Plateforme est {capacite_totale} m2')

except mysql.connect.Error as error: 
  print(f'Error occurred: {error}')

finally: 
  cursor.close()
  conn.close()