from django import forms

from locations.models import Location


class ForecastForm(forms.Form):
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        empty_label="Оберіть об'єкт для прогнозування",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Об'єкт"
    )
    forecast_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Початок"
    )
    forecast_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Кінець"
    )


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="Оберіть необхідний файл",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )


class ModelTrainingForm(forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), label="Місцезнаходження")

