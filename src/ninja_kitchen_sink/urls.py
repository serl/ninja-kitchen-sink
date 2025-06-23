from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI

api = NinjaAPI()


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}


api.add_router("/polls/", "ninja_kitchen_sink.polls.ninja_api.router")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ninja-api/", api.urls),
    path("drf-api/polls/", include("ninja_kitchen_sink.polls.drf_api")),
]
