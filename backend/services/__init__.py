"""
Services Package - __init__.py
"""
from .email_service import send_email, send_daily_report, generate_daily_report_html

__all__ = ["send_email", "send_daily_report", "generate_daily_report_html"]
