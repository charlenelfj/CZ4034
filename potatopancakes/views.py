from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
#from urllib2 import *
import solr
from django.http import HttpResponse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json
import random



# Create your views here.

# hello this file is for all the functions and rendering of the html pages
# create a function 
def geeks_view(request): 
    # create a dictionary 
    context = { 
        "data" : 99, 
    } 
    # return response 
    return render(request, "geeks.html", context) 

def get_image_url(post):
    # extract and format url of each post
    post_url = str(post['key'])
    post_url = post_url[2:]
    post_url = post_url[:-2]

    # beauuuuuuuuuuuuuutiful sooooooooup
    soup = BeautifulSoup(urlopen(post_url).read())
    scripts = soup.select('script[type="text/javascript"]')
    # for all the sections in html that has <script></script>
    for script in scripts:
        eachhtml = str(script)
        if 'window._sharedData =' in eachhtml:
            # get the string
            data = eachhtml
            # regex to find the display_url key
            r = re.compile(r'"display_url":(.*)",')
            initialdata = r.findall(data)
            initialdata = str(initialdata)
            # format the retrieved url eg slice
            sep = ","
            rest = initialdata[2:].split(sep, 1)[0]
            
            #process the retrieved url
            rest = rest.replace("\\u0026", "&")
            rest = rest.replace("\&", "&")
            rest = rest.replace('"', '')

            # update in each post
            post.update({'img_url': rest})
            break

    return post

def format_datetime(post):
    # format the datetime to render
    datetime= post['datetime'][0]
    date_time = datetime.strftime("%m/%d/%Y, %H:%M:%S")
    # update in each post
    post.update({'datetime': date_time})

    return post

def get_profile_pic(post):
        post_author = post['author']
        if (post_author == "washington post"):
            img_src = "https://imgur.com/zzotN7n.png"
        elif (post_author == "cbs"):
            img_src = "https://imgur.com/Iz5UPfm.png"
        elif (post_author == "abc"):
            img_src = "https://imgur.com/oJ5DUmJ.png"
        elif (post_author == "fox"):
            img_src = "https://imgur.com/Q0XTm3K.png"
        elif (post_author == "au"):
            img_src = "https://imgur.com/SH17JVA.png"
        elif (post_author == "bbc"):
            img_src = "https://imgur.com/UKHO0Ig.png"
        elif (post_author == "cnbc"):
            img_src = "https://imgur.com/Hzy0HSA.png"
        elif (post_author == "guardian"):
            img_src = "https://imgur.com/M8NgI6p.png"
        elif (post_author == "nbc"):
            img_src = "https://imgur.com/e0OncLN.png"
        elif (post_author == "nytimes"):
            img_src = "https://imgur.com/29eFbed.png"
        elif (post_author == "straits times"):
            img_src = "https://imgur.com/CvZtfDD.png"
        else:
            img_src = ""

        post.update({'author_url': img_src})

        return post 


def home(request):
    print("hersdfafasdfae")
    #specifying connection to solr
    connection = solr.SolrConnection('http://localhost:8983/solr/mainindex',debug=True)

    # need to make a query to solr
    response = connection.query('*:*',fields="author, likes, unprocessed_comments, key, datetime, labels", rows=8).results
    # print(response)
    print(type(response))

    print(random.shuffle(response))
    
    for post in response:
        # print(post)
        # beauuuuuuuuuuuuuutiful sooooooooup
        post = get_image_url(post)
        # get the profile picture of each author
        # post = get_profile_pic(post)

        # format datetime
        post = format_datetime(post)

        likes = post['likes']
        newlikes = likes[0]
        post['likes'] = newlikes


    context = { 
        "results" : response, 
    } 


    return render(request, 'home.html', context)


# 127.0.0.1:8000/search
def search(request, searchterm, author, hashtag, sort, category):
    print(author)
    print("Submitted a search query")
    # getting the form data
    # search_term = request.POST.get('search_term')

    # converting any upper case to lower case
    search_term = searchterm.lower()

    #specifying connection to solr
    connection = solr.SolrConnection('http://localhost:8983/solr/mainindex',debug=True)

    # type:quote AND (person_t:obama OR person_t:romney)
    # same rules: either search for search term/hashtag
    # can have search term + author + category + sorting
    # or can have hashtag + author + category + sorting
    # category and author and sorting is optional: ie if have then add 

    # if a category search is invoked
    # check got any is hashtag/term/nothing
    print("category: " + category)
    if (category != 'null' and category != "all"):
            if (hashtag != 'null'):
                if (author == 'null'):
                    query = "hashtags:" + hashtag + " AND labels:" + category
                else:
                    newauthor = author.split('&')
                    # multiple authors
                    query = ""
                    if (len(newauthor) != 1):
                        for j in range (len(newauthor)):
                            print(newauthor[j])
                            if (j != (len(newauthor)-1)):
                                query = query + "(hashtags:" + hashtag + " AND author:" + newauthor[j] + " AND labels:" + category + ") OR "
                            else:
                                query = query + "(hashtags:" + hashtag + " AND author:" + newauthor[j] + " AND labels:" + category + ")"

                    #one author
                    else:
                        query = "hashtags:" + hashtag + " AND author:" + author + " AND labels:" + category   
                    
                
            elif(search_term != 'null'):
                if (author == 'null'):
                    query = "processed_comments:" + search_term + " AND labels:" + category
                else:
                    # checking for multiple authors
                    
                    newauthor = author.split('&')
                    # multiple authors
                    query = ""
                    if (len(newauthor) != 1):
                        for j in range (len(newauthor)):
                            print(newauthor[j])
                            if (j != (len(newauthor)-1)):
                                query = query + "(processed_comments:" + search_term + " AND author:" + newauthor[j] + " AND labels:" + category + ") OR "
                            else:
                                query = query + "(processed_comments:" + search_term + " AND author:" + newauthor[j] + " AND labels:" + category + ")"

                    #one author
                    else:
                        query = "processed_comments:" + search_term + " AND author:" + author + " AND labels:" + category   
            else:
                if (author != 'null'):

                    newauthor = author.split('&')
                    # multiple authors
                    query = ""
                    if (len(newauthor) != 1):
                        for j in range (len(newauthor)):
                            print(newauthor[j])
                            if (j != (len(newauthor)-1)):
                                query = query + "(author:" + newauthor[j] + " AND labels:" + category + ") OR "
                            else:
                                query = query + "(author:" + newauthor[j] + " AND labels:" + category + ")"

                    #one author
                    else:
                        query = "author:" + author + " AND labels:" + category   
                else:
                    query = "labels:" + category

    # no category so normal search
    else:
        if (hashtag != 'null'):
            if (author == 'null'):
                query = "hashtags:" + hashtag
            else:

                newauthor = author.split('&')
                query = ""
                # multiple authors
                if (len(newauthor) != 1):
                    for j in range (len(newauthor)):
                        print(newauthor[j])
                        if (j != (len(newauthor)-1)):
                            query = query + "(hashtags:" + hashtag + " AND author:" + newauthor[j] + ") OR "
                        else:
                            query = query + "(hashtags:" + hashtag + " AND author:" + newauthor[j] + ")"

                #one author
                else:
                    query = "hashtags:" + hashtag + " AND author:" + author
        # term search
        else:
            if (author == 'null'):
                if (search_term == 'null'):
                    search_term = "*"
                query = "processed_comments:" + search_term
            else:
                newauthor = author.split('&')

                if (search_term == 'null'):
                    search_term = "*"
                query = ""
                # multiple authors
                if (len(newauthor) != 1):
                    for j in range (len(newauthor)):
                        print(newauthor[j])
                        if (j != (len(newauthor)-1)):
                            query = query + "(processed_comments:" + search_term + " AND author:" + newauthor[j] + ") OR "
                        else:
                            query = query + "(processed_comments:" + search_term + " AND author:" + newauthor[j] + ")"

                #one author
                else:
                    query = "processed_comments:" + search_term + " AND author:" + author

        

    print("sorting method:" + sort)
    print(query)

    sort_column = None

    # check any sorting required
    if (sort == "mostlikes"):
        sort_column = 'likes'
    elif (sort == "mostrecent"):
        sort_column = "datetime"

        
    # need to make a query to solr
    # start can be a parameter that the user specify 
    # so each page will show 5 posts
    response = connection.query(query , fields="author, likes, unprocessed_comments, key, datetime, labels", rows=8, sort=sort_column, sort_order="desc").results
    print(response)
    
    # if no response most likely is spell wrong word
    first_term = None
    query_term = None
    if (len(response) == 0):
        print("here")

        # check if its term search or hashtag search
        # check for term
        if (hashtag == "null"):
            #spell correction part
            search_term = search_term.replace(" ", '')
            conn = urlopen("http://localhost:8983/solr/mainindex/suggest?suggest=true&wt=json&suggest.dictionary=infixSuggester&suggest.q="+search_term)
            # return the results as a json object with responseHeader and everything
            suggestion_json = json.load(conn)
            suggest_results = suggestion_json['suggest']['infixSuggester'][search_term]['suggestions']
            print(suggest_results)

            # perform query on the first 'clean' suggested term
            # regex to clean the html text
            tag_re = re.compile(r'<[^>]+>')

            for i in range(len(suggest_results)):
                print(suggest_results[i]['term'])
                first_term = re.sub(tag_re, '', suggest_results[i]['term'])
                if(bool(re.match('^[a-zA-Z0-9]+$', first_term))):
                    break
            
            if (category != 'null' and category != "all"):
                    if (author == 'null'):
                        query = "processed_comments:" + first_term + " AND labels:" + category   
                    else:
                        query = "processed_comments:" + first_term + " AND author:" + author + " AND labels:" + category
            else:
                if (author == 'null'):
                    query = "processed_comments:" + first_term
                else:
                    query = "processed_comments:" + first_term + " AND author:" + author

            print("after query: " + query)

        # checking for hashtag
        else:
            #spell correction part
            conn = urlopen("http://localhost:8983/solr/mainindex/suggest?suggest=true&wt=json&suggest.dictionary=fuzzySuggester&suggest.q="+hashtag)
            # return the results as a json object with responseHeader and everything
            suggestion_json = json.load(conn)
            suggest_results = suggestion_json['suggest']['fuzzySuggester'][hashtag]['suggestions']

            # perform query on the first 'clean' suggested term
            # regex to clean the html text
            tag_re = re.compile(r'<[^>]+>')

            for i in range(len(suggest_results)):
                print(suggest_results[i]['term'])
                first_term = re.sub(tag_re, '', suggest_results[i]['term'])
                if(bool(re.match('^[a-zA-Z0-9]+$', first_term))):
                    break

            
            if (category != 'null' and category != "all"):
                    if (author == 'null'):
                        query = "hashtags:" + first_term + " AND labels:" + category   
                    else:
                        query = "hashtags:" + first_term + " OR author:" + author + " AND labels:" + category
            else:
                if (author == 'null'):
                    query = "hashtags:" + first_term
                else:
                    query = "hashtags:" + first_term + " OR author:" + author

        sort_column = None

        # check any sorting required
        if (sort == "mostlikes"):
            sort_column = 'likes'
        elif (sort == "mostrecent"):
            sort_column = "datetime"
        
        # query again
        response = connection.query(query , fields="author, likes, unprocessed_comments, key, datetime, labels", rows=8, sort=sort_column, sort_order="desc").results

        

    

    # #spell correction part
    # connection = urlopen("http://localhost:8983/solr/testauthor/suggest?suggest=true&wt=json&suggest.dictionary=infixSuggester&suggest.q="+search_term)
    # # return the results as a json object with responseHeader and everything
    # suggestion_json = json.load(connection)
    # suggest_results = suggestion_json['suggest']['infixSuggester'][search_term]['suggestions']

    # # if the first term is already the word, then don't need to suggest anything since its a proper word
    # # regex to clean the html text
    # tag_re = re.compile(r'<[^>]+>')
    # first_term = re.sub(tag_re, '', suggest_results[0]['term'])
    # print(first_term)
    # if (search_term == first_term):
    #     print("dont need")
    # else:
    #     print("need leh")
        # see you want to display everything or just one will do
        # then if just display one only right then maybe you want to do an additional query on the first one then equates to response
    
    message = ""
    # if there's no results 
    if (len(response) == 0):
        message = "There is no results in the database matching to your query, please try again."
    
    else:
        # for each post returned
        for post in (response):
            # beauuuuuuuuuuuuuutiful sooooooooup
            post = get_image_url(post)
            # get the profile picture of each author
            # post = get_profile_pic(post)

            # format datetime
            post = format_datetime(post)

            likes = post['likes']
            newlikes = likes[0]
            post['likes'] = newlikes



    context = { 
        "results" : response, 
    } 

    feedbackmessage = {
        "errormessage" : message,
    }

    suggestion = {
        "textsuggestion": first_term
    }

    # print("suggest: " + first_term)
    queryterm = ""
    # if no suggestion, display original query
    if (first_term == "" or first_term is None):
        if (hashtag != "null"):
            queryterm = "#" + hashtag
        else:
            queryterm = search_term

    if (message != ""):
        first_term = None

    if (queryterm == "*" or queryterm == "null"):
        queryterm = "all records"

    print("query: " + queryterm)
    

    return render(request, "home.html", {'results': response, 'errormessage': message, 'suggestionmessage': first_term, 'queryterm': queryterm}) 