# What is this?
This project automatically downloads the newest wictionary blob and extracts all german word types into an sqlite database.
## I already have a wiktionary blob in the root folder.
The file needs to be named dewiktionary-latest-pages-articles-multistream.xml.bz2 on root folder. Additionally a file named dewiktionary-latest-pages-articles-multistream.xml.bz2_lastmodified need to be placed next to the other file with the content schema: "Tue, 03 Dec 2019 07:02:38 GMT". The correct content is the last updated information from the wiktionary blob.
In case the file was downloaded before by the application itself it will not download the file again. But in case it detects a newer version of the blob on the wiktionary page it will download and update.
## I already have a local.db from a previous run
In case a local.db already exists new entries will be inserted in case they don't exist yet. If an entry already exists it will be updated with the new value and the need for update will be displayed in the console output. In general the console output only contains changes done on the database.

# Source
This project is based on https://github.com/gambolputty/german-nouns.

# Execution time
A full run approximately takes about 2 days.

# Setup:
- Install Anaconda
- Open Anaconda Shell and select path where README.md is located
- Create environment by: conda create --name german-words-wiktionary-de-extract
- Activate environment by: conda activate german-words-wiktionary-de-extract
- Install requests: conda install requests
- Check python version: python -v (should be at least python 3.8.0 now)
- Install bz2file: conda install bz2file
- Install lxml: conda install lxml
- Install pyphen: python -m pip install pyphen
- Call: python ./create_db/main.py
- Database result is in local.db in root folder

# I want to use a mssql or postgresql database
Simply change the pyodbc string. The used commands are very basic and should be supported by mssql and postgresql too.
Though not tested yet!
