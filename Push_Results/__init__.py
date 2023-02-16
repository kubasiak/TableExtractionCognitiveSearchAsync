import logging, json, os, requests, datetime
import azure.functions as func
#from process_data import *
def process_invoice(data):
    results={}
    for k, v in data['results']['analyzeResult']['documents'][0]['fields'].items():
        if v['type'] != 'array': # TO DO - Implement Array Processing and better type handling
            results['value'][k] = v['content']
    return(results)
 

def process_tables(data):

    tables=[]
    
   # tables.append({'raw content': data['results']['analyzeResult']['content'] })
    
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
                    
                tmptable =   {
                    "page_number": pageNumber,
                    "raw_count" : table['rowCount'],
                    "column_count": table['columnCount'],
                    "headers": headers,
                    "cells": cells,
                    "raw_text":raw_text
                }  

                tables.append(str(tmptable))
                h=len(headers)
    #results['value']['data']=tables
    #results['value']=tables
    #results['value'].append(data['results']['analyzeResult']['content'])
    #results['content']= {"content":data['results']['analyzeResult']['content']}
    return(tables)

def main(msg: func.ServiceBusMessage):
    #model= os.environ['MODEL']
    # Push the results to Azure Cognitive Search
    data = json.loads(msg.get_body().decode('utf-8'))
    logging.info(f"PUSH RESULTS DATA LOADED FROM MSG BODY {data.keys()}") #keys?
    model = data['model']

    results = {  
        "value": [  
            {  
                "@search.action": "merge",  
                "metadata_storage_path": data['key'] #key = metadata_storage_path 
            }  
        ]  
    }


    if model=='prebuilt-layout':
        processed_data=process_tables(data)
        fieldname='tables'

    if model == 'prebuilt-invoice':
        processed_data = process_invoice(data)
        fieldname='invoice'
    
    logging.info("processed_data: "+str(processed_data))
    results['value'][0][fieldname]=processed_data
    
    # Push data on Azure Cognitive Search
    search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    search_key = os.environ["AZURE_SEARCH_ENDPOINT_KEY"]
    index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
    service_bus_conn_str = os.environ["AZURE_SERVICE_BUS_CONNECTION_STRING"]
    headers = {'Content-Type': 'application/json', 'api-key': search_key}
    search_url = search_endpoint + f"/indexes/{index_name}/docs/index?api-version=2019-05-06"
    r = requests.post(search_endpoint + f"/indexes/{index_name}/docs/index?api-version=2019-05-06", 
                        headers=headers, json=results)
    logging.info(f"PUSHED RESULTS TO INDEX {index_name}")
    logging.info(f"headers: {str(headers)}")
    logging.info(f"search url: {str(search_url)}")
    logging.info("JSON pushed to SEARCH "+str(results))
    logging.info(str(r))
    # Check r status code
    if r.status_code == 207:
        # Document not present in the Search Index. Retry in a while
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=service_bus_conn_str, logging_enable=True)
        with servicebus_client:
            sender = servicebus_client.get_queue_sender(queue_name="results_queue", scheduled_enqueue_time_utc=datetime.datetime.utcnow() + datetime.timedelta(seconds=10))
            with sender:
                sender.send_messages(ServiceBusMessage(json.dumps(data)))