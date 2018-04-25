# Bradley Levine and Joshua Vasko
# Python for Developers: Milestone 3
# Purpose: To create a class that allows for the Bag of Words algorthim
# Date Written: 9/22/2017
# Date Updated: 9/23/2017

# Imports
import re
from nltk.stem import SnowballStemmer

# Class Declaration
class BagOfWords:
	def __init__(self, **kwargs):
		#attributes
		self.compound_map = set()
		self.noise = set()
		self.replacement_map = dict()
		
		# gets the noise words if given
		if "noise" in kwargs:
			try:
				noise_file = open(kwargs["noise"], "r")
				for line in noise_file:
					self.noise.add(line.strip().lower())
			except Exception as e:
				print(e)
			else:
				noise_file.close()
		# mapping of a word to a replacement (csv)
		if "map" in kwargs:
			try:
				rmap_file = open(kwargs["map"], "r")
				for line in rmap_file:
					mapping = line.split(",")
					# this will get the first element from the line and treat it as the mapped word (key)
					# and generate a list of values that are mapped to that key
					self.replacement_map.update({mapping[0].strip().lower():[mapping[i].strip().lower() for i in range(1, len(mapping))]})
			except Exception as e:
				print(e)
			else:
				rmap_file.close()
		# gets the compund words list if given
		if "compound" in kwargs:
			try:
				cmap_file = open(kwargs["compound"], "r")
				for line in cmap_file:
					self.compound_map.add(line.strip().lower())
			except Exception as e:
				print(e)
			else:
				cmap_file.close()

# compound_concepts
# Purpose: To taverse a file to combine compound concepts.
	def compound_concepts(self):
		if len(self.compound_map) > 0:
			for cc in self.compound_map:
				self.text = self.text.replace(cc, cc.replace(" ", "_"))		# replaces the spaces in a found concept compund with _s

# scrubbing
# Purpose: To remove noise words from a file.				
	def scrubbing(self):
		if len(self.noise) > 0:
			for noise_word in self.noise:
				self.text = re.sub("(?<= )" + noise_word + "(?![A-Za-z]+)", " " , self.text)	# this will replace any noise words with a empty string (aka delete it)

# sub
# Purpose: To standardize text			
	def sub(self):
		if len(self.replacement_map.keys()) > 0:
			for replacement in self.replacement_map.keys():
				for word in self.replacement_map[replacement]:
					self.text = re.sub("(?<= )" + word + "(?![A-Za-z]+)", replacement, self.text)	# this will search the file for any words that should be replaced with a standarized word

# analysis
# Purpose: To aggregate the counts of each word within a file.					
	def analysis(self):
		if len(self.text) > 0:
			self.text = re.sub("[\d\.,'\":;\-\?\!\~\(\)\[\]\{\}<>*\\\\/=_\+&]", " ", self.text)	# this will cut out any digit or punctuation
			self.text = re.sub("[ ]{2,}", " ", self.text)							# this will remove spaces that are greater than one space
			self.text = self.text.strip()											# this will remove white-space from the beginning and end of data
			words = self.text.split(" ")											# this will break-up the data into words
			
			assert len(words) > 0													# double checks that there are words after processing
			
			ps = SnowballStemmer("english")
			# loops through the words
			for word in words:
				word = ps.stem(word)	# this will remove tense or plural parts of words
				
				self.normalized += word + " "
				
				#this tries to aviod keeping words that lost most of their letters and updates the frequencies of keywords
				if len(word) > 2:
					if word in self.frequency.keys():
						self.frequency[word] += 1
					else:
						self.frequency.update({word:1})

# run
# Purpose: To call each of the functions belonging to the BagOfWords class.
	def run(self, text):
		self.text = text.replace("\n", " ").replace("\t", " ").lower()
		self.normalized = ""
		self.frequency = dict()
		self.compound_concepts()
		self.scrubbing()
		self.sub()
		self.analysis()
		
		return self.normalized.strip(), self.frequency
		