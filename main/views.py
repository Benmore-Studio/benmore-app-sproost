from django.shortcuts import render
# authentication

def loginUser(request):
    context = {}
    return render(request, 'user/auth/login.html', context)

def signUpUser(request):
    context = {}
    return render(request, 'user/auth/signup.html', context)

# mains
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
    properties =[
        {'name':"Daine Homes", 'address':"4600 East Washington Street, Suite 305"},
        {'name':"Golden Homes", 'address':"No. 17 November Street. 10343 NY"},
        {'name':"Grand-Stay Homes", 'address':"No. 10 Silints Street. 42333 LA"},
        {'name':"Safe Homes", 'address':"No. 10 Silints Street. 42333 LA"},
    ]
    context ={
        'properties': properties
    }
    return render(request, 'user/propertyList.html', context)
def QuotationReturn(request):
    context ={}
    return render(request, 'user/quotation_returns.html', context)
