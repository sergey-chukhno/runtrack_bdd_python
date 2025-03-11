import mysql.connector 
import os
from dotenv import load_dotenv

load_dotenv()

class Zoo:
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
        return
    
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

  def modify_animal(self, id, nom=None, race=None, cage_id=None, date_de_naissance=None, pays_origine=None): 
    try: 
      updates=[]
      values=[]

      if nom: 
        updates.append("nom=%s")
        values.append(nom)
      if race: 
        updates.append("race=%s")
        values.append(race)

      if cage_id is not None: 
        self.cursor.execute("SELECT capacite FROM cage where id=%s", (cage_id,))
        cage_info = self.cursor.fetchone()

        if cage_info: 
          capacite_max = cage_info[0]
          self.cursor.execute("SELECT COUNT(*) FROM animal WHERE cage_id=%s", (cage_id,))
          num_animals = self.cursor.fetchone()[0]

          if num_animals >= capacite_max: 
            print(f"La cage {cage_id} est pleine")
            return
        
        updates.append("cage_id=%s")
        values.append(cage_id)
      
      if date_de_naissance: 
        updates.append("date_de_naissance=%s")
        values.append(date_de_naissance)
      
      if pays_origine: 
        updates.append("pays_origine=%s")
        values.append(pays_origine)
      
      if updates: 
        query=f"UPDATE ANIMAL SET {', '.join(updates)} WHERE id=%s"
        values.append(id)
        self.cursor.execute(query, values)
        self.conn.commit()
        print(f"Animal {id} a été modifé avec succes")
      else: 
        print("Aucune modification à apporter")
    except mysql.connector.Error as error:
      print(f"Erreur lors de la modification d'un animal: {error}")
    

  def modify_cage(self, id, superficie=None, capacite=None): 
    try: 
      updates =[]
      values = []

      if superficie is not None: 
        updates.append("superficie=%s")
        values.append(superficie)
      if capacite is not None: 
        updates.append("capacite=%s")
        values.append(capacite)
      
      if updates: 
        query = f"UPDATE cage SET {', '.join(updates)} WHERE id=%s;"
        values.append(id)
        self.cursor.execute(query, values)
        self.conn.commit()
        print(f"Cage {id} a été modifé avec succes")
      else: 
        print("Aucune modification à apporter")
    except mysql.connector.Error as error:
      print(f"Erreur lors de la modification d'une cage: {error}")


  def delete_animal(self, id): 
    try: 
      self.cursor.execute("SELECT * FROM animal WHERE id=%s", (id,))

      if self.cursor.fetchone(): 
        self.cursor.execute("DELETE FROM animal WHERE id=%s", (id,))
        self.conn.commit()
        print(f"L'animal {id} a été supprimé")
      else:
        print(f"L'animal {id} n'existe pas")
    
    except mysql.connector.Error as error:
      print(f"Erreur lors de la suppression d'un animal: {error}")


  def delete_cage(self, id): 
    try: 
      self.cursor.execute("SELECT * FROM cage WHERE id=%s", (id,))

      if self.cursor.fetchone(): 
        self.cursor.execute("DELETE FROM cage WHERE id=%s", (id,))
        self.conn.commit()
        print(f"La cage {id} a été supprimé")
      else:
        print(f"La cage {id} n'existe pas")
    
    except mysql.connector.Error as error:
      print(f"Erreur lors de la suppression d'une cage: {error}")


  def calculate_total_surface(self): 
    try: 

      self.cursor.execute("SELECT SUM(superficie) FROM cage")
      total_superficie = self.cursor.fetchone()[0]
      print(f"La superficie totale des cages est {total_superficie} m2")
    
    except mysql.connector.Error as error:
      print(f"Erreur lors du calcul de la superficie totale des cages: {error}")

if __name__ == "__main__": 
  zoo = Zoo(
    host=os.getenv("DB_HOST"), 
    user=os.getenv("DB_USER"), 
    password=os.getenv("DB_PASSWORD"),
    database="zoo"
  )

  #zoo.add_animal("Baboon", "Old World Monkey", 3, "2002-11-10", "Tanzania")
  #zoo.show_animals()
  #zoo.show_animals_by_cage()
  #zoo.modify_animal(id=9, pays_origine="Kenya")
  #zoo.show_animals()
  #zoo.delete_animal(id=9)
  #zoo.show_animals()
  #zoo.calculate_total_surface()
  
    

