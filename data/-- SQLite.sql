-- SQLite

/* INSERT INTO deliberation (candidat_id, total_points, statut) 
VALUES ((SELECT id FROM candidats WHERE num_table = 100), 150, 'Recalé')
ON CONFLICT(candidat_id) DO UPDATE SET total_points = 150, statut = 'Recalé'; */
/* INSERT INTO livret_scolaire (candidat_id, nombre_de_fois, moyenne_6e, moyenne_5e, moyenne_4e, moyenne_3e, moyenne_cycle)
VALUES ((SELECT id FROM candidats WHERE num_table = 100), 1, 12.0, 11.5, 13.0, 12.5, 12.25);
 */

SELECT * FROM candidats WHERE num_table = 100;
SELECT * FROM notes WHERE candidat_id = (SELECT id FROM candidats WHERE num_table = 100);
SELECT  * FROM notes;
SELECT  * FROM deliberation;

SELECT candidat_id, nombre_de_fois, moyenne_cycle FROM livret_scolaire;


-- saufe ces deux requetes qui non rien donné 
SELECT * FROM livret_scolaire WHERE candidat_id = (SELECT id FROM candidats WHERE num_table = 100);
SELECT * FROM livret_scolaire;

SELECT id FROM candidats WHERE num_table = 100;

SELECT * FROM livret_scolaire WHERE candidat_id = (SELECT id FROM candidats WHERE num_table = 101);
SELECT * FROM notes WHERE candidat_id = (SELECT id FROM candidats WHERE num_table = 151);
SELECT * FROM deliberation WHERE candidat_id = (SELECT id FROM candidats WHERE num_table = 53);

--:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
SELECT COUNT(*) FROM candidats WHERE sexe = 'M';
SELECT COUNT(*) FROM notes;
SELECT COUNT(*) FROM livret_scolaire;
SELECT * FROM candidats;

SELECT candidat_id,prenom, nom, num_table, total_points, statut FROM candidats c JOIN deliberation d ON c.id = d.candidat_id WHERE d.total_points >= 171;
SELECT * FROM deliberation ;


SELECT * FROM candidats WHERE num_table = 100;
SELECT * FROM notes WHERE candidat_id = (SELECT id FROM candidats WHERE num_table = 100);
SELECT * FROM livret_scolaire WHERE candidat_id = (SELECT id FROM candidats WHERE num_table = 100);
SELECT * FROM deliberation WHERE candidat_id = (SELECT id FROM candidats WHERE num_table = 100);

SELECT * FROM jury;
ALTER TABLE jury ADD COLUMN num_jury VARCHAR(50) UNIQUE;
INSERT INTO jury (localite) VALUES ('DAKAR');
PRAGMA journal_mode=WAL;
PRAGMA table_info(candidats);
INSERT INTO jury (num_jury, ia_region, ief_departement, localite, centre_examen, president_jury, telephone, email, cle_acces) 
VALUES ("JURY001", "IA DAKAR", "IEF Dakar Plateau", "Dakar", "Lycée Blaise Diagne", "Mamadou Diop", "+221 77 123 45 67", "jury.dakar@example.com", "JURYDKR2024");
.tables