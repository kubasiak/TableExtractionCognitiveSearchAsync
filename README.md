# TableExtractionCognitiveSearchAsync

This repository is integrating Azure Cognigive Form Recognizer with Azure Cognitive Search in asyncronous process. 
For it to work you need:
  - Azure search and its credentials
  - Azure search index/skillset/indexer in the format that is compatible with the output of the pipeline (below)
  - Azure storage with data to be processed
  - Azure Service Bus - Two queues named "polling_queue" and "results_queue" and their credentials
  - Azure Form Recognizer, and credentials
  - Create Azure Function app (python) 
  - VSC and Azure addon with Azure Functions and Azure Core tools
  - Its useful to have Postman or other tool for testing and debugging purposes, but it's not necessary
  
  
  You will need to update Setting -> Configuration of your function app adding env variables:
  
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
     

git clone this repository
  go to left hand side panel in VSC and find Azure.
  Log in to Azure.
  Find "workspaces" menu and deploy to Azure button: 
  
 <img src="https://user-images.githubusercontent.com/7407845/219422590-b5e02841-8d8d-493f-b391-fc2ab936e284.png"  width="30%" >
  Follow the instructions to deploy your functions to the app. It should create 3 functions in your Azure Function app 
  * Start_processing
  * Fetch_results
  * Push_results
  
  
  To include the function in your azure search index you need to add the skill to skillset: 
  Here is an example of how it can look like:
  
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
                }
            ]
        }
