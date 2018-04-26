# EmailAnalysis
Takes in email files and extracts keywords based on frequency of the word.  Finally outputting a website to explore the keywords and see frequency analysis.
&nbsp;
Generated files:
&nbsp;
  keywords.db 
  &nbsp;
  \<foundkeyword\>.html
  &nbsp;
  index.html
  &nbsp;
  &nbsp;
Purpose of Files:
&nbsp;
  keywords.db - is a SQLite Database
  &nbsp;
  bow.py - Does Bag of Words text analysis
  &nbsp;
  runner.py - is the runner
  &nbsp;
  compound.txt - list of compound words
  &nbsp;
  noise.txt - list of noise words
  &nbsp;
  substitution.txt - list of substitution (<maped to>, word, word,..., word)
  &nbsp;
