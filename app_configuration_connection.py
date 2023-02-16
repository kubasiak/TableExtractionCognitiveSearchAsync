
from azure.appconfiguration.provider import (
    AzureAppConfigurationProvider,
    SettingSelector
)
import os
def colorprint(txt,opt="93",end='\n'): 
    #print(f'\033[{opt}m',txt,'\033[0m',end=end)

    print(u"\u001b[38;5;"+opt+'m'+txt+u"\u001b[0m",end=end)
   
    
connection_string = "Endpoint=https://frasync.azconfig.io;Id=vaEf-l9-s0:WatzRuoRDKdhxw7Bf/0+;Secret=wuTPgs1ta1ALt2v4vpoMO+kGAAfY2kpd+yJD34BR2eU="   
       

# Connect to Azure App Configuration using a connection string.
config = AzureAppConfigurationProvider.load(
    connection_string=connection_string)
cf= dict(config)

# Find the key "message" and print its value.
#colorprint(str(cf),'91')

for k in cf:
    colorprint(k + ' : '+cf[k][0:5] + '...')

# Find the key "my_json" and print the value for "key" from the dictionary.


# Connect to Azure App Configuration using a connection string and trimmed key prefixes.
trimmed = {"test."}
config = AzureAppConfigurationProvider.load(
    connection_string=connection_string, trimmed_key_prefixes=trimmed)
# From the keys with trimmed prefixes, find a key with "message" and print its value.
#print(config["model"])

# Connect to Azure App Configuration using SettingSelector.
#selects = {SettingSelector("message*", "\0")}
#config = AzureAppConfigurationProvider.load(
#    connection_string=connection_string, selects=selects)

# Print True or False to indicate if "message" is found in Azure App Configuration.
#print("message found: " + str("message" in config))
#print("test.message found: " + str("test.message" in config))