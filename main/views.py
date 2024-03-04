from django.shortcuts import render

# Create your views here.
def home(request):
    project_feed= [
        {
          'title':'Number of Uploaded projects',  'status': 'uploaded',  'count': 3, 
        },
        {
          'title': 'Number of Quotes Requested',  'status': 'quotes', 'count': 3, 
        },
        {
        'title':'Number of completed projects', 'status': 'completed', 'count': 2, 
        }
    ]
    context = {'project_feed': project_feed}
    return render(request, 'user/home-owner.html', context)

def loginUser(request):
    context = {}
    return render(request, 'user/auth/login.html', context)

def signUpUser(request):
    context = {}
    return render(request, 'user/auth/signup.html', context)