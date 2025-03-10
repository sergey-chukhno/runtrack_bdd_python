id	nom	prenom	age	email
4	Barnes	Binkie	16	binkie.barnes@laplateforme.io
mysql> SELECT * FROM etudiant WHERE nom LIKE "B%";
ERROR 1046 (3D000): No database selected
mysql> use LaPlateforme;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> tee /Users/anatoliychubais/Desktop/bdd-sql-python/Jour1/job16.sql
mysql> SELECT * FROM etudiant WHERE nom LIKE "B%";
+----+--------+--------+-----+-------------------------------+
| id | nom    | prenom | age | email                         |
+----+--------+--------+-----+-------------------------------+
|  4 | Barnes | Binkie |  16 | binkie.barnes@laplateforme.io |
+----+--------+--------+-----+-------------------------------+
1 row in set (0.00 sec)

mysql> notee;
