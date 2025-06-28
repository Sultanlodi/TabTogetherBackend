# TapTogetherBackend/bills_api/urls.py

from django.urls import path
from .views import BillUploadView, BillDetailView # Make sure these views are imported

urlpatterns = [
    # URL for uploading bills (e.g., POST to /api/bills/upload/)
    path('bills/upload/', BillUploadView.as_view(), name='bill-upload'),

    # URL for retrieving a specific bill by its ID (e.g., GET to /api/bills/1/)
    path('bills/<int:pk>/', BillDetailView.as_view(), name='bill-detail'),

    # You can add more API endpoints here later, e.g., for splitting logic, etc.
]