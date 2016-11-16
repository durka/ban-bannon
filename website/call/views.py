from django.shortcuts import render, HttpResponse
from call import scrape

def index(request):
    context = {}
    return render(request, 'call/index.html', context)

def scripts(request):
    context = {'zip': request.POST['zip']}
    return render(request, 'call/scripts.html', context)

