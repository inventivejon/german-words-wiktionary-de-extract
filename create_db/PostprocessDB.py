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

def createdFinalAdjDeclination(Typ, lemma, declinationDecision, numerusDecision, genusDecision, casesDecision):
    numDeclinationDecision = 0
    numNumerusDecision = 0
    numGenusDecision = 0
    numCasesDecision = 0

    lemma = lemma.lower()

    if Typ == 'superlativ':
        lemma = lemma[:-2] # Remove last two characters from lemma
    else:
        ## Prepare lemma for special cases
        if lemma == 'hoch':
            lemma = 'hoh' # hoch -> hoh
        elif lemma.endswith('el'):
            lemma = lemma[:-2] # Remove last two characters from lemma
            lemma = lemma + 'l' # Add h in the end: Example dunkel -> dunkl
        elif lemma.endswith('er'):
            lemma = lemma[:-2] # Remove last two characters from lemma
            lemma = lemma + 'e' # Add h in the end: Example teuer -> teur
        elif lemma.endswith('en'):
            lemma = lemma + 'd' # Add d in the end because this is very likely a verb: zäunen -> zäunend
        elif lemma.endswith('e'):
            lemma = lemma[:-1] # Remove last two characters from lemma
            # Simply should never end with e

    if declinationDecision == 'Starke_Deklination':
        numDeclinationDecision = 0
    else:
        numDeclinationDecision = 1
    
    if numerusDecision == 'Singular':
        numNumerusDecision = 0
    else:
        numNumerusDecision = 1

    if genusDecision == 'Maskulinum':
        numGenusDecision = 0
    elif genusDecision == 'Femininum':
        numGenusDecision = 1
    else: # Neutrum
        numGenusDecision = 2

    if casesDecision == 'Nominativ':
        numCasesDecision = 0
    elif casesDecision == 'Genitiv':
        numCasesDecision = 1
    elif casesDecision == 'Dativ':
        numCasesDecision = 2
    else: # Akkusativ
        numCasesDecision = 3

    # Starke_Deklination
    if numDeclinationDecision == 0:
        if numNumerusDecision == 0: # Singular
            if numGenusDecision == 0: # Maskulinum
                if numCasesDecision == 0: # Nominativ
                    return lemma + "er"
                elif numCasesDecision == 1: # Genitiv
                    return lemma + "en"
                elif numCasesDecision == 2: # Dativ
                    return lemma + "em"
                else: # Akkusativ
                    return lemma + "en"
            elif numGenusDecision == 1: # Femininum
                if numCasesDecision == 0: # Nominativ
                    return lemma + "e"
                elif numCasesDecision == 1: # Genitiv
                    return lemma + "er"
                elif numCasesDecision == 2: # Dativ
                    return lemma + "er"
                else: # Akkusativ
                    return lemma + "e"
            else: # Neutrum
                if numCasesDecision == 0: # Nominativ
                    return lemma + "es"
                elif numCasesDecision == 1: # Genitiv
                    return lemma + "en"
                elif numCasesDecision == 2: # Dativ
                    return lemma + "em"
                else: # Akkusativ
                    return lemma + "es"
        else: # Plural
            if numCasesDecision == 0: # Nominativ
                return lemma + "e"
            elif numCasesDecision == 1: # Genitiv
                return lemma + "er"
            elif numCasesDecision == 2: # Dativ
                return lemma + "en"
            else: # Akkusativ
                return lemma + "e"
    else: # Schwache Deklination
        if numNumerusDecision == 0: # Singular
            if numGenusDecision == 0: # Maskulinum
                if numCasesDecision == 0: # Nominativ
                    return lemma + "e"
                elif numCasesDecision == 1: # Genitiv
                    return lemma + "en"
                elif numCasesDecision == 2: # Dativ
                    return lemma + "en"
                else: # Akkusativ
                    return lemma + "en"
            elif numGenusDecision == 1: # Femininum
                if numCasesDecision == 0: # Nominativ
                    return lemma + "e"
                elif numCasesDecision == 1: # Genitiv
                    return lemma + "en"
                elif numCasesDecision == 2: # Dativ
                    return lemma + "en"
                else: # Akkusativ
                    return lemma + "e"
            else: # Neutrum
                if numCasesDecision == 0: # Nominativ
                    return lemma + "e"
                elif numCasesDecision == 1: # Genitiv
                    return lemma + "en"
                elif numCasesDecision == 2: # Dativ
                    return lemma + "en"
                else: # Akkusativ
                    return lemma + "e"
        else: # Plural
            if numCasesDecision == 0: # Nominativ
                return lemma + "en"
            elif numCasesDecision == 1: # Genitiv
                return lemma + "en"
            elif numCasesDecision == 2: # Dativ
                return lemma + "en"
            else: # Akkusativ
                return lemma + "en"

def process_Adj_declinations(db, handle):
    numCheckedAdj = 0
    numExistingAdjEntries = 0
    numUpdatedAdjEntries = 0
    numInsertedAdjEntries = 0

    # Combination of Declination
    # Starke_Deklination/Schwache_Deklination Singular/Plural Maskulinum/Femininum/Neutrum/ Nominativ/Genitiv/Dativ/Akkusativ

    # Search for all db entries that contains an adjektiv in the database
    db_result = db.execute('''SELECT *
                        FROM Adjektiv
                        WHERE Typ='lemma' ''').fetchall()
    db_result = db_result + db.execute('''SELECT *
                        FROM Adjektiv
                        WHERE Typ='positiv' ''').fetchall()
    db_result = db_result + db.execute('''SELECT *
                        FROM Adjektiv
                        WHERE Typ='komparativ' ''').fetchall()
    db_result = db_result + db.execute('''SELECT *
                        FROM Adjektiv
                        WHERE Typ='superlativ' ''').fetchall()

    totalResults = len(db_result)
    
    for singleResult in db_result:
        numCheckedAdj = numCheckedAdj + 1
       
        log(handle, "Anzahl geprüfter Adjektive: {}".format(numCheckedAdj))
        log(handle, "Anzahl existierender Adjektiveinträge: {}".format(numExistingAdjEntries))
        log(handle, "Anzahl aktualisierter Adjektiveinträge: {}".format(numUpdatedAdjEntries))
        log(handle, "Anzahl hinzugefügter Adjektiveinträge: {}".format(numInsertedAdjEntries))
        log(handle, "{}/{}: Using entry {} from type {} to interprete {} as {}".format(numCheckedAdj, totalResults, singleResult[1], singleResult[2], singleResult[3], singleResult[3]))

        declinationOption = [
            'Starke_Deklination',
            'Schwache_Deklination'
        ]

        numerusOptions = [
            'Singular',
            'Plural'
        ]

        genusOptions = [
            'Maskulinum',
            'Femininum',
            'Neutrum'
        ]

        casesOptions = [
            'Nominativ',
            'Genitiv',
            'Dativ',
            'Akkusativ'
        ]

        for singleDeclination in declinationOption:
            for singleNumerus in numerusOptions:
                for singleGenus in genusOptions:
                    for singleCase in casesOptions:
                        finalDeclination = ''
                        finalDeclination = createdFinalAdjDeclination(singleResult[2],singleResult[1], singleDeclination, singleNumerus, singleGenus, singleCase )
                        newTyp = " ".join([singleResult[2], singleDeclination, singleNumerus, singleGenus, singleCase])
                        db_result_sub = db.execute(''' SELECT *
                                                       FROM Adjektiv
                                                       WHERE lemma = ? AND Typ=? ''', [singleResult[1], newTyp]).fetchall()
                        log(handle, ''' SELECT * FROM Adjektiv WHERE lemma='{}' AND Typ='{}' '''.format(singleResult[1], newTyp))

                        if db_result_sub is not None and len(db_result_sub)>0:
                            db_result_sub_check = db.execute(''' SELECT *
                                                       FROM Adjektiv
                                                       WHERE lemma = ? AND Typ = ? AND Wortform = ? ''', [singleResult[1], newTyp, finalDeclination]).fetchall()
                            if db_result_sub_check is not None and len(db_result_sub_check)>0:
                                numExistingAdjEntries = numExistingAdjEntries + 1
                            else:
                                numUpdatedAdjEntries = numUpdatedAdjEntries + 1
                                db.execute('''UPDATE Adjektiv
                                            SET Typ = ?, Wortform = ?
                                            WHERE id = ?''', [newTyp, finalDeclination, db_result_sub[0]])
                                log(handle, '''UPDATE Adjektiv SET Wortform = '{}' WHERE id = '{}' '''.format(finalDeclination, db_result_sub[0]))
                        else:
                            numInsertedAdjEntries = numInsertedAdjEntries + 1
                            db.execute("INSERT INTO Adjektiv VALUES(NULL,?,?,?)", [singleResult[1], newTyp, finalDeclination])
                            log(handle, "INSERT INTO Adjektiv VALUES(NULL,{},{},{})".format(singleResult[1], newTyp, finalDeclination))
                            
    log(handle, "Anzahl geprüfter Adjektive: {}".format(numCheckedAdj))
    log(handle, "Anzahl existierender Adjektiveinträge: {}".format(numExistingAdjEntries))
    log(handle, "Anzahl aktualisierter Adjektiveinträge: {}".format(numUpdatedAdjEntries))
    log(handle, "Anzahl hinzugefügter Adjektiveinträge: {}".format(numInsertedAdjEntries))

def performAllPostprocessingDBOperations(handle, db_path):
        
    db = sqlite3.connect(db_path)

    # Process Substantiv Genus
    # process_Subst_genus(db, handle)

    # Process Adjektiv declinations
    process_Adj_declinations(db, handle)

    db.commit()

    db.close()