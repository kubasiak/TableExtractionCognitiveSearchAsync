import logging, json, os, requests
import azure.functions as func

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
        assert ('metadata_storage_path_decoded' in data), "'metadata_storage_path_decoded' field is required in 'data' object."
        assert ('metadata_storage_sas_token' in data), "'metadata_storage_sas_token ' field is required in 'data' object."
    except AssertionError  as error:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Error:" + error.args[0] }   ]       
            })

    try:        
        output = {
            "key": data['metadata_storage_path'],
            "file_path": data['metadata_storage_path_decoded'] + data['metadata_storage_sas_token'],
            "model": "prebuilt-layout"
        }        
        # Request to Azure Form Recognizer Model
        form_recognizer_url = f"{os.getenv('AzureFormRecognizerEndpoint')}formrecognizer/documentModels/{output['model']}:analyze?api-version=2022-08-31"
        headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": os.getenv('AzureFormRecognizerEndpointKey')}
        body = {'urlSource': output['file_path']}
        r = requests.post(form_recognizer_url, headers=headers, json=body)
        output['Operation-location'] = r.headers['Operation-Location']
        msg.set(json.dumps(output))


    except Exception as e:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": f"Could not complete operation for record. {e}" }   ]       
            })

    return ({
            "recordId": recordId,
            "data": {
                "status": "Document added to queue"
                    }
            })