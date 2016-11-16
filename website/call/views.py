from django.shortcuts import render, HttpResponse

def index(request):
    context = {}
    return render(request, 'call/index.html', context)

def scripts(request):
    context = {}
    return render(request, 'call/scripts.html', context)

