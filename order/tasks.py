from .models import Order
from django.utils import timezone
from celery import shared_task

@shared_task
def check_expired_order():
    print("chacking expired order")
    today = timezone.now().date()
    orders = Order.objects.all()
    for order in orders:
        expired = today > order.estimated_delivery_date
        if order.over_due != expired:
            order.over_due = expired
            order.save()
    return "Expired orders checked"