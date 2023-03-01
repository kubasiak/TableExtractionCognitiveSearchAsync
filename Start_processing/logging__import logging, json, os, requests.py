import logging, json, os, requests
import azure.functions as func
from azure.appconfiguration.provider import (
    AzureAppConfigurationProvider,
    SettingSelector
)

def main(req: func.HttpRequest, msg: func.Out[str]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        body = json.dumps(req.get_json())
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
    if body:
        # Connect to Azure App Configuration using a connection string.
        result = compose_response(body, msg)
        return func.HttpResponse(result, mimetype="application/json")
    else:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )

def compose_response(json_data, msg):
    values = json.loads(json_data)['values'] 
    # Prepare the Output before the loop
    results = {}
    results["values"] = []
    
    for value in values:
        output_record = transform_value(value, msg)
        if output_record != None:
            results["values"].append(output_record)
    return json.dumps(results, ensure_ascii=False)

## Perform an operation on a record
def transform_value(value, msg):
    try:
        recordId = value['recordId']
    except AssertionError  as error:
        return None

    # Validate the inputs
    try:         
        assert ('data' in value), "'data' field is required."
        data = value['data']        
        assert ('metadata_storage_path' in data), "'metadata_storage_path' field is required in 'data' object."
        assert ('formUrl' in data), "'formUrl' field is required in 'data' object."
        
        form_url = data["formUrl"] 
        metadata_storage_path = data['metadata_storage_pat']

        assert (type(form_url)==str), f"form_url invalid {str(form_url)}"
        #assert ('metadata_storage_path_decoded' in data), "'metadata_storage_path_decoded' field is required in 'data' object."
        #assert ('metadata_storage_sas_token' in data), "'metadata_storage_sas_token ' field is required in 'data' object."
    except AssertionError  as error:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Error:" + error.args[0] }   ]       
            })
    
    try:
        #appsettings_connection_string =os.getenv('AZURE_APPCONFIG_CONNECTION_STRING')
        #appsettings_connection_string = os.environ["AZURE_APPCONFIG_CONNECTION_STRING"]
        appsettings_connection_string = "Endpoint=https://frasync.azconfig.io;Id=vaEf-l9-s0:WatzRuoRDKdhxw7Bf/0+;Secret=wuTPgs1ta1ALt2v4vpoMO+kGAAfY2kpd+yJD34BR2eU="
        config = AzureAppConfigurationProvider.load(connection_string=appsettings_connection_string)
        cf= dict(config)
        endpoint = cf["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = cf["AZURE_FORM_RECOGNIZER_ENDPOINT_KEY"]
        model = cf["MODEL"]
    except Exception as e:
        #logging.error(e)
        return (
            {
            "recordId": recordId,
            "errors":[{"message":f"missing env variables {e}, {e.args[0]}"}]
            })    
    
    
    try:
        assert (type(endpoint)==str), "'endpoint' variable is required "
        assert(type(key)==str), "'key' variable is requred"
        assert(type(model)==str), "'model' variable is required"
    except AssertionError as e:
        #logging.error(e)
        return({
            "recordId": recordId,
            "errors":[{"message":f"missing values {e}, {e.args[0]} "}]
            }) 
            
    body='no body'
    form_recognizer_url = 'no url'
    
    
    try:  
        output = {
            "key": metadata_storage_path,
            "formUrl":form_url,
            #"file_path": data['metadata_storage_path_decoded'] + data['metadata_storage_sas_token'],
            "file_path": form_url+ metadata_storage_path,
            "model": model
        }  
        #logging.info(f"output 1 {output}")
        # Request to Azure Form Recognizer Model
        form_recognizer_url = f"{endpoint}formrecognizer/documentModels/{output['model']}:analyze?api-version=2022-08-31"
        headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": key}
        body = {'urlSource': output['file_path']}
        #body = {'urlSource': output['formUrl']}
        
        r = requests.post(form_recognizer_url, headers=headers, json=body)
        output['Operation-location'] = r.headers['Operation-Location']
        #logging.info(f"output 2 {output}")

        msg.set(json.dumps(output))


    except Exception as e:
        #logging.error(e)
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": f"Could not complete operation for record. {e} body: {str(body)}form_recognizer_url: {str(form_recognizer_url)}" }
              ]    
            })

    return ({
            "recordId": recordId,
            "data": {
                "status": "Document added to queue"
                    }
            })