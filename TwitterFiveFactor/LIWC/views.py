from django.shortcuts import render

# Create your views here.
def analysis(request):
    if(request.method == 'GET'):
        prodQuery = request.GET['analysisSearch']
        print(prodQuery)

    return render(request, 'LIWC/analysis.html')