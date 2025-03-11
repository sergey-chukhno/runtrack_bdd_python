import mysql.connector 
import os
from dotenv import load_dotenv

load_dotenv()

class ZooManager:
  def __init__(self, host, user, password, database):
    self.conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"), 
    user=os.getenv("DB_USER"), 
    password=os.getenv("DB_PASSWORD"),
    database="zoo"
  )
    self.cursor = self.conn.cursor()

  def add_cage(self, superficie, capacite): 
    try:
      query = "INSERT INTO cage (superficie, capacite) VALUES (%s, %s);"
      self.cursor.execute(query, (superficie, capacite))
      self.conn.commit()
      print(f"La cage a été ajoutée avec succes")
    except mysql.connector.Error as error:
      print(f"Erreur lors de l'ajout de la cage: {error}")
  
  def add_animal(self, nom, race, cage_id, date_de_naissance, pays_origine): 
    try: 
      self.cursor.execute("SELECT capacite FROM cage WHERE id=%s", (cage_id,))
      cage_info = self.cursor.fetchone()

      if cage_info:
        capacite_max = cage_info[0]
        self.cursor.execute('SELECT COUNT(*) FROM animal WHERE cage_id=%s', (cage_id,))
        num_animals = self.cursor.fetchone()[0]

        if num_animals >= capacite_max: 
          print(f"Erreur: La cage {cage_id} est pleine")
          return
        
        query = "INSERT INTO animal (nom, race, cage_id, date_de_naissance, pays_origine) VALUES (%s, %s, %s, %s, %s);"
        self.cursor.execute(query, (nom, race, cage_id, date_de_naissance, pays_origine))
        self.conn.commit()
        print(f"L'animal {nom} a été ajouté avec succès")
      else: 
        print(f"La cage {cage_id} n'existe pas")
    
    except mysql.connector.Error as error:
      print(f"Erreur lors de l'ajout de l'animal: {error}") 
  
  def show_animals(self): 
    try: 
      self.cursor.execute("SELECT * from animal;")
      animals = self.cursor.fetchall()
      if animals:
        for animal in animals: 
          print(f"ID: {animal[0]} | nom: {animal[1]} | race: {animal[2]} | cage: {animal[3]} | date_de_naissance: {animal[4]} | pays_d'origine: {animal[5]}")
      else: 
        print("Aucun animal dans le zoo")
    except mysql.connector.Error as error:
      print(f"Erreur lors de l'affichage des animaux du zoo: {error}")
  
  def show_animals_by_cage(self):
    try: 
      self.cursor.execute("SELECT cage.id, animal.nom FROM cage LEFT JOIN animal ON cage.id = animal.cage_id ORDER BY cage.id;")
      result = self.cursor.fetchall()
      cages = {}
      for cage_id, nom in result:
        if cage_id not in cages: 
          cages[cage_id] = []
        if nom: 
          cages[cage_id].append(nom)

      print('La liste des animaux par cage:')
      for cage_id, animals in cages.items():
        print(f"Cage {cage_id}: {", ".join(animals) if animals else 'vide'}")
    except mysql.connector.Error as error:
      print(f"Erreur lors de l'affichage des animaux par cage: {error}")

  def modif_animal(self, animal_id, nom=None, race=None, cage_id=None, date_de_naissance=None, pays_origine=None): 
    pass 

  def modify_cage(self, id, superficie, capacite): 
    pass

  def delete_animal(self, animal_id): 
    pass

  def delete_cage(self, id): 
    pass

  def calculate_total_surface(self): 
    pass
