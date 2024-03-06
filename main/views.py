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
    project_history = [
        {'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
    ]
    context = {'project_feed': project_feed, 'project_history': project_history}
    return render(request, 'user/home-owner.html', context)

def requestQuotes(request):
    context ={}
    return render(request, 'user/request_quotes.html', context)

def assignAgent(request):
    context ={}
    return render(request, 'user/assignAgent.html', context)

def propertyList(request):
    context ={}
    return render(request, 'user/propertyList.html', context)

def loginUser(request):
    context = {}
    return render(request, 'user/auth/login.html', context)

def signUpUser(request):
    context = {}
    return render(request, 'user/auth/signup.html', context)