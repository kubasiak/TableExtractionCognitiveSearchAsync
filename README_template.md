---
page_type: sample
languages:
- python
products:
- azure
- azure-cognitive-search
- azure-cognitive-services
- azure-form-recognizer
- azure-service-bus
name: Analyze document asyncronously using the different Form Recognizer APIs in 
urlFragment: azure-formrecognizer-sample
description: This custom skill can extract OCR text, tables, and key value pairs from a document. 
---
Invoking a Form Recognizer capability within the Cognitive Search pipeline is now merged into a single skill.
* [Analyze Document](#AnalyzeDocument) and extract tables or invoice information content, using a pre built model or a custom model in an ASYNCROUNOUS way
Supported models include:
- Prebuilt models (No training required)
    - Invoices
    - Tables


# Deployment    

The analyze form skill enables you to use a pretrained model - in this case Layout model (This usecase can be extended to other type of models such as a custom model) to identify and extract key value pairs, and tables. 
In order to allow for async documents processing, also Azure Service Bus and it's credentials will be needed. In the Service Bus asset, deploy two queues - 'polling_queue' and 'results_queue'.
You will also need Azure Cognitive Search service setup and Storage Account with a container with your data uploaded. 



To deploy the skills:
1. In case you already have Azure Cognitive Search note the endpoint, key and index name (to be added to appsettings in your web app), Otherwise create them in the Azure Portal. 
2. Upload your documents to Azure Storage account and note the account name, key and container with the data. In case you don't have the Storage account create one in Azure Portal
3. In Azure Portal create Azure Service Bus namespace and two queues within it - 'polling_queue' and 'results_queue'. Nothe their credentials. They will be used for the asyncronous process.
4. In the Azure portal, create a Forms Recognizer resource. Note the form recognizer URL and key.
5. In Azure portal create Azure Function web app. 
6. Clone this repository.
7. Open the FormRecognizer folder in VS Code and deploy the function to your Azure Function app.
8. Once the function is deployed, set the required appsettings. You will need all noted before data to create environment variables (see below)
  On the Azure portal, these can be found in your Azure function in the "Configuration" page under the "Settings" section.  Add them as new Application settings.  See [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings?tabs=portal#settings) for further description.  
9. Add the skill to your skillset as [described below](#sample-skillset-integration)


The skill requires the following properties set in the appsettings.

  |Variable name|value|
  |-------------|------------|
  |"AZURE_WEB_JOB_STORAGE"|"<your connection string>",|
   "AZURE_WEB_JOB_STORAGE"|"<your connection string>",
   "AZURE_SERVICE_BUS_CONNECTION_STRING"| "<your connection string>",
   "AZURE_FORM_RECOGNIZER_ENDPOINT"| "<https:...>",
   "AZURE_FORM_RECOGNIZER_ENDPOINT_KEY"|: "<primary key>",
   "AZURE_SEARCH_ENDPOINT"| "<https:...>",
   "AZURE_SEARCH_ENDPOINT_KEY"| "<primary key>",
   "AZURE_SEARCH_INDEX_NAME"| "<your index name>",
   "MODEL"|"prebuilt-layout" OR  "invoice"
     
# AnalyzeDocument

This custom skill can invoke any of the following Form Recognizer APIs
1. Layout
2. Prebuilt invoice


## Sample Input:

This sample data is pointing to a file stored in this repository, but when the skill is integrated in a skillset, the URL and token will be provided by cognitive search.

```json
body = {
    "values": [
        {   "recordId": "record1",
            "data": { 
                "metadata_storage_path":"encoded_metadata_storage_path_generated_by_Cognitive_search",
                "metadata_storage_path_decoded":"https://github.com/Azure-Samples/azure-search-power-skills/raw/master/SampleData/Invoice_4.pdf",
                "metadata_storage_sas_token":"?st=sasTokenThatWillBeGeneratedByCognitiveSearch"
                }
        }
    ]
}
```

## Requirements

In addition to the common requirements described in [the root `README.md` file](../../README.md), this function requires access to an [Azure Form Recognizer](https://azure.microsoft.com/en-us/services/cognitive-services/form-recognizer/) resource. 

[Train a model with your forms](https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/build-training-data-set) if you plan to use the custom model. For any of the prebuilt models or general document model, no additional setup is required. 

## Settings

This function requires a `FORMS_RECOGNIZER_ENDPOINT` and a `FORMS_RECOGNIZER_KEY` settings set to a valid Azure Forms Recognizer API key and to your custom Form Recognizer 2.1-preview endpoint. 
If running locally, this can be set in your project's local environment variables. This ensures your key won't be accidentally checked in with your code.
If running in an Azure function, this can be set in the application settings.



## Sample Output:

```json
{
    "values": [
        {
            "recordId": "record1",
            "tables": ["","",""],
            "pipe_tables": ["","",""],
            "invoice": ["","",""],
        }
    ]
}
```




## Sample Skillset Integration:

In order to use this skill in a cognitive search pipeline, you'll need to add a skill definition to your skillset.
Here's a sample skill definition for this example (inputs and outputs should be updated to reflect your particular scenario and skillset environment):

```json
{
    "@odata.type":"#Microsoft.Skills.Custom.WebApiSkill",
    "name":"formrecognizer-tables",
    "description":"Analyze documents and extracts tables.",
    "uri":"{{Async_table_extractor_url}}?code={{Async_table_extractor_key}}",
    "httpMethod":"POST",
    "timeout": "PT1M",
    "context":"/document",
    "batchSize":1,
    "inputs":[ 
                { 
                    "name":"metadata_storage_sas_token",
                    "source":"/document/metadata_storage_sas_token"
                },
                { 
                    "name":"metadata_storage_path",
                    "source":"/document/metadata_storage_path"
                },
                { 
                    "name":"metadata_storage_path_decoded",
                    "source":"/document/metadata_storage_path_decoded"
                }
            ],
            "outputs":[ 
                { 
                    "name":"tables",
                    "targetName":"tables"
                },
                {
                    "name":"pipe_tables",
                    "targetName":"pipe_tables"
                }
            ],
    "cognitiveServices": {
        "@odata.type": "#Microsoft.Azure.Search.DefaultCognitiveServices"
    }
}
```


