# EmailAnalysis
Takes in email files and extracts keywords based on frequency of the word.  Finally outputting a website to explore the keywords and see frequency analysis.  SQLite was used because it has significant speed up and allowed easier analysis. 

- Generated files:
  - keywords.db 
  - \<foundkeyword\>.html
  - index.html

- Purpose of Files:
  - keywords.db - is a SQLite Database
  - bow.py - Does Bag of Words text analysis
  - runner.py - is the runner
  - compound.txt - list of compound words
  - noise.txt - list of noise words
  - substitution.txt - list of substitution (\<maped to\>, \<word1\>, \<word2\>,..., \<wordn\>)
  
- pip installs
  - `pip install tqdm` - this is to have the loading bar during execution
  - `pip install jinja2` - this is to use the HTML templets to generate the webpages
