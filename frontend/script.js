const API_URL = ""; // Empty string sends requests to the same origin (FastAPI backend)

const companiesInput = document.getElementById("companies");
const startInput = document.getElementById("start");
const endInput = document.getElementById("end");
const results = document.getElementById("results");
const compareButton = document.getElementById("compare-button");
const saveButton = document.getElementById("save-button");
const deleteButton = document.getElementById("delete-button");
const savedSelect = document.getElementById("saved-comparisons");

const CHART_IDS = {
    "closing-prices-chart": "closing_prices",
    "ma20-chart": "moving_average_20",
    "ma50-chart": "moving_average_50",
    "normalized-chart": "normalized_performance",
    "volatility-chart": "volatility",
    "drawdown-chart": "drawdown",
};

compareButton.addEventListener("click", compareStocks);
saveButton.addEventListener("click", saveComparison);
deleteButton.addEventListener("click", deleteSelectedComparison);
savedSelect.addEventListener("change", loadSelectedComparison);

async function compareStocks() {
    compareButton.disabled = true;
    compareButton.textContent = "Comparing…";

    try {
        const companies = companiesInput.value;
        const start = startInput.value;
        const end = endInput.value;
        const url = `${API_URL}/charts?companies=${encodeURIComponent(companies)}&start=${start}&end=${end}`;
        const response = await fetch(url);

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            alert(error.detail || "Could not load charts. Check the company names and dates.");
            return;
        }

        const data = await response.json();

        document.getElementById("selected-tickers").textContent = data.tickers.join(", ");
        document.getElementById("selected-start").textContent = data.start;
        document.getElementById("selected-end").textContent = data.end;

        results.classList.remove("hidden");
        // Wait for the browser to finish calculating the layout before rendering 
        // Plotly charts, otherwise they render at 0 width and look broken.
        await new Promise(requestAnimationFrame);

        for (const chartId in CHART_IDS) {
            const chart = data.charts[CHART_IDS[chartId]];
            Plotly.newPlot(chartId, chart.data, chart.layout, { 
                responsive: true,
                displayModeBar: false
            });
        }
    } finally {
        compareButton.disabled = false;
        compareButton.textContent = "Compare stocks";
    }
}

async function saveComparison() {
    const name = prompt("Enter a name for this comparison:");
    if (!name) return;

    const companies = companiesInput.value
        .split(",")
        .map((company) => company.trim())
        .filter((company) => company !== "");

    const response = await fetch(`${API_URL}/comparisons`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: name,
            tickers: companies,
            start: startInput.value,
            end: endInput.value,
        }),
    });

    if (response.ok) {
        alert("Comparison saved.");
        loadSavedComparisons();
    } else {
        alert("Could not save comparison.");
    }
}

async function deleteSelectedComparison() {
    const comparisonId = savedSelect.value;
    if (!comparisonId) {
        alert("Select a saved comparison first.");
        return;
    }

    const response = await fetch(`${API_URL}/comparisons/${comparisonId}`, {
        method: "DELETE",
    });

    if (response.ok) {
        alert("Comparison deleted.");
        loadSavedComparisons();
    } else {
        alert("Could not delete comparison.");
    }
}

async function loadSavedComparisons() {
    try {
        const response = await fetch(`${API_URL}/comparisons`);
        const data = await response.json();

        savedSelect.innerHTML = '<option value="">Select a saved comparison</option>';
        for (const comparison of data.comparisons) {
            const option = document.createElement("option");
            option.value = comparison.id;
            option.textContent = comparison.name;
            savedSelect.appendChild(option);
        }
    } catch {
    }
}

async function loadSelectedComparison() {
    const comparisonId = savedSelect.value;
    if (!comparisonId) return;

    const response = await fetch(`${API_URL}/comparisons`);
    const data = await response.json();
    const comparison = data.comparisons.find(
        (item) => String(item.id) === comparisonId
    );
    if (!comparison) return;

    companiesInput.value = comparison.tickers.join(", ");
    startInput.value = comparison.start;
    endInput.value = comparison.end;
    compareStocks();
}

loadSavedComparisons();