import json
from datetime import date
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import database
from data import get_data, lookup_ticker, plot_stock_trends

app = FastAPI(
    title="StockLens API",
    description="API for comparing stock performance, moving averages and risk metrics.",
    version="1.0.0",
)

database.create_table()

class ComparisonCreate(BaseModel):
    name: str
    tickers: list[str]
    start: str
    end: str

def convert_companies_to_tickers(companies: str):
    company_names = [
        name.strip()
        for name in companies.split(",")
        if name.strip()
    ]
    if not company_names:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one company name.",
        )
    if len(company_names) > 3:
        raise HTTPException(
            status_code=400,
            detail="Please provide a maximum of 3 companies only.",
        )
    # We loop through names individually rather than using a bulk lookup 
    # so we can track exactly which names failed and return a helpful error to the user.
    tickers = []
    failed_names = []
    for name in company_names:
        ticker = lookup_ticker(name)
        if ticker:
            if ticker not in tickers:
                tickers.append(ticker)
        else:
            failed_names.append(name)
    if failed_names:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find a stock for: '{', '.join(failed_names)}'. Please check the spelling.",
        )
    if not tickers:
        raise HTTPException(
            status_code=404,
            detail="No valid companies were found.",
        )
    return tickers

def validate_dates(start: str, end: str):
    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Dates must use the YYYY-MM-DD format.",
        )
    if start_date >= end_date:
        raise HTTPException(
            status_code=400,
            detail="The start date must be earlier than the end date.",
        )

    return start, end

# @app.get("/")
#  def home():
#     return {
#         "message": "Welcome to the StockLens API.",
#         "docs": "/docs",
#     }  

@app.get("/charts")
def get_stock_charts(companies: str, start: str, end: str):
    start, end = validate_dates(start, end)
    tickers = convert_companies_to_tickers(companies)
    prices = get_data(tickers, start, end)
    if prices.empty:
        raise HTTPException(
            status_code=404,
            detail="No price data was found for the requested companies.",
        )
    for ticker in tickers:
        if ticker not in prices.columns or prices[ticker].dropna().empty:
            raise HTTPException(
                status_code=404,
                detail=f"No price data was found for {ticker}.",
            )
    (
        price_chart,
        short_ma_chart,
        long_ma_chart,
        normalized_chart,
        volatility_chart,
        drawdown_chart,
    ) = plot_stock_trends(prices)
    return {
        "tickers": tickers,
        "start": start,
        "end": end,
        "charts": {
            "closing_prices": json.loads(price_chart.to_json()),
            "moving_average_20": json.loads(short_ma_chart.to_json()),
            "moving_average_50": json.loads(long_ma_chart.to_json()),
            "normalized_performance": json.loads(normalized_chart.to_json()),
            "volatility": json.loads(volatility_chart.to_json()),
            "drawdown": json.loads(drawdown_chart.to_json()),
        },
    }

@app.post("/comparisons")
def save_comparison_route(comparison: ComparisonCreate):
    comparison_id = database.save_comparison(
        comparison.name,
        comparison.tickers,
        comparison.start,
        comparison.end,
    )
    return {
        "id": comparison_id,
        "message": "Comparison saved",
    }

@app.get("/comparisons")
def get_comparisons_route():
    comparisons = database.get_saved_comparisons()
    return {
        "comparisons": comparisons,
    }

@app.delete("/comparisons/{comparison_id}")
def delete_comparison_route(comparison_id: int):
    deleted = database.delete_comparison(comparison_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Comparison not found",
        )
    return {
        "message": "Comparison deleted",
    }

FRONTEND_DIR = Path(__file__).with_name("frontend")

if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")