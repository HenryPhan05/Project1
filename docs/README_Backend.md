# README – Backend (Azure Function) 🔧
**Role:** Backend Developer
**Goal:** Turn `data_analysis.py` + `lambda_function.py` (Phase 1) into a real **Azure Function HTTP Trigger** that reads `All_Diets.csv` from Azure Blob Storage (cloud) and returns JSON to the dashboard.

> 📌 Already reviewed the real code in the repo (`HenryPhan05/Project1`). The real dataset has the following columns: `Diet_type, Recipe_name, Cuisine_type, Protein(g), Carbs(g), Fat(g), Extraction_day, Extraction_time` — 7,806 rows of data. The sample code below uses these exact column names.

---

## ⚠️ Important change compared to Phase 1
In Phase 1, `lambda_function.py` pushed results to **Firebase Firestore**. The Phase 2 rubric grades "Integration" based on the **frontend fetching directly from the Azure Function endpoint**, so Firebase is no longer needed — the Function will **return JSON directly in the response** instead of saving to another DB. This also simplifies the architecture and makes it easier to demo.

---

## 0. Tool setup
- [ ] Python 3.9–3.11
- [ ] Azure Functions Core Tools v4: `npm install -g azure-functions-core-tools@4 --unsafe-perm true`
- [ ] Azure CLI: `az login`
- [ ] Azurite (for local testing before deploying): `npm install -g azurite`

---

## 1. Clone the repo and create a new Function project
```bash
git clone https://github.com/HenryPhan05/Project1
cd Project1
func init AzureFunction --python
cd AzureFunction
func new --name GetDietAnalysis --template "HTTP trigger" --authlevel "anonymous"
```
Use the **Python v2 programming model** → the entire function lives in `function_app.py`.

---

## 2. Write `function_app.py` (reusing logic from `data_analysis.py`)
```python
import azure.functions as func
import pandas as pd
import os, json, time
from io import BytesIO
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

@app.route(route="GetDietAnalysis", auth_level=func.AuthLevel.ANONYMOUS)
def GetDietAnalysis(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()
    try:
        conn_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = "diet-data"
        blob_name = "All_Diets.csv"

        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        download_stream = blob_client.download_blob()

        df = pd.read_csv(BytesIO(download_stream.readall()))
        df.fillna(df.mean(numeric_only=True), inplace=True)

        # Optional filter: ?diet_type=paleo
        diet_filter = req.params.get("diet_type")
        if diet_filter:
            df = df[df["Diet_type"].str.lower() == diet_filter.lower()]

        avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().reset_index()
        top_protein = (df.sort_values("Protein(g)", ascending=False)
                         .groupby("Diet_type").head(5)[["Diet_type", "Recipe_name", "Protein(g)"]])
        common_cuisine = df.groupby("Diet_type")["Cuisine_type"].agg(lambda x: x.mode()[0]).reset_index()

        # Add 2 new metrics from Phase 1 (Protein-to-Carbs, Carbs-to-Fat) so the dashboard has more insights
        df["Protein_to_Carbs_ratio"] = df["Protein(g)"] / df["Carbs(g)"]
        df["Carbs_to_Fats_ratio"] = df["Carbs(g)"] / df["Fat(g)"]
        avg_ratios = df.groupby("Diet_type")[["Protein_to_Carbs_ratio", "Carbs_to_Fats_ratio"]].mean().reset_index()

        result = {
            "avg_macros": avg_macros.to_dict(orient="records"),
            "top_protein": top_protein.to_dict(orient="records"),
            "common_cuisine": common_cuisine.to_dict(orient="records"),
            "avg_ratios": avg_ratios.to_dict(orient="records"),
            "execution_time_seconds": round(time.time() - start_time, 3),
            "row_count": len(df),
        }

        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except Exception as e:
        # Return a clear error instead of letting Azure return a default 500 — helps debug faster
        # and is also a plus point for "Cloud Practices" (proper error handling)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
```

> 💡 Adding `avg_ratios` (2 new metrics from Phase 1) to the response gives the dashboard extra data to draw a 4th chart if desired — going a bit beyond the minimum "3 visualizations" requirement usually scores better.

---

## 3. `requirements.txt`
```
azure-functions
pandas
azure-storage-blob
```
(Remove `pyarrow` if you're not using `engine='pyarrow'` when reading the CSV in the Function — keeping dependencies lean helps cold-start speed, which is also a small plus for "Cloud Practices".)

---

## 4. Local testing with Azurite
```bash
azurite --silent --location ./azurite-data &
# Create a container + upload the CSV into Azurite to test just like in real cloud
az storage container create --name diet-data --connection-string "UseDevelopmentStorage=true"
az storage blob upload --container-name diet-data --name All_Diets.csv --file ../All_Diets.csv --connection-string "UseDevelopmentStorage=true"

func start
```
Test: `http://localhost:7071/api/GetDietAnalysis`

`local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_STORAGE_CONNECTION_STRING": "UseDevelopmentStorage=true"
  }
}
```
⚠️ Do not push this file to GitHub (it's already in the default `.gitignore` created by `func init`).

---

## 5. Deploy to Azure (after your Deployment person has created the Function App)
```bash
func azure functionapp publish <YOUR_FUNCTION_APP_NAME_ON_AZURE>
```
Update the connection string to point to the real Storage Account:
```bash
az functionapp config appsettings set \
  --name <FUNCTION_APP_NAME> \
  --resource-group diet-analysis-rg \
  --settings AZURE_STORAGE_CONNECTION_STRING="<real connection string>"
```

---

## 6. Test the real endpoint + send the URL to Frontend
```
https://<FUNCTION_APP_NAME>.azurewebsites.net/api/GetDietAnalysis
```
- [ ] Returns correct JSON, including `avg_macros`, `top_protein`, `common_cuisine`, `avg_ratios`, `execution_time_seconds`
- [ ] CORS enabled (Azure Portal → Function App → CORS)
- [ ] Test the error case too (e.g. change the container name to a wrong one) to make sure the endpoint returns a clear error instead of crashing with a blank page

---

## ✅ Tips to maximize the Backend score
- Don't hardcode the connection string in code — always read it from `os.environ`. Graders often scrutinize this closely under "Cloud Practices".
- Have a `try/except` that returns a clear JSON error (already in the sample code) instead of letting the Function return Azure's default 500 error.
- Return additional `row_count` and `execution_time_seconds` fields — this both meets the dashboard's "metadata" requirement and shows that you understand what the Function is doing.
- If you have time, add a secondary `/api/health` endpoint that returns `{"status": "ok"}` — useful for quickly demoing that the Function has deployed successfully without needing to read the whole CSV, very handy during presentations.
- Take screenshots of Postman/browser request + response JSON to include in the Documentation PDF.

## Completion checklist
- [ ] Function runs locally with Azurite, using the correct real dataset column names
- [ ] Function reads data from real Azure Blob Storage (not Azurite, not Firebase)
- [ ] Returns complete JSON + handles errors
- [ ] Successfully deployed, has a public URL, CORS working
- [ ] URL sent to Frontend and fetch tested successfully
