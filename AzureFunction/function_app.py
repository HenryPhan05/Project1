import azure.functions as func
import pandas as pd
import os, json, time
from io import BytesIO
from azure.storage.blob import BlobServiceClient
import datetime
import logging

app = func.FunctionApp()

@app.route(route="GetDietAnalysis", auth_level=func.AuthLevel.ANONYMOUS)
def GetDietAnalysis(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()
    try:
        conn_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = "diet-analysis"
        blob_name = "All_Diets.csv"

        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        blob_client =  blob_service_client.get_blob_client(container = container_name, blob = blob_name)
        download_stream = blob_client.download_blob();

        df = pd.read_csv(BytesIO(download_stream.readall()))
        df.fillna(df.mean(numeric_only=True), inplace=True)

        # filer : ? diet_type =paleo
        diet_filter = req.params.get("diet_type")
        if(diet_filter):
            df = df[df["Diet_type"].str.lower() == diet_filter.lower()]
        
        avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().reset_index()
        top_protein = (df.sort_values("Protein(g)", ascending = False)).groupby("Diet_type").head(5)[["Diet_type", "Recipe_name", "Protein(g)"]]
        common_cuisine = df.groupby("Diet_type")["Cuisine_type"].agg(lambda x: x.mode()[0]).reset_index()

        # add 2 new metrics from phase 1 (protein-to-carbs, carbs-to-fat) to dashboard
        df["Protein_to_Carbs_ratio"] = df["Protein(g)"] / df["Carbs(g)"]
        df["Carbs_to_Fats_ratio"] = df["Carbs(g)"] / df["Fat(g)"]
        avg_ratios = df.groupby("Diet_type")[["Protein_to_Carbs_ratio", "Carbs_to_Fats_ratio"]].mean().reset_index()

        result = {
            "avg_macros": avg_macros.to_dict(orient="records"),
            "top_protein": top_protein.to_dict(orient="records"),
            "common_cuisine": common_cuisine.to_dict(orient="records"),
            "avg_ratios": avg_ratios.to_dict(orient="records"),
            "execution_time_seconds": round(time.time() - start_time, 3),
            "row_count" : len(df), 
        }
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin":"*"}
        )
    #return the error of exception
    except Exception as e:
        return func.HttpResponse(
            json.dumps({
                "error": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin":"*"}
        )
   
