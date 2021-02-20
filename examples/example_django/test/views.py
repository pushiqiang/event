# -*- coding: utf-8 -*-
from django.shortcuts import HttpResponse
from django.views import View

from example.event_manager import manager


class TestView(View):
    def get(self, request, *args, **kwargs):
        redis_server = manager.get_server('redis')
        kafka_server = manager.get_server('kafka')
        rabbitmq_server = manager.get_server('rabbitmq')
        redis_server.publish_soon(channel='example:test:django',
                                  message={
                                      'test_id': 'redis_id',
                                      'message': 'redis good'
                                  })
        kafka_server.publish_soon(topic='example-test-django',
                                  message={
                                      'test_id': 'kafka_id',
                                      'message': 'kafka good'
                                  })
        rabbitmq_server.publish_soon(routing_key='example:test:django',
                                     message={
                                         'test_id': 'rabbitmq_id',
                                         'message': 'rabbitmq good'
                                     })

        return HttpResponse('good')


class TestRedisView(View):
    def get(self, request, *args, **kwargs):
        server = manager.get_server('redis')
        server.publish_soon(channel='example:test:django',
                            message={
                                'test_id': 'redis_id',
                                'message': 'redis good'
                            })

        return HttpResponse('redis good')


class TestKafkaView(View):
    def get(self, request, *args, **kwargs):
        server = manager.get_server('kafka')
        server.publish_soon(topic='example-test-django',
                            message={
                                'test_id': 'kafka_id',
                                'message': 'kafka good'
                            })

        return HttpResponse('kafka good')


class TestRabbitmqView(View):
    def get(self, request, *args, **kwargs):
        server = manager.get_server('rabbitmq')
        server.publish_soon(routing_key='example:test:django',
                            message={
                                'test_id': 'rabbitmq_id',
                                'message': 'rabbitmq good'
                            })

        return HttpResponse('rabbitmq good')
