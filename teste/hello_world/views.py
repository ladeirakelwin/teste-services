from django.http import HttpResponse
from django.views import View
import json

class HelloWorldView(View):
    def get(self, request, *args, **kwargs):
        msg = "Hello World!"
        return HttpResponse(msg)

# Create your views here.
