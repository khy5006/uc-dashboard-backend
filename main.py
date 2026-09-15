"""
FastAPI Backend for Union China Dashboard
Real-time API serving invoice and line item data
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Dict, Any
from datetime import datetime, date
import os

from database import get_db, Invoice, LineItem, init_db

app = FastAPI(
    title="Union China Dashboard API",
    description="Real-time API for business performance dashboard",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Union China Dashboard API",
        "version": "1.0.0"
    }


@app.get("/api/invoices")
def get_invoices(db: Session = Depends(get_db)):
    """Get all invoices"""
    invoices = db.query(Invoice).all()

    return {
        "invoices": [
            {
                "invoice_no": inv.invoice_no,
                "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else "N/A",
                "customer": inv.customer,
                "ship_via": inv.ship_via or "No shipping",
                "total_amount": inv.total_amount,
                "line_item_count": inv.line_item_count
            }
            for inv in invoices
        ]
    }


@app.get("/api/line-items")
def get_line_items(db: Session = Depends(get_db)):
    """Get all line items"""
    items = db.query(LineItem).all()

    return {
        "line_items": [
            {
                "invoice_no": item.invoice_no,
                "p_n": item.p_n,
                "description": item.description,
                "qty": item.qty,
                "price_unit": item.price_unit,
                "amount": item.amount
            }
            for item in items
        ]
    }


@app.get("/api/dashboard-data")
def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Get all data needed for dashboard in one call
    This is the main endpoint your frontend will use
    """
    invoices = db.query(Invoice).all()
    line_items = db.query(LineItem).all()

    return {
        "invoices": [
            {
                "invoice_no": inv.invoice_no,
                "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else "N/A",
                "customer": inv.customer,
                "ship_via": inv.ship_via or "No shipping",
                "total_amount": inv.total_amount,
                "line_item_count": inv.line_item_count
            }
            for inv in invoices
        ],
        "line_items": [
            {
                "invoice_no": item.invoice_no,
                "p_n": item.p_n,
                "description": item.description,
                "qty": item.qty,
                "price_unit": item.price_unit,
                "amount": item.amount
            }
            for item in line_items
        ],
        "last_updated": datetime.utcnow().isoformat()
    }


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get summary statistics"""
    total_invoices = db.query(func.count(Invoice.id)).scalar()
    total_revenue = db.query(func.sum(Invoice.total_amount)).scalar() or 0
    unique_customers = db.query(func.count(func.distinct(Invoice.customer))).scalar()
    unique_products = db.query(func.count(func.distinct(LineItem.p_n))).scalar()

    return {
        "total_invoices": total_invoices,
        "total_revenue": float(total_revenue),
        "unique_customers": unique_customers,
        "unique_products": unique_products
    }


@app.get("/api/customers")
def get_customers(db: Session = Depends(get_db)):
    """Get customer revenue breakdown"""
    results = db.query(
        Invoice.customer,
        func.count(Invoice.id).label('invoice_count'),
        func.sum(Invoice.total_amount).label('total_revenue')
    ).group_by(Invoice.customer).all()

    return {
        "customers": [
            {
                "customer": r.customer,
                "invoice_count": r.invoice_count,
                "total_revenue": float(r.total_revenue)
            }
            for r in results
        ]
    }


@app.get("/api/monthly-revenue")
def get_monthly_revenue(db: Session = Depends(get_db)):
    """Get monthly revenue totals"""
    results = db.query(
        func.date_trunc('month', Invoice.invoice_date).label('month'),
        func.sum(Invoice.total_amount).label('revenue')
    ).filter(
        Invoice.invoice_date.isnot(None)
    ).group_by(
        func.date_trunc('month', Invoice.invoice_date)
    ).order_by('month').all()

    return {
        "monthly_revenue": [
            {
                "month": r.month.strftime('%Y-%m') if r.month else None,
                "revenue": float(r.revenue)
            }
            for r in results if r.month
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
