# german-verbs
Based on https://github.com/gambolputty/german-nouns same for verbs

Setup:
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