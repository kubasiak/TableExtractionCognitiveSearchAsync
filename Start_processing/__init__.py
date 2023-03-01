import logging, json, os, requests
import azure.functions as func

def main(req: func.HttpRequest, msg: func.Out[str]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        body = json.dumps(req.get_json())
        body = req.get_json()
        logging.info(f"body from input request below")
        logging.info(body)

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
    try:
        values = json.loads(json_data)['values'] 
    except:
        logging.error("type json_data ")
        values = json_data['values']
    # Prepare the Output before the loop
    results = {}
    results["values"] = []
    try:
        for value in values:
            output_record = transform_value(value, msg)
            logging.info(f"output_record {output_record}")
            if output_record != None:
                results["values"].append(output_record)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        logging.error(e)

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
        assert ( 'metadata_storage_path' in data), "'metadata_storage_path' field is required in 'data' object."
        assert ('metadata_storage_path_decoded' in data), "'metadata_storage_path_decoded' field is required in 'data' object."
        assert ('metadata_storage_sas_token' in data), "'metadata_storage_sas_token ' field is required in 'data' object."
    except AssertionError  as error:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Error:" + error.args[0] }   ]       
            })
    
    try:
        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT_KEY"]
        model = os.environ["MODEL"]
    except Exception as e:
        return (
            {
            "recordId": recordId,
            "errors":[{"message":f"missing env variables {e}, {e.args[0]}"}]
            })    

    try:  
        logging.info(f"data FROM FR INPUT: {data}")
        
        output = {
            "key": data['metadata_storage_path'],
            "metadata_file_path": data['metadata_storage_path_decoded'] + data['metadata_storage_sas_token'],
            "model": model
        }  
    
        # Request to Azure Form Recognizer Model
        form_recognizer_url = f"{endpoint}formrecognizer/documentModels/{output['model']}:analyze?api-version=2022-08-31"
        headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": key}
        body = {'urlSource': output['metadata_file_path']} 
        
        r = requests.post(form_recognizer_url, headers=headers, json=body)
        output['Operation-location'] = r.headers['Operation-Location']
        msg.set(json.dumps(output))
        logging.info(f"output PASSED TO SERVICE BUS from Start_processing function {str(output)}")

    except Exception as e:
        logging.error(f"error: {e}")

        return (
            {
            "recordId": recordId,
            "errors": [ { "message": f"Could not complete operation for record. {e} body: {str(body)}form_recognizer_url: {str(form_recognizer_url)}" }
              ]    
            })

    return ({
            "recordId": recordId,
            "data": {
                "status": "Document added to queue",
                "Operation-location":output['Operation-location'],
                "File":data['metadata_storage_path_decoded']
                    }
            })