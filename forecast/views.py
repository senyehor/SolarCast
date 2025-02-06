from urllib.parse import quote

from django.http import HttpResponse
from django.shortcuts import render
from openpyxl.workbook import Workbook

from .forecasting import Forecaster
from .forms import ForecastForm, ModelTrainingForm
from .utils import create_model_for_location


def forecast_request_view(request):
    if request.method == "POST":
        form = ForecastForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']
            forecast_start_date = form.cleaned_data['forecast_start_date']
            forecast_end_date = form.cleaned_data['forecast_end_date']
            forecaster = Forecaster(location, forecast_start_date, forecast_end_date)
            data = forecaster.get_forecast()
            if request.POST.get('action') == 'get_report':
                return render(
                    request, 'forecast/main_page.html', {'form': form, 'forecast_data': data}
                )
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "Прогноз генерації"
            worksheet.append(["Час", "Прогнозована генерація (кВт·год)"])

            for record in data:
                worksheet.append([record[0], record[1]])

            worksheet.column_dimensions['A'].width = 20
            worksheet.column_dimensions['B'].width = 20

            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response[
                'Content-Disposition'] = f'attachment; filename={quote(f"звіт_генерації_для_{location.name}_від_{forecast_start_date}_до_{forecast_end_date}")}.xlsx'
            workbook.save(response)
            return response
    else:
        form = ForecastForm()

    return render(request, "forecast/main_page.html", {"form": form})


def train_model_view(request):
    if request.method == 'POST':
        form = ModelTrainingForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']
            mae, mse = create_model_for_location(location)
            return render(request, 'train_result.html', {'mae': mae, 'mse': mse})
    else:
        form = ModelTrainingForm()
    return render(request, 'train_model.html', {'form': form})

