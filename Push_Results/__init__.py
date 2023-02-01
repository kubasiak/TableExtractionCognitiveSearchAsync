import logging, json, os, requests, datetime
import azure.functions as func


def main(msg: func.ServiceBusMessage):
    # Push the results to Azure Cognitive Search
    data = json.loads(msg.get_body().decode('utf-8'))

    results = {  
        "value": [  
            {  
                "@search.action": "merge",  
                "metadata_storage_path": data['metadata_storage_path']
            }  
        ]  
    }
   # for k, v in data['results']['analyzeResult']['documents'][0]['fields'].items():
   #     if v['type'] != 'array': # TO DO - Implement Array Processing and better type handling
   #         results['value'][k] = v['content']
        
    tables=[]
    if 'tables' in data['results']['analyzeResult'].keys():
        res=data['results']['analyzeResult']['tables']
        for table in res:
            raw_text=[]
            cells = []
            headers=[]
            regions=table['boundingRegions']
            for r in regions: pageNumber = r['pageNumber']
            for cell in table['cells']:
                cells.append(
                {
                    "text": cell['content'],
                    "rowIndex": cell['rowIndex'],
                    "colIndex": cell['columnIndex'],
                    #"confidence": '',
                    "is_header": False
                })
                isheader=False
                if ('kind' in cell.keys() ): 
                    isheader = (cell['kind']=='columnHeader')
                    cells.append({'is_header': isheader})
                    if isheader: 
                        headers.append(cell['content'])
                if not isheader: 
                    raw_text.append(cell['content'])


            tables.append({
                "page_number": pageNumber,
                "raw_count" : table['rowCount'],
                "column_count": table['columnCount'],
                "headers": headers,
                "cells": cells,
                "raw_text":raw_text
            }
            )
            h=len(headers)
            #df = pd.DataFrame([raw_text[i:i+h] for i in range(0, len(raw_text), h)],columns=headers)   
        logging.info(results)

    # Push data on Azure Cognitive Search
    headers = {'Content-Type': 'application/json', 'api-key': os.getenv('AzureSearchEndpointKey')}
    r = requests.post(os.getenv('AzureSearchEndpoint') + f"/indexes/{os.getenv('AzureSearchIndexName')}/docs/index?api-version=2019-05-06", headers=headers, json=results)

    # Check r status code
    if r.status_code == 207:
        # Document not present in the Search Index. Retry in a while
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=os.getenv('AzureServiceBusConnectionString'), logging_enable=True)
        with servicebus_client:
            sender = servicebus_client.get_queue_sender(queue_name="results_queue", scheduled_enqueue_time_utc=datetime.datetime.utcnow() + datetime.timedelta(seconds=10))
            with sender:
                sender.send_messages(ServiceBusMessage(json.dumps(data)))