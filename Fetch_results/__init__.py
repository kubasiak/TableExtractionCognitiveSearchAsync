import logging, json, os, requests, datetime
import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage

def main(msgin: func.ServiceBusMessage):
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 msgin.get_body().decode('utf-8'))

    # Use the REST API to get Form Recognizer output and save it to Azure Service Bus
    data = json.loads(msgin.get_body().decode('utf-8'))
    r = requests.get(data['Operation-location'], headers={'Ocp-Apim-Subscription-Key': os.getenv('AZURE_FORM_RECOGNIZER_ENDPOINT_KEY')})
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING'), logging_enable=True)
    if r.json()['status'] == 'succeeded':
        data['results'] = r.json()
        with servicebus_client:
            sender = servicebus_client.get_queue_sender(queue_name="results_queue")
            with sender:
                sender.send_messages(ServiceBusMessage(json.dumps(data)))

    elif r.json()['status'] in ('notStarted', 'running'):
        with servicebus_client:
            sender = servicebus_client.get_queue_sender(queue_name="polling_queue")
            with sender:
                sender.send_messages(ServiceBusMessage(json.dumps(data), scheduled_enqueue_time_utc=datetime.datetime.utcnow() + datetime.timedelta(seconds=10)))
