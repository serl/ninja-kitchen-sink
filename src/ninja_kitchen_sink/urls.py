from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI()


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}


api.add_router("/polls/", "ninja_kitchen_sink.polls.api.router")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
