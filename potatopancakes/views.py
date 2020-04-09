from django.shortcuts import render, redirect
#from urllib2 import *
import solr
from django.http import HttpResponse


# Create your views here.

# hello this file is for all the functions and rendering of the html pages
def Home():

    # need to read the db


    #Connect to Solr
    connection = solr.SolrConnection('http://localhost:8983/solr/hello',debug=True)
    print(connection)

    

def test(request):
    context = "sdasdasd"
    return render(request, 'home.html')