# Stocklens

**Stocklens** is a full-stack web application that allows users to compare and visualise historical stock performance, 20 and 50 day moving averages, and risk metrics such as volatility and drawdown of upto 3 companies together.

![Stocklens Dashboard](./images/Stocklens-Dashboard.png)

## Features
* **Smart Search** Accepts company names or tickers and looks up the correct symbol using the Yahoo Finance API.
* **Interactive Visualization:** Generates six dynamic Plotly charts, including 20 and 50 day moving averages and normalized historical performance.
* **Data Persistence:** Users can save their comparisons to a local SQLite database and instantly reload them.
* **Graceful Error Handling:** Catches misspelled company names and returns helpful feedback rather than failing silently.

## Tech Stack
* **Backend:** Python, FastAPI
* **Data Processing:** Pandas, Numpy, yfinance
* **Database:** SQLite
* **Frontend:** Vanilla JavaScript, HTML/CSS, Plotly.js

## The Engineering journey
This project started as a basic data visualization assignment in IBM's Python for Data Science course. Unsatisfied with the static nature of a Jupyter Notebook, I independently decided to rebuild it as a fully deployed full-stack application. This transition forced me to solve several real-world engineering challenges:

1. **Frontend Rendering Bugs:** Plotly initially rendered charts as invisible lines because the browser hadn't finished calculating the layout. I solved this by implementing `requestAnimationFrame` to synchronize the JavaScript event loop with the DOM rendering.
2. **API Data Normalization:** The `yfinance` API returns completely different DataFrame structures depending on how many tickers are requested. I wrote a custom normalization function to ensure a predictable data format across the entire backend.
3. **Robust Error Handling:** I rewrote the API to process company inputs individually, allowing it to track exactly which names failed and return a specific 404 error to the user.

## Run Locally
1. Clone the repo and navigate to the folder.
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `python main.py`
4. Open `http://127.0.0.1:8000` in your browser.

## Future Improvements
* Add user authentication to support private, multi-user comparison saving.
* Implement Redis caching to reduce latency and limit external API calls.
* Dockerize the application for easier deployment.

---
*Disclaimer: This application was built for educational and computer science portfolio purposes. It displays historical data for visualization only and does not provide financial advice, predictions, or investment recommendations.*