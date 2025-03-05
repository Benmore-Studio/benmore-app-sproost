from django.contrib import admin
from django.utils.html import format_html
from .models import QuoteRequest, Project, Property, QuoteRequestStatus

class StatusFilter(admin.SimpleListFilter):
    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        """Defines the filter options."""
        return [
            (QuoteRequestStatus.pending, "Pending"),
            (QuoteRequestStatus.returned, "Returned"),
            (QuoteRequestStatus.accepted, "Accepted"),
            (QuoteRequestStatus.rejected, "Rejected"),
        ]

    def queryset(self, request, queryset):
        """Filters the queryset based on the selected option."""
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "is_quote", "upload_date")
    list_filter = (StatusFilter, "is_quote", "upload_date")  # Custom filter added
    search_fields = ("title", "user__email")
    ordering = ("-upload_date",)




class ProjectAdmin(admin.ModelAdmin):
    list_display = ('quote_request_title', 'admin', 'is_approved', 'file_link', 'upload_date')
    # list_filter = ('is_approved', 'quote_request__status')
    list_filter = ('is_approved',)
    search_fields = ('quote_request__title', 'admin__username')
    readonly_fields = ('upload_date',)

    def quote_request_title(self, obj):
        return obj.quote_request.title
    quote_request_title.short_description = 'Quote Request Title'

    def file_link(self, obj):
        if obj.file:
            return format_html("<a href='{0}' target='_blank'>Download</a>", obj.file.url)
        return "No file"
    file_link.short_description = 'File Link'

    def upload_date(self, obj):
        return obj.quote_request.upload_date
    upload_date.short_description = 'Upload Date'

# Register your models here
admin.site.register(QuoteRequest, QuoteRequestAdmin)
# admin.site.register(Project, ProjectAdmin)
admin.site.register(Property)
