mysql> DELETE FROM etudiant
    -> WHERE nom = "Doe" AND prenom = "John";
Query OK, 1 row affected (0.06 sec)

mysql> SELECT * FROM etudiant;
+----+-----------+----------+-----+---------------------------------+
| id | nom       | prenom   | age | email                           |
+----+-----------+----------+-----+---------------------------------+
|  1 | Spaghetti | Betty    |  20 | betty.spaghetti@laplateforme.io |
|  2 | Steak     | Chuck    |  45 | chuck.steak@laplateforme.io     |
|  4 | Barnes    | Binkie   |  16 | binkie.barnes@laplateforme.io   |
|  5 | Dupuis    | Gertrude |  20 | gertrude.dupuis@laplateforme.io |
|  6 | Dupuis    | Martin   |  18 | martin.dupuis@gmail.com         |
+----+-----------+----------+-----+---------------------------------+
5 rows in set (0.01 sec)

mysql> tee /Users/anatoliychubais/Desktop/bdd-sql-python/Jour1/job19.sql
