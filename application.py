from flask import Flask, request
import json
from newsapi import NewsApiClient
import datetime
import operator, string

application = Flask(__name__, static_url_path='')
newsapi = NewsApiClient(api_key='API_KEY')

@application.route('/get_top_headline_source')
def get_news_from_source():
	source = request.args.get('source', None)
	if source == None:
		top_headlines = newsapi.get_top_headlines(page_size=10, country="us")
	else:
		top_headlines = newsapi.get_top_headlines(sources=source, page_size=10)
	print(len(top_headlines['articles']))
	return json.dumps(top_headlines)

@application.route('/filter_source/')
def get_filtered_sources():
	category = request.args['category']
	filtered_source = newsapi.get_sources(category=category, language="en", country="us")
	return json.dumps(filtered_source, indent=4)

@application.route('/get_source_list')
def get_source_list():
	sources = newsapi.get_sources(language="en", country="us")
	print(sources)
	return json.dumps(sources, indent=4)

@application.route('/')
def root():
	try:
		return application.send_static_file('index.html')
	except Exception as e:
		print(e)

@application.route("/get_frequent_words")
def get_frequent_words():
	stop_words = set(line.strip() for line in open('static/stopwords_en.txt'))
	stop_words = stop_words.union(set(string.punctuation))
	stop_words.add("—")
	frequent_words_set = dict()
	top_articles = newsapi.get_top_headlines(page_size=30, language="en", country="us")
	top_articles = top_articles['articles']
	titles = [x['title'] for x in top_articles if x['title'] is not None]
	for title in titles:
		words = title.split(" ")
		words = [''.join(c for c in word if c not in string.punctuation) for word in words if not word.isdigit()]
		words = [word for word in words if word.lower() not in stop_words]
		for word in words:
			if word:
				if frequent_words_set.get(word):
					frequent_words_set[word] += 1
				else:
					frequent_words_set[word] = 1
	my_words = []
	count = 30
	sorted_words = sorted(frequent_words_set.items(), key=operator.itemgetter(1), reverse=True)
	for tple in sorted_words[:30]:
		dct = {}
		dct['word'] = tple[0]
		dct['size'] = tple[1]
		count -= 1
		my_words.append(dct)
	frequent_words_set = {"words":my_words}
	return json.dumps(frequent_words_set)

@application.route('/news', methods=['GET', 'POST'])
def get_news():
	keyword = request.args.get("keyword", "")
	category = request.args.get("category", "")
	from_date = request.args.get("from_date", "")
	to_date = request.args.get("to_date", "")
	sources = request.args.get("sources","")
	sources = None if sources == "all" else sources
	category = None if category == "all" else category
	try:
		keyword_news = newsapi.get_everything(q=keyword, sources=sources, from_param=from_date, to=to_date, language='en', page_size=30, sort_by="publishedAt")
	except Exception as e:
		error = json.loads(str(e).replace("'", "\""))
		return json.dumps(error)
	return json.dumps(keyword_news, indent=4)

if __name__ == '__main__':
	application.run(host="0.0.0.0")
