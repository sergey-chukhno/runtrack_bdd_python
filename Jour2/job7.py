import mysql.connector 
import os
from dotenv import load_dotenv

load_dotenv()

try: 

  conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"), 
    user=os.getenv("DB_USER"), 
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME1")
  )

  cursor = conn.cursor()
  cursor.execute("SELECT nom, prenom FROM employe WHERE salaire > 3000")
  result = cursor.fetchall()

  print('Les noms et prénoms des employés dont le salaire est supérieur à 3000 euros:')

  for row in result: 
    nom, prenom = row
    print(f"{prenom} {nom}")
  
  cursor.execute('SELECT employe.nom, employe.prenom, service.nom AS service_name FROM employe JOIN service ON employe.id_service=service.id;')
  employees = cursor.fetchall()
  print('La liste des employes et leurs services:')
  for row in employees:
    nom, prenom, service_name = row
    print(f"{prenom} {nom} travaille dans le service {service_name}")

except mysql.connect.Error as error: 
  print(f'Error occurred: {error}')

finally: 
  cursor.close()
  conn.close()