from django.contrib import admin
from django.urls import path

from minimizer.views import index, solution

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('solution/', solution, name='solution')
]
