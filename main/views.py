from django.shortcuts import render
# authentication

# loggedInUser = 'home-owner'| 'agent'| 'contractor'| 'investor', this is used to switch between bottom navigation, default navigation is home-owner, so need to add it.

loggedInUser = 'home-owner'

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

    


# web based admin- applications


def loginAdmin(request):
  context ={}  
  return render(request, 'admin/login.html', context) 

def adminDashboard(request):
    recent_home_owners =[
        {
            'name':'Olivia Rhye', 'photo':'/static/images/ownerAvatar.png', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"accepted"
        },
        {
            'name':'Olivia Rhye', 'photo':'/static/images/ownerAvatar.png', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"rejected"
        },
        {
            'name':'Olivia Rhye', 'photo':'/static/images/ownerAvatar.png', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"accepted"
        },
        {
            'name':'Olivia Rhye', 'photo':'/static/images/ownerAvatar.png', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"pending"
        },
    ]
    recent_agents =[
        {
            'name':'Olivia Rhye', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"accepted", 'rating':4, 'total_project':5
        },
        {
            'name':'Olivia Rhye', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"rejected", 'total_project':2
        },
        {
            'name':'Olivia Rhye', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"accepted", 'total_project':1
        },
        {
            'name':'Olivia Rhye', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"pending",'total_project':10       
            },
    ]
    recent_contractors =[
        {
            'name':'Olivia Rhye', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"accepted", 'rating':4, 'total_project':5
        },
        {
            'name':'Olivia Rhye', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"rejected", 'rating':4, 'total_project':2
        },
        {
            'name':'Olivia Rhye', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"accepted", 'rating':4, 'total_project':1
        },
        {
            'name':'Olivia Rhye', 'phone': '+1 834 955 0920', 'email':'olivia@untitledui.com', 'project_name':'Project title', 'quotation_status':"pending", 'rating':4, 'total_project':10       
            },
    ]
    project_history = [
        {'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
    ]
    
    overall_stats = [
        {'title':'Home Owners', 'project_counts': 316, 'increased_by':'20%', 'action':'View owners'},
        {'title':'Agents', 'project_counts': 316, 'increased_by':'10%', 'action':'View agents'},
        {'title':'Contractors', 'project_counts': 316, 'increased_by':'10%', 'action':'View contractors'},
        {'title':'Active Projects', 'project_counts': 316, 'increased_by':'40%', 'action':'View projects'},
    ]
    context ={'recent_home_owners': recent_home_owners, 'recent_agents':recent_agents,
              'recent_contractors': recent_contractors, 'project_history': project_history, 'overall_stats': overall_stats }  
    return render(request, 'admin/dashboard.html', context)

def projectRequest(request):
    project_history = [
        {'id':1,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':2,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':3,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':4,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':5,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':6,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':7,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':8,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':9,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':10,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':11,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'id':12,'name':'Bungalow Renovation', 'quotation_status': 'pending', 'home_owner': {'name':'Olivia Rhye', 'image':'/static/images/ownerAvatar.png'}, 'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
    ]
    context ={'project_history': project_history}  
    return render(request, 'admin/project_request.html', context)


def projectRequestDetail(request, id):
    quotation_items =[
        {'name': 'Building Material', 'price':'20,000'},
        {'name': 'Rentals', 'price':'5000'},
        {'name': 'Cleaning', 'price':'8000'},
        {'name': 'Cleaning', 'price':'8000'},
        {'name': 'Labour', 'price':'10,000'},
    ]
    context ={'quotation_items':quotation_items}
    return render(request, 'admin/project_request_detail.html', context)