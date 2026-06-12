import os
import pandas as pd
from io import BytesIO
from azure.storage.blob import BlobServiceClient
import firebase_admin
from firebase_admin import credentials, firestore

def main():
    print("Starting serverless data processing...")

    # 1. Connect to Local Azurite Blob Storage
    # This is the standard Microsoft connection string for the local emulator
    connection_string = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    container_name = "diet-data"
    blob_name = "All_Diets.csv"

    # Download the dataset from Azurite
    print(f"Downloading {blob_name} from Azurite container '{container_name}'...")
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    download_stream = blob_client.download_blob()

    # 2. Process Data with Pandas
    print("Calculating macronutrient averages...")
    df = pd.read_csv(BytesIO(download_stream.readall()))
    
    # Calculate average protein, carbs, and fat grouped by Diet_type
    avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean().reset_index()
    
    # Convert the processed dataframe into a list of dictionaries for Firestore
    results_dict = avg_macros.to_dict(orient='records')

    # 3. Connect to Firebase Firestore
    print("Connecting to Firestore database...")
    # Ensure the JSON key is in the same folder as this script
    cred = credentials.Certificate("firebase-service-account.json")
    
    # Prevent initializing the app multiple times if the script is run repeatedly
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()

    # 4. Upload processed data to Firestore
    print("Uploading insights to Firestore...")
    for record in results_dict:
        # We use the Diet_type string as the unique document ID in the collection
        doc_ref = db.collection('diet_macro_averages').document(str(record['Diet_type']))
        doc_ref.set(record)

    print("Task 3 Complete: Insights successfully stored in Firestore.")

if __name__ == "__main__":
    main()
