import xml.etree.ElementTree as etree
import os
import re
from bz2file import BZ2File
from pdb import set_trace as bp
from pprint import pprint
from wiktionary_de_parser import Parser
from extend_flexion import extend_flexion
from save import save
from getWiktionaryData import DownloadIfNeeded
import time

wiki_url = 'https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bzfile_path = 'dewiktionary-latest-pages-articles-multistream.xml.bz2'

def log(handle, content):
    handle.write(content)
    print(content)

timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
handle = open("log_main_py_{}.txt".format(timestamp), 'w+')

DownloadIfNeeded(handle, bzfile_path, wiki_url)

bz = BZ2File(bzfile_path)

data = []
index = 0
for record in Parser(bz, custom_methods=[extend_flexion]):
    # Titel muss Buchstabend enthalten
    if re.search(r'([a-zA-Z]+)', record['title']) is None:
        continue

    if re.search(r'{{Schweizer und Liechtensteiner Schreibweise\|[^}]+}}', record['wikitext']):
        continue

    if re.search(r'{{Alte Schreibweise\|[^}]+}}', record['wikitext']):
        continue

    if 'language' not in record or record['language'].lower() != 'deutsch':
        continue

    if 'pos' not in record:
        continue

    index += 1
        
    data.append(record)

log(handle, "Index {} reached".format(index))

save(handle, 'local.db', data)

log(handle, f'Saved {len(data)} records')