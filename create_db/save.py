from operator import itemgetter
import os
import locale
import csv
locale.setlocale(locale.LC_ALL, 'deu_deu' if os.name == 'nt' else 'de_DE.UTF-8')
import sqlite3
import sys

# from pdb import set_trace as bp

header = [
    # Nomen
    # 'id',
    'lemma',
    #'pos',
    'genus',
    'genus 1',
    'genus 2',
    'genus 3',
    'genus 4',

    'nominativ singular',
    'nominativ singular*',
    'nominativ singular 1',
    'nominativ singular 2',
    'nominativ singular 3',
    'nominativ singular 4',
    'nominativ singular stark',
    'nominativ singular schwach',
    'nominativ singular gemischt',
    'nominativ plural',
    'nominativ plural*',
    'nominativ plural 1',
    'nominativ plural 2',
    'nominativ plural 3',
    'nominativ plural 4',
    'nominativ plural stark',
    'nominativ plural schwach',
    'nominativ plural gemischt',

    'genitiv singular',
    'genitiv singular*',
    'genitiv singular 1',
    'genitiv singular 2',
    'genitiv singular 3',
    'genitiv singular 4',
    'genitiv singular stark',
    'genitiv singular schwach',
    'genitiv singular gemischt',
    'genitiv plural',
    'genitiv plural*',
    'genitiv plural 1',
    'genitiv plural 2',
    'genitiv plural 3',
    'genitiv plural 4',
    'genitiv plural stark',
    'genitiv plural schwach',
    'genitiv plural gemischt',

    'dativ singular',
    'dativ singular*',
    'dativ singular 1',
    'dativ singular 2',
    'dativ singular 3',
    'dativ singular 4',
    'dativ singular stark',
    'dativ singular schwach',
    'dativ singular gemischt',
    'dativ plural',
    'dativ plural*',
    'dativ plural 1',
    'dativ plural 2',
    'dativ plural 3',
    'dativ plural 4',
    'dativ plural stark',
    'dativ plural schwach',
    'dativ plural gemischt',

    'akkusativ singular',
    'akkusativ singular*',
    'akkusativ singular 1',
    'akkusativ singular 2',
    'akkusativ singular 3',
    'akkusativ singular 4',
    'akkusativ singular stark',
    'akkusativ singular schwach',
    'akkusativ singular gemischt',
    'akkusativ plural',
    'akkusativ plural*',
    'akkusativ plural 1',
    'akkusativ plural 2',
    'akkusativ plural 3',
    'akkusativ plural 4',
    'akkusativ plural stark',
    'akkusativ plural schwach',
    'akkusativ plural gemischt',

    # Verb
    'präsens_ich',
    'präsens_du',
    'präsens_er, sie, es',
    'präteritum_ich',
    'partizip ii',
    'konjunktiv ii_ich',
    'imperativ singular',
    'imperativ plural',
    'hilfsverb',

    # Pronomen

    # Adjektiv
    'positiv',
    'komparativ',
    'superlativ',

    # Partikel

    # Abkürzung

    # Adverb

    # Gebundenes Lexem

    # Wortverbindung

    # Redewendung

    # Adposition

    # Kontraktion

    # Konjunktion

    # Affix

    # Numerale

    # Artikel

    # Sprichwort

    # Geflügeltes Wort
]

numUpdatedEntries = 0
numInsertedEntries = 0

def log(handle, content):
    try:
        handle.write(content.encode(sys.stdout.encoding, errors='replace').decode("utf-8") + '\n')
    except:
        pass
    print(content)

def UpdateOrInsertIntoDBGen(handle, table_postfix, column2name, column3name, db, singleWordType, execute_parameters):
    global numUpdatedEntries
    global numInsertedEntries

    table = '{}{}'.format(singleWordType.replace(' ', '_'), table_postfix)
    log(handle,'SELECT * FROM {} WHERE lemma={} AND {}={} AND {}={}'.format(table, execute_parameters[0], column2name, execute_parameters[1], column3name, execute_parameters[2]))
    db_result = db.execute('SELECT * FROM {} WHERE lemma=? AND {} LIKE ? AND {}=?'.format(table, column2name, column3name), [execute_parameters[0], execute_parameters[1], execute_parameters[2]]).fetchone()
    if db_result is not None and len(db_result)>0:
        log(handle, 'Changing value in table {} for id {} from {} {} {} to {} {} {}'.format(table, db_result[0], db_result[1], db_result[2], db_result[3], execute_parameters[0], execute_parameters[1], execute_parameters[2]))
        numUpdatedEntries = numUpdatedEntries + 1
    elif execute_parameters[2] is not None and execute_parameters[2] != 'None':
        log(handle, "INSERT INTO {} VALUES(NULL,{},{},{})".format(table,execute_parameters[0],execute_parameters[1],execute_parameters[2]))
        db.execute("INSERT INTO {} VALUES(NULL,?,?,?)".format(table),execute_parameters)
        numInsertedEntries = numInsertedEntries + 1

def UpdateOrInsertIntoDB_attr(handle, db, singleWordType, execute_parameters):
    UpdateOrInsertIntoDBGen(handle, "_attr", "Attribute", "Value", db, singleWordType, execute_parameters)

def UpdateOrInsertIntoDB(handle, db, singleWordType, execute_parameters):
    UpdateOrInsertIntoDBGen(handle, "", "Typ", "Wortform", db, singleWordType, execute_parameters)

def create_db_entries(db, handle, data):
    global numUpdatedEntries
    global numInsertedEntries

    numDataEntries = len(data)
    log(handle, "Processing {} data entries".format(numDataEntries))
    # map dict values to list
    index = 0
    for word_data in data:
        log(handle, "{}".format(word_data['flexion'] if hasattr(word_data, 'flexion') else ""))
        index = index + 1
        log(handle, "Processing: {}/{} So far: {} inserted and {} updated".format(index,numDataEntries,numInsertedEntries,numUpdatedEntries))
        
        singleWordType = 'empty'

        for wordType in word_data['pos']:
            if singleWordType == 'empty' and wordType != 'Toponym':
                singleWordType = wordType
                break

        if singleWordType == 'empty':
            log(handle, "ERROR: No WordType selected")
            continue

        db.execute('CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY AUTOINCREMENT, lemma VARCHAR(250), Typ VARCHAR(250), Wortform VARCHAR(250))'.format(singleWordType.replace(' ', '_')))
        db.execute('CREATE TABLE IF NOT EXISTS {}_attr (id INTEGER PRIMARY KEY AUTOINCREMENT, lemma VARCHAR(250), Attribute VARCHAR(250), Value VARCHAR(250))'.format(singleWordType.replace(' ', '_')))
        
        db.commit()

        wordTypeIndex = 0
        for wordType in word_data['pos']:
            wordTypeIndex = wordTypeIndex + 1
            UpdateOrInsertIntoDB_attr(handle, db, singleWordType, [word_data['lemma'], 'pos' if wordTypeIndex == 0 else 'pos{}'.format(wordTypeIndex), wordType])
            for subAttributePos in word_data['pos'][wordType]:
                UpdateOrInsertIntoDB_attr(handle, db, singleWordType, [word_data['lemma'], wordType, subAttributePos])
        
        if hasattr(word_data,'inflected'):
            UpdateOrInsertIntoDB_attr(handle, db, singleWordType, [word_data['lemma'], 'inflected', word_data['inflected']])

        if hasattr(word_data,'language'):
            UpdateOrInsertIntoDB_attr(handle, db, singleWordType, [word_data['lemma'], 'language', word_data['language']])

        for col_name in header:
            if col_name in word_data:
                UpdateOrInsertIntoDB(handle, db, singleWordType, [word_data['lemma'], col_name, word_data[col_name]])
            elif 'flexion' in word_data and col_name in word_data['flexion']:
                UpdateOrInsertIntoDB(handle, db, singleWordType, [word_data['lemma'], col_name, word_data['flexion'][col_name]])
            else:
                pass

        db.commit()

def save(handle, db_path, data):
    global numUpdatedEntries
    global numInsertedEntries
        
    db = sqlite3.connect(db_path)

    create_db_entries(db, handle, data)

    db.commit()

    db.close()

    log(handle, "Total number updated entries {}".format(numUpdatedEntries))
    log(handle, "Total number inserted entries {}".format(numInsertedEntries))