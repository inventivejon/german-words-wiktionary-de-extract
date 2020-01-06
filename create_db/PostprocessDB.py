from operator import itemgetter
import os
import locale
import csv
locale.setlocale(locale.LC_ALL, 'deu_deu' if os.name == 'nt' else 'de_DE.UTF-8')
import sqlite3
import sys

def log(handle, content):
    try:
        handle.write(content.encode(sys.stdout.encoding, errors='replace').decode("utf-8") + '\n')
    except:
        pass
    print(content)

# Postprocess Operation 1: Replace all genus, genus 1, genus 2, genus 3, genus 4, entries in Database with extending all other entries for the same lemma with m, f, n
# Detailled operation steps:
# 

def process_Subst_genus(db, handle):
    numCheckedGenus = 0
    numUpdatedSubstantivEntries = 0

    # Search for all db entries that contains genus or genus 1 or ... in the database
    db_result = db.execute('''SELECT *
                        FROM Substantiv
                        WHERE Typ LIKE 'genus' ''').fetchall()
    
    for singleResult in db_result:
        numCheckedGenus = numCheckedGenus + 1
        interpretedGenus = ''

        if singleResult[3] == 'm':
            interpretedGenus = 'Maskulin'
        elif singleResult[3] == 'f':
            interpretedGenus = 'Feminim'
        elif singleResult[3] == 'n':
            interpretedGenus = 'Neutrum'

        log(handle, "Using entry {} from type {} to interprete {} as {}".format(singleResult[1], singleResult[2], singleResult[3], singleResult[3]))

        db_result_sub = db.execute('''SELECT *
                        FROM Substantiv
                        WHERE lemma = ? AND Typ NOT LIKE '{}' '''.format(interpretedGenus), [singleResult[1]]).fetchall()

        for singleSubResult in db_result_sub:
            numUpdatedSubstantivEntries = numUpdatedSubstantivEntries + 1
            db.execute('''UPDATE Substantiv
                          SET Typ = ?
                          WHERE id = ?''', [singleSubResult[2] + " " + interpretedGenus, singleSubResult[0]])
            log(handle, "UPDATE Substantiv SET Typ = {} WHERE id = {}".format(singleSubResult[2] + " " + interpretedGenus, singleSubResult[0]))

    log(handle, "Anzahl geprüfter Genus: {}".format(numCheckedGenus))
    log(handle, "Anzahl geänderter Substantiveinträge: {}".format(numUpdatedSubstantivEntries))

def performAllPostprocessingDBOperations(handle, db_path):
        
    db = sqlite3.connect(db_path)

    # create_db_entries(db, handle, data)

    # Process Substantiv Genus
    process_Subst_genus(db, handle)

    db.commit()

    db.close()