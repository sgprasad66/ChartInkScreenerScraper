import pika, json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import ssl 

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

params = pika.URLParameters('amqp://endnpqyd:lFusCAGdoGWor8Ro6RffeopDcZambQ05@albatross.rmq.cloudamqp.com/endnpqyd')

connection = pika.BlockingConnection(params)

channel = connection.channel()


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='main', body=json.dumps(body), properties=properties)