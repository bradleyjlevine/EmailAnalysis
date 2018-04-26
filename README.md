# EmailAnalysis
Takes in email files and extracts keywords based on frequency of the word.  Finally outputting a website to explore the keywords and see frequency analysis.

Generated files:
  keywords.db
  <foundkeyword>.html
  index.html
  
Purpose of Files:
  keywords.db - is a SQLite Database
  bow.py - Does Bag of Words text analysis
  runner.py - is the runner
  compound.txt - list of compound words
  noise.txt - list of noise words
  substitution.txt - list of substitution (<maped to>, word, word,..., word)
