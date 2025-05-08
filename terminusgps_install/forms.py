from django import forms
from django.core.validators import validate_image_file_extension

from terminusgps_install.models import WialonAccount


class VinNumberScanForm(forms.Form):
    image = forms.ImageField(
        label="Upload Image",
        allow_empty_file=False,
        validators=[validate_image_file_extension],
        widget=forms.widgets.FileInput(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-gray-300"
            }
        ),
    )


class WialonAssetCreateForm(forms.Form):
    vin_number = forms.CharField(
        label="VIN #",
        max_length=17,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-gray-300",
                "placeholder": "AA0AAAA0AAA000000",
            }
        ),
    )
    imei_number = forms.CharField(
        label="IMEI #",
        max_length=19,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-gray-300",
                "placeholder": "867730050855555",
            }
        ),
    )
    account = forms.ModelChoiceField(
        label="Wialon Account",
        queryset=WialonAccount.objects.all(),
        widget=forms.widgets.Select(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-gray-300",
            }
        ),
    )
