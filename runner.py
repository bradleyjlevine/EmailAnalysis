# Bradley Levine and Joshua Vasko
# Python for Developers: Milestone 3
# Purpose: To display top 20 keywords from maildir data into an
#			html file with deadlinks for each keyword.
# Date Written: 9/24/2017
# Last Updated: 10/16/2017
# Python Version Used: 3.6.2

# Imports
from bow import BagOfWords as bw # Class to scrub text
import os # Traverse directory
import re # Pattern detection within files
import time # Used for progress bar
from tqdm import * # User needs to download seperately: pip install tqdm
from jinja2 import Template, Environment, FileSystemLoader # HTML Generation
import webbrowser as web # Open index automatically
import sqlite3 as sql # Database implementation
#import plotly # Report generation
#plotly.tools.set_credentials_file(username='jvasko', api_key='ljocCxHdgVsrmAqbXUOw')
import plotly.offline as offline # Report generation
import plotly.graph_objs as go # Report generation


# Main Function
def main():
##### Begin Menu Generation and User Choice #####
	root = None
	
	choices = next(os.walk("."))[1]
	
	if "__pycache__" in choices:
		choices.remove("__pycache__")
	
	print("Please enter the number for which choice you would like to run.")
	
	# Handle User Input
	while True:
		try:
			print_menu(choices)
			userin = input()
			if not userin.isdigit(): # Makes sure input is an integer
				raise ValueError
			if not 1 <= int(userin) <= len(choices):
				raise ValueError
		except ValueError:
			print('Please enter an integer within the menu.')
		else:
			userin = int(userin)
			break
	
	root = choices[userin - 1]
##### End Menu Generation and User Choice #####

##### Begin Import Email Files #####
	emails = []
	users = set()
	
	print("Finding files")
	for root, dirs, files in os.walk(root, topdown=False):
		for file in files:
			emails.append(os.path.join(root, file))
	print("Found emails")
##### End Import Email Files #####
	
##### Begin Create Database Connection ######
	try:
		conn = sql.connect("keywords.db")
		cursor = conn.cursor()
	except sql.Error as e:
		print(e)
	else:
		print("Connected to Database Successfully")
	
	create_db(cursor)
##### End Create Database Connection End #####
	
##### Begin Retrieve Frequencies and Email Scrubbing #####
	
	print("This may take a few moments...")

	fields = ["From", "To", "Date"]
	r = bw(noise="noise.txt", compound="compound.txt", map="substitution.txt")
	for file in tqdm(range(len(emails))):# Progress Bar
		try:
			m = re.search("\\.[\\w]+$", emails[file])
			if m == None:
				current = open(emails[file], "r")
				text = current.readlines()
				
				user = get_email_owner(text)
				
				### insert into user to email ###
				cursor.execute("""INSERT INTO user_to_email (user_name, file_path) VALUES ('""" + user + """','""" + emails[file] + """');""")
				### 		   end 			  ###
				
				text, header = extract_header(text)
				fill(header, fields)
				norm_text, keywords = r.run(text)
				
				###	insert into emails ###
				cursor.execute("""INSERT INTO emails (file_path, data, clean_data, from_, to_, date_) VALUES ('""" + emails[file] + """', '"""+ text.replace("'", "") +"""', '""" + norm_text + """', '""" + header["from"].replace("'", "") + """', '""" + header["to"].replace("'", "") + """', '""" + header["date"].replace("'", "") + """');""")
				
				for k in keywords:
					cursor.execute("""INSERT INTO keyword_to_email (file_path, keyword, frequency) VALUES ('""" + emails[file] + """', '""" + k + """', """ + str(keywords[k]) +""")""")
				###			end		   ###
				
				if file % 150 == 0:
					conn.commit()
			
		except sql.Error as e:
			print(e)
			conn.rollback()
	
	### Get the Top 20 keywords ###
	q = cursor.execute("""SELECT keyword, SUM(frequency) 
						  FROM keyword_to_email
						  GROUP BY keyword
						  ORDER BY SUM(frequency) DESC, keyword ASC
						  LIMIT 50;""")
	
	top20 = dict()
	for row in q:
		top20.update({row[0]:row[1]})
		for col in row:
			print(str(col) + "    ", end="")
		print("\n")
	### end ###
	
	### Get list of found users ###
	q = cursor.execute("""SELECT user_name, COUNT(*)
						  FROM user_to_email
						  GROUP BY user_name
						  ORDER BY user_name;""")
						  
	users = dict()
	for row in q:
		users.update({row[0]:row[1]})
		print(row[0])
	### end ###
	
	
	### Generate HTML ###
	index_html(top20, users)
	
	for k in top20:
		e = cursor.execute("""SELECT e.file_path, e.from_, e.to_, e.date_, e.data
							  FROM emails AS e
							  WHERE e.file_path IN (SELECT file_path
													FROM keyword_to_email
													WHERE '"""+ k +"""' = keyword)
							  ORDER BY e.file_path
							  ;""")
		em = {}
		emd = {}
		j = 1
		for row in e:
			i = 1
			em.update({row[0]:dict()})
			for f in fields:
				em[row[0]].update({f:row[i]})
				i+=1
			emd.update({row[0]:{"data":row[4], "p":j}})
			j+=1
			
		keyword_html(top20, users, em, emd, k, fields)
	
	for u in users:
		e = cursor.execute("""SELECT e.file_path, e.from_, e.to_, e.date_, e.data
							  FROM emails AS e
							  WHERE e.file_path IN (SELECT file_path
													FROM user_to_email
													WHERE '"""+ u +"""' = user_name)
							  ORDER BY e.file_path
							  ;""")
		em = {}
		emd = {}
		j = 1
		for row in e:
			i = 1
			em.update({row[0]:dict()})
			for f in fields:
				em[row[0]].update({f:row[i]})
				i+=1
			emd.update({row[0]:{"data":row[4], "p":j}})
			j+=1
		authors_html(top20, users, em, emd, u, fields)
	### 		end			 ###
	
	# Get Month and Date Frequencies
	date = dict()
	month = dict()
	q = cursor.execute("""SELECT date_, COUNT(*)
						  FROM emails
						  GROUP BY date_
						  ORDER BY COUNT(*);""")
	
	for row in q:
		try:
			rl = row[0].split(" ")
			if rl[1].isdigit():
				rk = rl[1] + rl[2][:3] + rl[3]
				mk = rl[2][:3]
			else:
				rk = rl[2] + rl[1][:3] + rl[3]
				mk = rl[1][:3]
			rk = rk.replace(",", "")
			if rk in date:
				date[rk] += 1
			else:
				date.update({rk: 1})
			if mk in month:
				month[mk] += 1
			else:
				month.update({mk: 1})
		except Exception as e:
			pass
##### End Retrieve Frequencies and Email Scrubbing #####
	
	generate_reports(users, top20, date, month)
	
	conn.close()
	web.open("index.html")
	
# create_db
# Purpose: Creates database to hold information extracted from emails. "keywords.db"
# Date Written: 10/12/17
# Date Updated: 10/15/17
def create_db(c):

	sql_create_tables = """
				   DROP TABLE IF EXISTS keyword_to_email;
				   DROP TABLE IF EXISTS user_to_email;
				   DROP TABLE IF EXISTS emails;
					
				   CREATE TABLE
				   IF NOT EXISTS emails(
				   file_path text NOT NULL,
				   data text,
				   clean_data text,
				   from_ text,
				   to_ text,
				   date_ text,
				   PRIMARY KEY(file_path)
				   );
				   
				   CREATE TABLE
				   IF NOT EXISTS keyword_to_email(
				   file_path text NOT NULL,
				   keyword text NOT NULL,
				   frequency integer,
				   FOREIGN KEY(file_path) REFERENCES emails (file_path),
				   PRIMARY KEY(file_path, keyword)
				   );
				   
				   CREATE TABLE
				   IF NOT EXISTS user_to_email(
				   user_name NOT NULL,
				   file_path NOT NULL,
				   FOREIGN KEY(file_path) REFERENCES emails (file_path),
				   PRIMARY KEY(user_name, file_path)
				   );
				"""
	try:
		c.executescript(sql_create_tables)
	except sql.Error as e:
		print(e)
	else:
		print("Created Database")

# index_html
# Purpose: Creations of index html page with keywords.
# Date Written: 9/24/2017
# Date Updated: 10/08/2017
def index_html(data, auths):
	j2_env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))), trim_blocks=True)
	t = j2_env.get_template("index_template.html")
	html = open("index.html", "w+")
	html.write(t.render(keywords=data, authors=auths))
	html.close()

# keyword_html
# Purpose: Creates individual html pages for each keyword.
# Date Written: 10/08/17
# Date Updated: 10/12/17
def keyword_html(data, auths, emails , emd, keyword, fields):
	j2_env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))), trim_blocks=True)
	t = j2_env.get_template("keyword_template.html")
	html = open(keyword + ".html", "w+")
	html.write(t.render(keywords=data, authors=auths, emails=emails, ed=emd, keyword=keyword, fields=fields))
	html.close()

# authors_html
# Purpose: Creates individual html pages for each author.
# Date Written: 10/08/17
# Date Updated: 10/12/2017
def authors_html(data, auths, emails, emd, author, fields):
	j2_env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))), trim_blocks=True)
	t = j2_env.get_template("author_template.html")
	html = open(author + ".html", "w+")
	html.write(t.render(keywords=data, authors=auths, emails=emails, ed=emd, author=author, fields=fields))
	html.close()

# extract_header
# Purpose: Removes header from each file so they do not get counted.
# Date Written: 9/24/2017
# Date Updated: 9/25/2017
def extract_header(data):
	tracker = dict()
	r = ""
	for line in data:
		if not (line.startswith("Message-ID:") or line.startswith("Date:") or line.startswith("X-From:") or line.startswith("X-To:") or line.startswith("X-cc:") or \
			line.startswith("X-bcc:") or line.startswith("X-Folder:") or line.startswith("X-Origin:") or line.startswith("X-FileName:") or \
			line.startswith("Subject:") or line.startswith("Date:") or line.startswith("Mime-Version:") or line.startswith("Content-Type:") or \
			line.startswith("Content-Transfer-Encoding:") or line.startswith("From:") or line.startswith("To:")):
			r += line
		else:
			t = line.split(":", 1)
			if len(t) == 2 and t[0].strip() not in tracker:
				tracker.update({t[0].strip().lower():t[1].strip().lower()})
	return r, tracker

# get_email_owner
# Purpose: Retrieves whom the email document belongs to.
# Date Written: 10/08/17
# Date Updated: 10/08/17
def get_email_owner(data):
	for line in data:
		if line.startswith("X-Origin:"):
			return line.replace("X-Origin: ", "").strip().lower()
	return "None"

# print_menu
# Purpose: Generates menu for user to select root.
# Date Written: 10/12/17
# Date Updated: 10/13/17
def print_menu(l):
	j = 1
	for i in l:
		print("\t" + str(j) + ". " + i)
		j+=1

# fill
# Purpose: Handles empty header field to avoide KeyValue Errors.
# Date Written: 10/12/17
# Date Updated: 10/13/17
def fill(header, fields):
	for field in fields:
		if field.lower() not in header:
			header.update({field.lower():"None"})
			
# generate_reports
# Purpose: Generates reports for user consumption.
# Date Written: 10/8/17
# Date Written: 10/15/17
def generate_reports(authors, keywords, date, month):
	# Author
	x1 = []
	y1 = []
	for author in authors:
		x1.append(author)
		y1.append(authors[author])
	AutBar = [go.Bar(x = x1, y = y1)]
	AutPie = [go.Pie(labels = x1, values = y1)]
	offline.plot(AutBar, filename = "AuthorFreqBar.html")
	offline.plot(AutPie, filename = "AuthorPie.html")
	
	# Keyword
	x2 = []
	y2 = []
	for key, value in keywords.items():
		x2.append(key)
		y2.append(int(value))
	KeyBar = [go.Bar(x = x2, y = y2)]
	KeyPie = [go.Pie(labels = x2, values = y2)]
	offline.plot(KeyBar, filename = "KeyFreqBar.html")
	offline.plot(KeyPie, filename = "KeyPie.html")
	
	# Days
	x3 = []
	y3 = []
	for key, value in date.items():
		x3.append(key)
		y3.append(int(value))
	DateBar = [go.Bar(x = x3, y = y3)]
	offline.plot(DateBar, filename = "DateFreqBar.html")
	
	# Months
	x4 = []
	y4 = []
	for key, value in month.items():
		x4.append(key)
		y4.append(int(value))
	MonthBar = [go.Bar(x = x4, y = y4)]
	MonthPie = [go.Pie(labels = x4, values = y4)]
	offline.plot(MonthBar, filename = "MonthFreqBar.html")
	offline.plot(MonthPie, filename = "MonthPie.html")

# Main Call
if __name__ == "__main__":
	main()
