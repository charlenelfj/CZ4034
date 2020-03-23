from django.shortcuts import render
from urllib2 import *
import solr


# Create your views here.

# hello this file is for all the functions and rendering of the html pages
def Home():

    # need to read the db


    #Connect to Solr
    connection = solr.SolrConnection('http://localhost:8983/solr/hello',debug=True)
    print(connection)

    

def Test():
    return HttpResponse("hello")