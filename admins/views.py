from django.shortcuts import render
from quotes.models import Project, QuoteRequest, QuoteRequestStatus
from django.core.paginator import Paginator


# Create your views here.
def projectRequest(request):
    project_history = QuoteRequest.objects.all()
    paginator = Paginator(project_history, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'project_history': project_history,
        'page_obj': page_obj
    }
    return render(request, 'user_admin/project_request.html', context)


def projectRequestDetail(request, id):
    quote_request = QuoteRequest.objects.get(id=id)

    if request.method == "POST":
        decision = request.POST.get('decision')
        if decision == "accept":
            pdf = request.FILES['pdf']
            Project.objects.create(
                admin=request.user,
                quote_request=quote_request,
                file=pdf,
                is_approved=True
            )
            quote_request.status = QuoteRequestStatus.approved
            quote_request.save(update_fields=['status'])

        else:
            quote_request.status = QuoteRequestStatus.rejected
            quote_request.save(update_fields=['status'])
    quotation_items = [
        {'name': 'Building Material', 'price': '20,000'},
        {'name': 'Rentals', 'price': '5000'},
        {'name': 'Cleaning', 'price': '8000'},
        {'name': 'Cleaning', 'price': '8000'},
        {'name': 'Labour', 'price': '10,000'},
    ]
    quotation_history = [
        {'date': 'Jan 16, 2024', 'contractor_name': 'Olivia Rhye', 'price': '$43,000', 'status': 'pending'},
        {'date': 'Jan 16, 2024', 'contractor_name': 'Olivia Rhye', 'price': '$43,000', 'status': 'pending'},
        {'date': 'Jan 16, 2024', 'contractor_name': 'Olivia Rhye', 'price': '$43,000', 'status': 'pending'},
    ]
    quotation_history_length = len(quotation_history)
    # Quotation history length greater than 0 will change the UI under quotations history, defaulted to 0 at the beginning
    context = {'quotation_items': quotation_items, 'quotation_history_length': 0,
               'quotation_history': quotation_history, 'quote_request': quote_request}
    return render(request, 'user_admin/project_request_detail.html', context)
