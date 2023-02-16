# TableExtractionCognitiveSearchAsync

This repository is integrating Azure Cognigive Form Recognizer with Azure Cognitive Search in asyncronous process. 
For it to work you need:
  - Azure search and its credentials
  - Azure search index/skillset/indexer in the format that is compatible with the output of the pipeline (tbc)
  - Azure storage with data to be processed
  - Azure Service Bus - Two queues named "polling_queue" and "results_queue" and their credentials
  - Azure Form Recognizer, and credentials
  - VSC and Azure addon with Azure Functions and Azure Core tools
  - Its useful to have Postman or other tool for testing and debugging purposes, but it's not necessary
  
  You will need to update Setting -> Configuration of your web app adding env variables:
  '''
   "AZURE_WEB_JOB_STORAGE":"<your connection string>",
   "AZURE_SERVICE_BUS_CONNECTION_STRING": "<your connection string>",
   "AZURE_FORM_RECOGNIZER_ENDPOINT": "<https:...>",
   "AZURE_FORM_RECOGNIZER_ENDPOINT_KEY": "<primary key>",
   "AZURE_SEARCH_ENDPOINT": "<https:...>",
   "AZURE_SEARCH_ENDPOINT_KEY": "<primary key>",
   "AZURE_SEARCH_INDEX_NAME": "<your index name>",
   "MODEL":"prebuilt-layout" OR  "invoice"
     
'''  
