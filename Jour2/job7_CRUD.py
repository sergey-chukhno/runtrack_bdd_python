import mysql.connector 
import os
from dotenv import load_dotenv

load_dotenv()

class Employe:
  def __init__(self, host, user, password, database):
    self.conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"), 
    user=os.getenv("DB_USER"), 
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME1")
  )
    self.cursor = self.conn.cursor()
  
  def create_employe(self, nom, prenom, salaire, id_service): 
    try: 
      query = "INSERT INTO employe (nom, prenom, salaire, id_service) VALUES (%s, %s, %s, %s);"
      values = (nom, prenom, salaire, id_service)
      self.cursor.execute(query, values)
      self.conn.commit()
      print(f"L'employe {prenom} {nom} a été ajouté à la liste des employés")
    except mysql.connector.Error as error:
      print(f"Erreur est survenue lors de l'ajout de l'employé {prenom} {nom}: {error}")
  
  def fetch__all_employes(self): 
    try: 
      query = "SELECT * FROM employe;"
      self.cursor.execute(query)
      result = self.cursor.fetchall()
      print('Les employés ')
      for row in result: 
        employe_id, nom, prenom, salaire, id_service = row
        print(f'\nemploye_id: {employe_id} | prenom: {prenom} | nom: {nom} | salaire: {salaire} | id_service: {id_service}')
    except mysql.connector.Error as error:
      print(f"Erreur est survenue lors de l'affichage d'une liste des employés: {error}")
  
  def update_employes(self, id, nom=None, prenom=None, salaire=None, id_service=None): 
    try: 
      query_check = "SELECT id FROM employe WHERE id=%s;"
      self.cursor.execute(query_check, (id,))
      result = self.cursor.fetchone()

      if result is None: 
        print(f"Aucun employé avec {id} n'a pas été trouvé")
      else:
        query_update = "UPDATE employe SET "
        values = []

        if nom is not None: 
          query_update += "nom=%s, "
          values.append(nom)
        if prenom is not None: 
          query_update += "prenom=%s, "
          values.append(prenom)
        if salaire is not None: 
          query_update += "salaire=%s, "
          values.append(salaire)
        if id_service is not None: 
          query_update += "id_service=%s, "
          values.append(id_service)
        
        query_update = query_update.rstrip(', ')

        query_update += "WHERE id=%s;"
        values.append(id)

        self.cursor.execute(query_update, tuple(values))
        self.conn.commit()
        print(f"Les données de l'employé {id} ont été mises au jour.\n employe_id: {id} \nnom: {nom}, \nprenom: {prenom} \nsalaire: {salaire} \nid_service: {id_service}")

    except mysql.connector.Error as error:
      print(f"Erreur est survenue lors de la mise à jour des données de l'employé {id} : {error}")
  
  def delete_employee(self, id): 
    try: 
      query_check = "SELECT id FROM employe WHERE id=%s;"
      self.cursor.execute(query_check, (id,))
      result = self.cursor.fetchone()

      if result is None: 
        print(f"Aucun employé avec {id} n'a pas été trouvé")
      else: 
        query_delete = "DELETE FROM employe WHERE id=%s;"
        self.cursor.execute(query_delete, (id,))
        self.conn.commit()
        print(f"Employé {id} a été supprimé avec success")
    except mysql.connector.Error as error:
      print(f"Erreur est survenue lors de la suppression de l'employé {id} : {error}")
  
  def close(self): 
    self.cursor.close()
    self.conn.close()


if __name__ == "__main__": 
  employe = Employe(
     host=os.getenv("DB_HOST"),
      user=os.getenv("DB_USER"),
      password=os.getenv("DB_PASSWORD"),
      database=os.getenv("DB_NAME1")
  )

  #employe.create_employe('Snail', 'Gary', 3217.45, 2)
  #employe.create_employe('Cheeks', 'Sandy', 1800, 2)

  #employe.fetch__all_employes()

  #employe.update_employes(4, prenom="Bob")
  #employe.delete_employee(6)
 

        
  
  

