mysql> UPDATE etudiant
    -> SET age = 20
    -> WHERE nom = "Spaghetti" AND prenom = "Betty";
Query OK, 1 row affected (0.04 sec)
Rows matched: 1  Changed: 1  Warnings: 0

mysql> SELECT * FROM etudiant WHERE nom = "Spaghetti" AND prenom = "Betty"; 
+----+-----------+--------+-----+---------------------------------+
| id | nom       | prenom | age | email                           |
+----+-----------+--------+-----+---------------------------------+
|  1 | Spaghetti | Betty  |  20 | betty.spaghetti@laplateforme.io |
+----+-----------+--------+-----+---------------------------------+
1 row in set (0.01 sec)

mysql> notee;
