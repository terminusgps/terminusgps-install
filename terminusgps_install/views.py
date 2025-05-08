import typing

from django.forms import Form, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from PIL import Image
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.django.utils import scan_barcode
from terminusgps.wialon.constants import WialonProfileField
from terminusgps.wialon.items import WialonResource
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_unit_by_imei

from .forms import VinNumberScanForm, WialonAssetCreateForm
from .models import Installer, WialonAccount


class InstallerDashboardView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": None,
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_install/partials/_dashboard.html"
    template_name = "terminusgps_install/dashboard.html"


class VinNumberScanView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Scan VIN #",
        "subtitle": None,
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps_install/scan_vin.html"
    partial_template_name = "terminusgps_install/partials/_scan_vin.html"
    form_class = VinNumberScanForm
    success_url = reverse_lazy("install:scan vin success")

    def form_valid(
        self, form: VinNumberScanForm
    ) -> HttpResponse | HttpResponseRedirect:
        img = Image.open(form.cleaned_data["image"].file)
        results = scan_barcode(img)
        if not results:
            form.add_error(
                "image",
                ValidationError(
                    _(
                        "Whoops! No barcode was detected in the uploaded image. Please upload a new image."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)

        extracted_vin: str = results[0].data.decode("utf-8")
        return HttpResponseRedirect(self.get_success_url(extracted_vin))

    def get_success_url(self, vin_number: str | None = None) -> str:
        if vin_number is not None:
            return f"{super().get_success_url()}?vin={vin_number}"
        return super().get_success_url()


class VinNumberScanSuccessView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "VIN # Scanned",
        "subtitle": None,
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    template_name = "terminusgps_install/scan_vin_success.html"
    partial_template_name = "terminusgps_install/partials/_scan_vin_success.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["vin_number"] = self.request.GET.get("vin", "")
        return context


class WialonAssetCreateView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Create Asset",
        "subtitle": None,
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps_install/create_asset.html"
    partial_template_name = "terminusgps_install/partials/_create_asset.html"
    form_class = WialonAssetCreateForm
    success_url = reverse_lazy("install:dashboard")

    def get_installer(self) -> Installer | None:
        if self.request.user and self.request.user.is_authenticated:
            installer, _ = Installer.objects.get_or_create(user=self.request.user)
            return installer

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["vin_number"] = self.request.GET.get("vin")
        return initial

    def get_form(self, form_class=None) -> Form:
        accounts = WialonAccount.objects.filter(installers=self.get_installer())
        form: Form = super().get_form(form_class=form_class)
        form.fields["account"].choices = accounts.order_by("name").values_list(
            "pk", "name"
        )
        return form

    def form_valid(self, form: Form) -> HttpResponse | HttpResponseRedirect:
        imei_number = str(form.cleaned_data["imei_number"])
        vin_number = str(form.cleaned_data["vin_number"])
        account_id = str(form.cleaned_data["account"].id)

        with WialonSession() as session:
            unit = get_unit_by_imei(imei_number, session=session)
            resource = WialonResource(account_id, session=session)

            if not unit:
                form.add_error(
                    "imei_number",
                    ValidationError(
                        _(
                            "Whoops! Couldn't find a Wialon unit with IMEI # '%(imei_number)s'."
                        ),
                        code="invalid",
                        params={"imei_number": imei_number},
                    ),
                )
                return self.form_invalid(form=form)
            if not resource.is_account:
                form.add_error(
                    "account",
                    ValidationError(
                        _("Whoops! The Wialon resource '%(name)s' isn't an account."),
                        code="invalid",
                        params={"name": resource.name},
                    ),
                )

            unit.update_pfield(key=WialonProfileField.VIN, value=vin_number)
            resource.migrate_unit(unit)
            return HttpResponseRedirect(self.get_success_url())
