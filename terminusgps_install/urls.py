from django.urls import path

from . import views

app_name = "install"
urlpatterns = [
    path("", views.InstallerDashboardView.as_view(), name="dashboard"),
    path("scan-vin/", views.VinNumberScanView.as_view(), name="scan vin"),
    path(
        "scan-vin/success/",
        views.VinNumberScanSuccessView.as_view(),
        name="scan vin success",
    ),
    path("assets/create/", views.WialonAssetCreateView.as_view(), name="create asset"),
]
