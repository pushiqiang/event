from django.urls import path

from .views import TestKafkaView, TestRabbitmqView, TestRedisView, TestView

urlpatterns = [
    path('', TestView.as_view(), name='django_test'),
    path('redis', TestRedisView.as_view(), name='django_redis_test'),
    path('kafka', TestKafkaView.as_view(), name='django_redis_test'),
    path('rabbitmq', TestRabbitmqView.as_view(), name='django_rabbitmq_test'),
]
