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
totalParsed = 0
numericTitle = 0
schweizerWording = 0
oldWording = 0
noLanguage = 0
noPos = 0
for record in Parser(bz, custom_methods=[extend_flexion]):
    totalParsed = totalParsed + 1
    #print("Total Parsed: {}".format(totalParsed))
    #print("Indexed: {}".format(index))
    # Titel muss Buchstaben enthalten
    if re.search(r'([a-zA-Z]+)', record['title']) is None:
        #print("Keine Buchstaben im Titel {}".format(record['title']))
        numericTitle = numericTitle + 1
        continue

    if re.search(r'{{Schweizer und Liechtensteiner Schreibweise\|[^}]+}}', record['wikitext']):
        #print("Schweizer/Liechtensteiner Schreibweise")
        schweizerWording = schweizerWording + 1
        continue

    if re.search(r'{{Alte Schreibweise\|[^}]+}}', record['wikitext']):
        #print("Alte Schreibweise")
        oldWording = oldWording + 1
        continue

    if ('lang' not in record or record['lang'].lower() != 'deutsch') and ('language' not in record or record['language'].lower() != 'deutsch') and ('langCode' not in record or record['langCode'].lower() != 'de'):
        #print("Kein Hinweis auf die verwendete Sprache")
        noLanguage = noLanguage + 1
        continue

    if 'pos' not in record:
        #print("Kein pos enthalten")
        noPos = noPos + 1
        continue

    ### Filter if only a specific kind shall be processed

    #isAdjektiv = False

    #for wordType in record['pos']:
    #    if wordType == 'Adjektiv':
            # print("{}".format(record))
    #        isAdjektiv = True
    #        break

    #if isAdjektiv == False:
    #    continue

    ### End of Filter

    index += 1

    ### Filter if only a specific amount shall be processed
    if index > 0:
        break
    ### End of Filter
    
    data.append(record)

log(handle, "Finally parsed: {}".format(totalParsed))
log(handle, "Index {} reached".format(index))
log(handle, "NumericTitle: {}".format(numericTitle))
log(handle, "schweizerWording: {}".format(schweizerWording))
log(handle, "oldWording: {}".format(oldWording))
log(handle, "noLanguage: {}".format(noLanguage))
log(handle, "noPos: {}".format(noPos))

# save(handle, 'local.db', data)

log(handle, f'Saved {len(data)} records')

elapsed_time = time.time() - start_time

log(handle, f'Saved {len(data)} records')

elapsed_hours, elapsed_remainder = divmod(elapsed_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)

formattedTimeString = "{}:{}:{}".format(round(elapsed_hours), round(elapsed_minutes), round(elapsed_seconds))
log(handle, "Execution time (hh:mm:ss): {}".format(formattedTimeString))

start_time = time.time()

performAllPostprocessingDBOperations(handle, 'local.db')

elapsed_hours, elapsed_remainder = divmod(elapsed_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)

formattedTimeString = "{}:{}:{}".format(round(elapsed_hours), round(elapsed_minutes), round(elapsed_seconds))
log(handle, "Execution time (hh:mm:ss): {}".format(formattedTimeString))

handle.close()