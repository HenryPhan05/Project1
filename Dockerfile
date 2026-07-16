FROM mcr.microsoft.com/azure-functions/python:4-python3.9

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

RUN pip install azure-functions pandas matplotlib seaborn azure-storage-blob

COPY ./AzureFunction /home/site/wwwroot
