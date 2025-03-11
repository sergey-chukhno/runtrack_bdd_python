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

