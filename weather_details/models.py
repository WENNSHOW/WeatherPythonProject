# from django.db import models

# class Region(models.Model):
#     """
#     Модель для хранения информации о регионе (городе), для которого предоставляются данные о погоде.
#     """
#     city_name = models.CharField(max_length=100, verbose_name="Название города")
#     latitude = models.FloatField(verbose_name="Широта")
#     longitude = models.FloatField(verbose_name="Долгота")

#     def __str__(self):
#         return self.city_name

# class Weather(models.Model):
#     """
#     Модель для хранения погодных данных, включая прогнозы на текущий день и на 3 дня вперед.
#     """
#     region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="weather_reports", verbose_name="Регион")
#     forecast_date = models.DateField(verbose_name="Дата прогноза")
#     min_temperature = models.FloatField(verbose_name="Минимальная температура")
#     max_temperature = models.FloatField(verbose_name="Максимальная температура")
#     precipitation = models.FloatField(verbose_name="Количество осадков")
#     humidity = models.PositiveIntegerField(verbose_name="Влажность, %")
#     description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Описание погодных условий")

#     def __str__(self):
#         return f"{self.region.city_name} - {self.forecast_date}"

