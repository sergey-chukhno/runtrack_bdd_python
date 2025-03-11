mysql> use LaPlateforme;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> CREATE TABLE etage (
    -> id INT AUTO_INCREMENT PRIMARY KEY,
    -> nom VARCHAR(255) NOT NULL,
    -> numero INT NOT NULL,
    -> superficie INT NOT NULL);
Query OK, 0 rows affected (0.16 sec)

mysql> CREATE TABLE salle (
    -> id INT AUTO_INCREMENT PRIMARY KEY, 
    -> nom VARCHAR(255) NOT NULL, 
    -> id_etage INT NOT NULL, 
    -> capactie INT NOT NULL);
Query OK, 0 rows affected (0.02 sec)

mysql> desc etage;
+------------+--------------+------+-----+---------+----------------+
| Field      | Type         | Null | Key | Default | Extra          |
+------------+--------------+------+-----+---------+----------------+
| id         | int          | NO   | PRI | NULL    | auto_increment |
| nom        | varchar(255) | YES  |     | NULL    |                |
| numero     | int          | YES  |     | NULL    |                |
| superficie | int          | NO   |     | NULL    |                |
+------------+--------------+------+-----+---------+----------------+
4 rows in set (0.04 sec)

mysql> desc salle;
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int          | NO   | PRI | NULL    | auto_increment |
| nom      | varchar(255) | NO   |     | NULL    |                |
| id_etage | int          | NO   |     | NULL    |                |
| capactie | int          | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
4 rows in set (0.01 sec)

mysql> INSERT INTO etage VALUES
    -> ('RDC', 0, 500),
    -> ('R+1', 1, 500);
ERROR 1136 (21S01): Column count doesn't match value count at row 1
mysql> INSERT INTO etage (nom, numero, superficie)
    -> VALUES 
    -> ("RDC", 0, 500),
    -> ("R+1", 1, 500);
Query OK, 2 rows affected (0.01 sec)
Records: 2  Duplicates: 0  Warnings: 0

mysql> desc etage;
+------------+--------------+------+-----+---------+----------------+
| Field      | Type         | Null | Key | Default | Extra          |
+------------+--------------+------+-----+---------+----------------+
| id         | int          | NO   | PRI | NULL    | auto_increment |
| nom        | varchar(255) | YES  |     | NULL    |                |
| numero     | int          | YES  |     | NULL    |                |
| superficie | int          | NO   |     | NULL    |                |
+------------+--------------+------+-----+---------+----------------+
4 rows in set (0.02 sec)

mysql> INSERT INTO salle (nom, id_etage, capacite)
    -> VALUES 
    -> ('Lounge', 1, 100),
    -> ('Studio Son', 1, 5), 
    -> ('Broadcasting', 2, 50),
    -> ('Bocal Peda', 2, 4), 
    -> ('Coworking', 2, 80), 
    -> ('Studio Video', 2, 5);
ERROR 1054 (42S22): Unknown column 'capacite' in 'field list'
mysql> UPDATE salle 
    -> SET capactie='capacite';
Query OK, 0 rows affected (0.00 sec)
Rows matched: 0  Changed: 0  Warnings: 0

mysql> INSERT INTO salle (nom, id_etage, capacite) VALUES  ('Lounge', 1, 100), ('Studio Son', 1, 5),  ('Broadcasting', 2, 50), ('Bocal Peda', 2, 4),  ('Coworking', 2, 80),  ('Studio Video', 2, 5);
ERROR 1054 (42S22): Unknown column 'capacite' in 'field list'
mysql> desc salle;
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int          | NO   | PRI | NULL    | auto_increment |
| nom      | varchar(255) | NO   |     | NULL    |                |
| id_etage | int          | NO   |     | NULL    |                |
| capactie | int          | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
4 rows in set (0.01 sec)

mysql> ALTER TABLE salle 
    -> RENAME COLUMN capactie capacite;
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'capacite' at line 2
mysql> ALTER TABLE salle  RENAME COLUMN capactie capacite INT NOT NULL;
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'capacite INT NOT NULL' at line 1
mysql> ALTER TABLE salle  RENAME COLUMN capactie TO capacite;
Query OK, 0 rows affected (0.07 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> desc salle;
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int          | NO   | PRI | NULL    | auto_increment |
| nom      | varchar(255) | NO   |     | NULL    |                |
| id_etage | int          | NO   |     | NULL    |                |
| capacite | int          | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
4 rows in set (0.01 sec)

mysql> INSERT INTO salle (nom, id_etage, capacite) VALUES  ('Lounge', 1, 100), ('Studio Son', 1, 5),  ('Broadcasting', 2, 50), ('Bocal Peda', 2, 4),  ('Coworking', 2, 80),  ('Studio Video', 2, 5);
Query OK, 6 rows affected (0.00 sec)
Records: 6  Duplicates: 0  Warnings: 0

mysql> exit
