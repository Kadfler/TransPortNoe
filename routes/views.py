from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Route

@login_required
def route_geometry_api(request, route_id):
    """
    API endpoint, отдающий координаты точек А и Б для карты на фронтенде.
    """
    route = get_object_or_404(Route, id=route_id)
    data = {
        "id": route.id,
        "distance_km": route.distance_km,
        "start": {"lat": route.loading_lat, "lon": route.loading_lon, "address": route.loading_address},
        "end": {"lat": route.unloading_lat, "lon": route.unloading_lon, "address": route.unloading_address},
    }
    return JsonResponse(data)