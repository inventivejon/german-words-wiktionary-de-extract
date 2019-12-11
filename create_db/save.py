from operator import itemgetter
import os
import locale
import csv
locale.setlocale(locale.LC_ALL, 'deu_deu' if os.name == 'nt' else 'de_DE.UTF-8')
import sqlite3

# from pdb import set_trace as bp

header = [
    # Nomen
    # 'id',
    'lemma',
    'pos'
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


def create_db_entries(db, data):
    # map dict values to list
    for word_data in data:
        
        singleWordType = 'empty'

        for wordType in word_data['pos']:
            if singleWordType == 'empty' and wordType != 'Toponym':
                singleWordType = wordType
                break

        if singleWordType == 'empty':
            print("ERROR: No WordType selected")
            continue

        db.execute('CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY AUTOINCREMENT, lemma VARCHAR(250), Typ VARCHAR(250), Wortform VARCHAR(250))'.format(singleWordType.replace(' ', '_')))
        db.execute('CREATE TABLE IF NOT EXISTS {}_attr (id INTEGER PRIMARY KEY AUTOINCREMENT, lemma VARCHAR(250), Attribute VARCHAR(250), Value VARCHAR(250))'.format(singleWordType.replace(' ', '_')))
        
        db.commit()

        for wordType in word_data['pos']:
            db_execute_parameters = [word_data['lemma'], 'pos', wordType]
            db.execute("INSERT INTO {}_attr VALUES(NULL,?,?,?)".format(singleWordType.replace(' ', '_')),db_execute_parameters)
            for subAttributePos in word_data['pos'][wordType]:
                db_execute_parameters = [word_data['lemma'], wordType, subAttributePos]
                db.execute("INSERT INTO {}_attr VALUES(NULL,?,?,?)".format(singleWordType.replace(' ', '_')),db_execute_parameters)
        
        if hasattr(word_data,'inflected'):
            db_execute_parameters = [word_data['lemma'], 'inflected', word_data['inflected']]
            db.execute("INSERT INTO {}_attr VALUES(NULL,?,?,?)".format(singleWordType.replace(' ', '_')),db_execute_parameters)

        if hasattr(word_data,'language'):
            db_execute_parameters = [word_data['lemma'], 'language', word_data['language']]
            db.execute("INSERT INTO {}_attr VALUES(NULL,?,?,?)".format(singleWordType.replace(' ', '_')),db_execute_parameters)

        for col_name in header:
            if col_name in word_data:
                db_execute_parameters = [word_data['lemma'], col_name, word_data[col_name]]
                print(db_execute_parameters)
                db.execute("INSERT INTO {} VALUES(NULL,?,?,?)".format(singleWordType.replace(' ', '_')),db_execute_parameters)
            elif 'flexion' in word_data and col_name in word_data['flexion']:
                db_execute_parameters = [word_data['lemma'], col_name, word_data['flexion'][col_name]]
                print(db_execute_parameters)
                db.execute("INSERT INTO {} VALUES(NULL,?,?,?)".format(singleWordType.replace(' ', '_')),db_execute_parameters)
            else:
                pass

        db.commit()

def save(db_path, data):
        
    db = sqlite3.connect(db_path)

    create_db_entries(db, data)

    db.commit()

    db.close()