# README – Frontend (Dashboard) 🎨
**Role:** Frontend Developer
**Goal:** A dashboard that displays data from the Azure Function endpoint (provided by the Backend teammate), ≥3 charts, filter, refresh, execution time — plus a few extra small details to fully cover the rubric.

> 📌 The real JSON response from the Function will have 4 data groups: `avg_macros`, `top_protein`, `common_cuisine`, `avg_ratios` (Protein-to-Carbs & Carbs-to-Fat ratio — the 2 metrics the team already built in Phase 1). Use `avg_ratios` to draw a 4th chart, going beyond the minimum requirement.

---

## 0. Tool setup
- [ ] VS Code + Live Server extension
- [ ] Plain HTML/CSS/JS + Chart.js (recommended — deploying a Static Web App needs no build step, fewer small errors than React close to the deadline)

---

## 1. Folder structure
```
frontend/
├── index.html
├── style.css
├── app.js
```
> Place this exactly under the `frontend/` folder at the repo root — your Deployment teammate will point the Static Web App's "App location" here.

---

## 2. `index.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Diet Analysis Dashboard</title>
  <link rel="stylesheet" href="style.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
</head>
<body>
  <h1>🥗 Diet Analysis Dashboard</h1>

  <div class="controls">
    <label>Filter by Diet Type:
      <select id="dietFilter">
        <option value="">All</option>
        <option value="paleo">Paleo</option>
        <option value="vegan">Vegan</option>
        <option value="keto">Keto</option>
        <option value="mediterranean">Mediterranean</option>
        <option value="dash">Dash</option>
      </select>
    </label>
    <button id="refreshBtn">🔄 Refresh</button>
    <span id="statusBar">⏳ Loading...</span>
  </div>

  <div class="charts">
    <canvas id="barChart"></canvas>
    <canvas id="lineChart"></canvas>
    <canvas id="pieChart"></canvas>
    <canvas id="ratioChart"></canvas>
  </div>

  <script src="app.js"></script>
</body>
</html>
```
> The 5 diet types in the real dataset are: `paleo, vegan, keto, mediterranean, dash` — fill in the options exactly so the filter always matches the data.

---

## 3. `app.js`
```javascript
// ⚠️ Replace with the real URL provided by the Backend teammate
const FUNCTION_URL = "https://<FUNCTION_APP_NAME>.azurewebsites.net/api/GetDietAnalysis";

let barChart, lineChart, pieChart, ratioChart;

async function loadDashboard(dietType = "") {
  const statusBar = document.getElementById("statusBar");
  statusBar.innerText = "⏳ Loading...";

  try {
    const url = dietType ? `${FUNCTION_URL}?diet_type=${dietType}` : FUNCTION_URL;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Function returned an error: ${res.status}`);
    const data = await res.json();

    statusBar.innerText =
      `⏱ Execution time: ${data.execution_time_seconds}s | Rows: ${data.row_count}`;

    const labels = data.avg_macros.map(d => d.Diet_type);
    const protein = data.avg_macros.map(d => d["Protein(g)"]);
    const carbs = data.avg_macros.map(d => d["Carbs(g)"]);
    const fat = data.avg_macros.map(d => d["Fat(g)"]);

    if (barChart) barChart.destroy();
    barChart = new Chart(document.getElementById("barChart"), {
      type: "bar",
      data: { labels, datasets: [{ label: "Protein (g)", data: protein }] },
      options: { plugins: { title: { display: true, text: "Average Protein by Diet Type" } } }
    });

    if (lineChart) lineChart.destroy();
    lineChart = new Chart(document.getElementById("lineChart"), {
      type: "line",
      data: {
        labels,
        datasets: [
          { label: "Carbs (g)", data: carbs },
          { label: "Fat (g)", data: fat }
        ]
      },
      options: { plugins: { title: { display: true, text: "Carbs vs Fat by Diet Type" } } }
    });

    const cuisineCounts = {};
    data.common_cuisine.forEach(c => {
      cuisineCounts[c.Cuisine_type] = (cuisineCounts[c.Cuisine_type] || 0) + 1;
    });
    if (pieChart) pieChart.destroy();
    pieChart = new Chart(document.getElementById("pieChart"), {
      type: "pie",
      data: {
        labels: Object.keys(cuisineCounts),
        datasets: [{ data: Object.values(cuisineCounts) }]
      },
      options: { plugins: { title: { display: true, text: "Most Common Cuisine by Diet Type" } } }
    });

    // 4th chart (extra beyond the minimum requirement of 3 charts) — uses the team's own metric from Phase 1
    const ratioLabels = data.avg_ratios.map(d => d.Diet_type);
    const proteinCarbsRatio = data.avg_ratios.map(d => d.Protein_to_Carbs_ratio);
    if (ratioChart) ratioChart.destroy();
    ratioChart = new Chart(document.getElementById("ratioChart"), {
      type: "bar",
      data: { labels: ratioLabels, datasets: [{ label: "Protein-to-Carbs Ratio", data: proteinCarbsRatio }] },
      options: { plugins: { title: { display: true, text: "Protein-to-Carbs Ratio by Diet Type" } } }
    });

  } catch (err) {
    statusBar.innerText = `❌ Error: ${err.message}`;
    console.error(err);
  }
}

document.getElementById("refreshBtn").addEventListener("click", () => {
  loadDashboard(document.getElementById("dietFilter").value);
});
document.getElementById("dietFilter").addEventListener("change", (e) => {
  loadDashboard(e.target.value);
});

loadDashboard();
```

---

## 4. `style.css`
```css
body { font-family: sans-serif; margin: 2rem; background: #f7f7f9; }
.controls { display: flex; gap: 1rem; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; }
.charts { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
canvas { background: white; border-radius: 8px; padding: 1rem; }
button { cursor: pointer; padding: 0.4rem 1rem; }
#statusBar { font-size: 0.9rem; color: #555; }
```

---

## 5. Local testing
1. Test temporarily with `http://localhost:7071/api/GetDietAnalysis` (while Backend is running `func start`)
2. Open `index.html` with Live Server
3. Verify: all 4 charts render correctly, filter changes the data, Refresh re-calls the API, a clear error message shows if the fetch fails (not a blank screen)

---

## 6. Deploy to Azure Static Web App
Coordinate with your Deployment teammate — the App location should point exactly to `/frontend`. Details in `README_Deployment.md`.

---

## ✅ Tips to maximize the Frontend score
- Have 4 charts instead of the minimum 3 — but make sure each chart uses a different type (bar/line/pie) to avoid being judged as "repetitive".
- Handle loading and error states clearly (`statusBar`) — graders often click the Refresh button multiple times or test with a wrong endpoint; having proper error handling scores much better on "Frontend Dashboard" than a dashboard that crashes to a blank page.
- Give each chart a clear `title` — this helps graders immediately understand the meaning without needing to ask during grading.
- Light responsiveness (a 2-column grid that resizes) so it looks good on different projectors/laptops during the demo.
- Take a few dashboard screenshots at different filter states to include in the Documentation PDF.

## Completion checklist
- [ ] 4 charts (bar, line, pie, secondary bar) display the correct real data
- [ ] Filter dropdown matches exactly the 5 diet types in the real dataset
- [ ] Refresh works, with loading/error states
- [ ] Shows execution time + row count
- [ ] Deployed publicly via the Static Web App URL
