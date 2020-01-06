import xml.etree.ElementTree as etree
import os
import re
from bz2file import BZ2File
from pdb import set_trace as bp
from pprint import pprint
from wiktionary_de_parser import Parser
from extend_flexion import extend_flexion
from save import save
from PostprocessDB import performAllPostprocessingDBOperations
from getWiktionaryData import DownloadIfNeeded
import time
import sys

wiki_url = 'https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bzfile_path = 'dewiktionary-latest-pages-articles-multistream.xml.bz2'

def log(handle, content):
    try:
        handle.write(content.encode(sys.stdout.encoding, errors='replace').decode("utf-8") + '\n')
    except:
        pass
    print(content)

start_time = time.time()

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

elapsed_time = time.time() - start_time

log(handle, f'Saved {len(data)} records')

elapsed_hours, elapsed_remainder = divmod(elapsed_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)

formattedTimeString = "{}:{}:{}".format(round(elapsed_hours), round(elapsed_minutes), round(elapsed_seconds))
log(handle, "Execution time (hh:mm:ss): {}".format(formattedTimeString))

performAllPostprocessingDBOperations(handle, 'local.db')

elapsed_hours, elapsed_remainder = divmod(elapsed_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)

formattedTimeString = "{}:{}:{}".format(round(elapsed_hours), round(elapsed_minutes), round(elapsed_seconds))
log(handle, "Execution time (hh:mm:ss): {}".format(formattedTimeString))

handle.close()