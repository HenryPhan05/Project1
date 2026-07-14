# README – Deployment / Cloud Infra ☁️
**Role:** Deployment / DevOps
**Goal:** Set up Azure infrastructure (Resource Group, Storage, Function App, Static Web App), upload the real `All_Diets.csv`, configure CI/CD, and support Backend + Frontend deployment.

> 📌 Current repo: `github.com/HenryPhan05/Project1`. Phase 1 already has `.github/workflows/deploy.yml` (build & push a Docker image to Docker Hub) — in Phase 2 it will be replaced with an Azure deployment workflow, see section 6.

---

## 0. Preparation
- [ ] Create an **Azure for Students** account (free, no credit card required): https://azure.microsoft.com/free/students/
- [ ] Install Azure CLI: `az login`
- [ ] Confirm the correct subscription: `az account show`

---

## 1. Resource Group
```bash
az group create --name diet-analysis-rg --location eastus
```

---

## 2. Storage Account + Container + Upload the real dataset
```bash
az storage account create \
  --name dietanalysisstorage \
  --resource-group diet-analysis-rg \
  --location eastus \
  --sku Standard_LRS

az storage account show-connection-string \
  --name dietanalysisstorage \
  --resource-group diet-analysis-rg \
  --query connectionString --output tsv

az storage container create \
  --name diet-data \
  --account-name dietanalysisstorage

# Use the exact All_Diets.csv file already in the repo (7,806 rows of data)
az storage blob upload \
  --account-name dietanalysisstorage \
  --container-name diet-data \
  --name All_Diets.csv \
  --file ./All_Diets.csv
```
- [ ] Send the **connection string** to Backend (private channel, do NOT commit it to GitHub)
- [ ] Double-check: the file on Blob Storage must have the same UTF-8 encoding as the original file, since `Recipe_name` contains many dish names with quotation marks/special characters (e.g. `"Paleo Effect Asian-Glazed Pork Sides, A Sweet & Crispy Appetizer"`) — if uploaded with the wrong encoding, `pd.read_csv` on the Function side may fail.

---

## 3. Function App
```bash
az storage account create \
  --name dietfuncstorage \
  --resource-group diet-analysis-rg \
  --location eastus \
  --sku Standard_LRS

az functionapp create \
  --name diet-analysis-func \
  --resource-group diet-analysis-rg \
  --storage-account dietfuncstorage \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type linux
```
> The name must be unique across all of Azure; if it's taken, change it (e.g. `diet-analysis-func-g1`).

After Backend finishes `func azure functionapp publish`:
```bash
az functionapp config appsettings set \
  --name diet-analysis-func \
  --resource-group diet-analysis-rg \
  --settings AZURE_STORAGE_CONNECTION_STRING="<real connection string>"

az functionapp cors add \
  --name diet-analysis-func \
  --resource-group diet-analysis-rg \
  --allowed-origins "*"
```
Once you have the real Static Web App URL (step 4), it's better to change `"*"` to the actual domain for tighter security — this is also a small plus point for "Cloud Practices" in the rubric.

---

## 4. Static Web App
Via the Azure Portal (auto-generates a GitHub Actions workflow):
1. portal.azure.com → Create resource → Static Web App
2. Resource Group: `diet-analysis-rg`
3. Link the GitHub repo `HenryPhan05/Project1`, branch `main`
4. Build Details:
   - **App location**: `/frontend`
   - **Output location**: (leave blank)
5. Create → Azure automatically adds `.github/workflows/azure-static-web-apps-*.yml`

- [ ] Get the public URL (`https://<random-name>.azurestaticapps.net`) — this is the main deliverable link

---

## 5. End-to-end check
- [ ] Dashboard loads via the Static Web App URL
- [ ] Fetches the correct real data (no CORS/404/500 errors)
- [ ] Changing the filter + Refresh works correctly

---

## 6. Updating CI/CD from Phase 1
The old workflow `.github/workflows/deploy.yml` builds a Docker image for `data_analysis.py` — no longer needed in Phase 2 since Docker is not used to run the Azure Function/Static Web App anymore. Suggestions:
- [ ] **Delete** or archive the old Docker workflow (keep it in the docs as proof of Phase 1 if you want)
- [ ] Keep the auto-generated Static Web App workflow from step 4
- [ ] (Optional, extra points for "Cloud Practices") Add a job to automatically deploy the Function App using the `Azure/functions-action@v1` action, with the publish profile stored in GitHub Secrets — this makes the entire CI/CD pipeline fully automatic, without needing manual `func publish` every time the code changes.

---

## 7. Preparing the Documentation PDF
- [ ] Architecture diagram: Blob Storage → Function (HTTP trigger) → Dashboard (Static Web App)
- [ ] Screenshot of the full Resource Group (Storage Account, Function App, Static Web App) on the Azure Portal
- [ ] Screenshot of the Function endpoint returning real JSON (Postman/browser)
- [ ] Screenshot of the working dashboard (all 4 charts, filter by 5 diet types, refresh)
- [ ] Function App URL + Static Web App URL
- [ ] Note down any difficulties encountered (e.g. duplicate resource names, CORS errors, CSV encoding) — graders appreciate this part since it shows the team genuinely did the work rather than copying a template

---

## ✅ Tips to maximize the Deployment score
- Don't leave connection strings/secrets in code that's been pushed to GitHub — always go through Application Settings or GitHub Secrets. This is the most common point deducted under "Cloud Practices".
- Give resources a consistent name prefix (`diet-analysis-*`) — easy to read, easy to grade when the examiner opens the Resource Group.
- Delete leftover test/junk resources before submitting (e.g. a Storage Account created for testing then abandoned) so the Resource Group looks clean in screenshots.
- Test the endpoint + dashboard in an incognito browser window before submitting — to make sure it doesn't depend on your personal machine's cache/cookies.

## Completion checklist
- [ ] Resource Group + Storage Account + Function App exist on Azure
- [ ] The real dataset (`All_Diets.csv`, 7,806 rows) has been uploaded to cloud Blob Storage
- [ ] Function App + Static Web App deployed successfully, with public URLs
- [ ] CORS correct, connection string not exposed on GitHub
- [ ] Enough screenshots collected for the Documentation
