from .models import HeadQuarter

def main_warehouse_processor(request):
    a = HeadQuarter.objects.filter(primary=True)
    return {'main_warehouse': a.first() if a else None}