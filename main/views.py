from django.shortcuts import render
# authentication

# loggedInUser = 'home-owner'| 'agent'| 'contractor'| 'investor', this is used to switch between bottom navigation, default navigation is home-owner, so need to add it.

loggedInUser = 'contractor'

# take a look at each template to know why this loggedInUser is used


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
    
    
    if loggedInUser == 'contractor':
        context = {
        'loggedInUser': loggedInUser
    }
        return render(request, 'user/contractor_home.html', context)
    else:
        context = {'project_feed': project_feed, 'project_history': project_history, 'loggedInUser': loggedInUser}
        return render(request, 'user/home.html', context)

def requestQuotes(request):
    context ={
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/request_quotes.html', context)

def assignAgent(request):
    context ={
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/assignAgent.html', context)

def propertyList(request):
    properties =[
        {'name':"Daine Homes", 'address':"4600 East Washington Street, Suite 305"},
        {'name':"Golden Homes", 'address':"No. 17 November Street. 10343 NY"},
        {'name':"Grand-Stay Homes", 'address':"No. 10 Silints Street. 42333 LA"},
        {'name':"Safe Homes", 'address':"No. 10 Silints Street. 42333 LA"},
    ]
    context ={
        'properties': properties,
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/propertyList.html', context)

def QuotationReturn(request):
    context ={
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/quotation_returns.html', context)

def MenuList(request):
    context ={
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/menu.html', context)

def contractors(request):
    searchResults = [
        {'name': 'Olivia Rhye', 'profession': 'plumber', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Phoenix Baker', 'profession': 'electrician', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Lana Steiner', 'profession': 'carpenter', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Demi Wilkinson', 'profession': 'interior designer', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Candice Wua', 'profession': 'painter', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Natali Craig', 'profession': 'carpenter', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Drew Cano', 'profession': 'painter', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Phoenix Baker', 'profession': 'electrician', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Lana Steiner', 'profession': 'carpenter', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Demi Wilkinson', 'profession': 'interior designer', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
    ]
    context ={
        'contractors': searchResults,
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/contractors.html', context)
 
def contractorDetail(request, profession):
    context ={
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/contractorDetail.html', context)

def addProperty(request):
    context ={
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/add_property.html', context)

def editProfile(request):
    context ={}
    return render(request, 'user/edit_profile.html', context)

    