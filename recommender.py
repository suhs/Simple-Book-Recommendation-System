#####################################
# Sungyeon Suh
# Book Recommendation System
#####################################
import csv
from copy import deepcopy
from math import sqrt

#csv filenames
bi_filename = 'GoodReads_Books_Info.csv'
ur_filename = 'GoodReads_Users_Ratings_TR.csv'

#global lists
books = {}
user_ratings = {}

'''
Purpose
	Load files and build dictionaries & lists for further uses
Precondition
	The file names are pre-fixed as a global variable
	The contents in 'GoodReads_Books_Info.csv' should not be re-ordered or changed
'''
def load_data():
	# load books' information
	with open(bi_filename, 'rU') as fbi:
		bi_reader = csv.reader(fbi)
		i = 0
		for row in bi_reader:
			if i != 0:	#ignore the first row
				spec = []
				spec.append(row[1])
				spec.append(row[6])
				spec.append(row[14])
				spec.append(row[15])
				spec.append(row[16])	
				books[row[0]] = spec
			i=1
	# load users' ratings
	with open(ur_filename, 'rU') as fur:
		ur_reader = csv.reader(fur)
		first_row = True
		for row in ur_reader:
			i = 0
			if first_row:
				book_ids = row
				book_ids.pop(0)
				first_row = False
			else:
				user = row.pop(0)
				for rating in row:
					if rating != '':
						user_ratings.setdefault(user,{})
						user_ratings[user][book_ids[i]] = int(rating)
					i+=1

'''
Purpose
	get a title of a book
'''
def get_title(l):
	return l[0]

'''
Purpose
	get an author of a book
'''
def get_author(l):
	return l[2]


'''
Purpose
	get a number of pages of a book
'''
def get_page_num(l):
	return l[1]

'''
Purpose
	get a list of genres of a book
'''
def get_genres(l):
	genres = l[3].split(';')
	return genres
	
'''
Purpose
	get a list of sub-genres of a book
'''
def get_sub_genres(l):
	sgenres = l[4].split(';')
	return sgenres

'''
Purpose
	calculate a pearson correlation between items x and y
'''
def pearson_corr(x, y):
	rx=0.0	#avg rate of x
	ry=0.0	#avg rate of y
	n=0
	m=0
	for user in user_ratings:
		if x in user_ratings[user]:
			rx += user_ratings[user][x]
			n += 1
		if y in user_ratings[user]:
			ry += user_ratings[user][y]
			m += 1
	rx = rx/n
	ry = ry/m

	topsum=0.0
	xsum=0.0
	ysum=0.0
	for user in user_ratings:
		if x in user_ratings[user] and y in user_ratings[user]:
			topsum += ((user_ratings[user][x]-rx)*(user_ratings[user][y]-ry))	
			xsum += (user_ratings[user][x]-rx)**2
			ysum += (user_ratings[user][y]-ry)**2
	if xsum==0 or ysum==0:
		wxy = 0
	else:
		wxy = topsum/(sqrt(xsum)*sqrt(ysum))
	return wxy

'''
Purpose
	Calculate Prob(u|v) for items u and v
'''
def prob_simm(u,v):
	frequv=0.0
	freqv=0.0
	for user in user_ratings:
		if u in user_ratings[user] and v in user_ratings[user]:
			frequv += 1
			freqv += 1
		elif v in user_ratings[user]:
			freqv += 1
	return frequv/freqv


'''
Purpose
	produce a top n items that are simmilar to a list of items a user had browsed
	return a sorted list of tuples where each tuple is structured as
	(sum of pearson correlation factors, book id)
'''
def item_based_recommender(U,book_list):
	C={}
	# go through each item in U and calculate a prob that
	# person who bought i will buy j 
	for i in U:
		for j in book_list:
			if not(j in U) and prob_simm(j,i)>=0.35 and not(j in C):
					C[j]=0.0
	# classic item-based recommendation
	for book in C:
		for i in U:
			C[book] += pearson_corr(book,i)	
	top_list = [(C[book],book) for book in C]
	top_list.sort()
	top_list.reverse()
	return top_list
	

'''
Purpose
	based on genres and sub-genred of books, 
	create an union of genres & sub-genres, calculate a frequency of each category,
	and sort books based on frequencies
'''
def content_based_recommender(U,n):
	C = {}
	contents = {}
	total = 0
	# calculate a frequency of each genres
	for i in U:
		loc = get_genres(books[i])+get_sub_genres(books[i])
		for content in loc:
			if content in contents:
				contents[content]+=1
			else:
				contents.setdefault(content,1.0)
			total+=1
	for content in contents:
		contents[content] /= total
	
	# build C based on frequency
	for j in books:	
		loc = get_genres(books[j])+get_sub_genres(books[j])
		if not(j in U):
			C.setdefault(j,0)
		for content in loc:
			if content in contents and not(j in U):
				C[j]+=contents[content]
	top_list = [(C[book],book) for book in C]
	top_list.sort()
	top_list.reverse()	
	return top_list[0:n]
			
'''
Purpose
	using the content based recommender and item based recommender,
	pick top n items 
'''	
def topN_recommender(U,n):
	lot = content_based_recommender(U,60)
	conbook = [i[1] for i in lot]
	lot = item_based_recommender(U, conbook)
	final_list = [i[1] for i in lot]
	return final_list[0:n]

#Main function
if __name__ == "__main__":
	nob = 10	#number of suggested books
	web_crawl = ['398201883','204328712','421459000']	
	user_books = []
	load_data()
	lob = topN_recommender(web_crawl,nob)
	print '::: Top {0} recommendation System:::'.format(nob)
	print '*User browsed books: '
	for ids in web_crawl:
		#for test purpose only: comment out
		#print ids, get_title(books[ids])
		print get_title(books[ids])
	print ' '
	print '*Recommended books: '
	n=1
	for ids in lob:
		#for test purpose only: comment out
		#print '{0}. {1}, {2}'.format(n, get_title(books[ids]), ids)
		print '{0}. {1}'.format(n, get_title(books[ids]))
		n+=1
