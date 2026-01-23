"""
Payroll Routes - إدارة الرواتب والخصومات والمكافآت
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging

from .shared import (
    get_database, get_current_user, get_user_tenant_id,
    build_tenant_query, UserRole
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Payroll"])

# ==================== MODELS ====================
class DeductionCreate(BaseModel):
    employee_id: str
    deduction_type: str  # absence, late, advance, penalty, other
    amount: Optional[float] = None
    hours: Optional[float] = None
    days: Optional[float] = None
    reason: str
    date: str

class DeductionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    deduction_type: str
    amount: float
    hours: Optional[float] = None
    days: Optional[float] = None
    reason: str
    date: str
    created_by: str
    created_at: str

class BonusCreate(BaseModel):
    employee_id: str
    bonus_type: str  # performance, overtime, holiday, other
    amount: Optional[float] = None
    hours: Optional[float] = None
    reason: str
    date: str

class BonusResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    bonus_type: str
    amount: float
    hours: Optional[float] = None
    reason: str
    date: str
    created_by: str
    created_at: str

class PayrollCreate(BaseModel):
    employee_id: str
    month: str
    basic_salary: float
    total_deductions: float = 0
    total_bonuses: float = 0
    advance_deduction: float = 0
    net_salary: float
    notes: Optional[str] = None

class PayrollResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    month: str
    basic_salary: float
    worked_days: int = 0
    absent_days: int = 0
    late_hours: float = 0
    overtime_hours: float = 0
    total_deductions: float
    total_bonuses: float
    advance_deduction: float
    net_salary: float
    status: str
    notes: Optional[str] = None
    created_by: str
    created_at: str

# ==================== DEDUCTIONS ====================
@router.post("/deductions", response_model=DeductionResponse)
async def create_deduction(deduction: DeductionCreate, current_user: dict = Depends(get_current_user)):
    """إنشاء خصم"""
    db = get_database()
    if current_user["role"] not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPERVISOR, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    employee = await db.employees.find_one({"id": deduction.employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    
    amount = deduction.amount or 0
    if not amount:
        hourly_rate = employee.get("salary", 0) / (30 * employee.get("work_hours_per_day", 8))
        daily_rate = employee.get("salary", 0) / 30
        
        if deduction.hours:
            amount = deduction.hours * hourly_rate
        elif deduction.days:
            amount = deduction.days * daily_rate
    
    deduction_doc = {
        "id": str(uuid.uuid4()),
        **deduction.model_dump(),
        "employee_name": employee.get("name"),
        "amount": amount,
        "tenant_id": get_user_tenant_id(current_user),
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.deductions.insert_one(deduction_doc)
    del deduction_doc["_id"]
    return deduction_doc

@router.get("/deductions")
async def get_deductions(
    employee_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """جلب قائمة الخصومات"""
    db = get_database()
    query = build_tenant_query(current_user)
    if employee_id:
        query["employee_id"] = employee_id
    if start_date:
        query["date"] = {"$gte": start_date}
    if end_date:
        query.setdefault("date", {})["$lte"] = end_date
    
    deductions = await db.deductions.find(query, {"_id": 0}).sort("date", -1).to_list(500)
    return deductions

# ==================== BONUSES ====================
@router.post("/bonuses", response_model=BonusResponse)
async def create_bonus(bonus: BonusCreate, current_user: dict = Depends(get_current_user)):
    """إنشاء مكافأة"""
    db = get_database()
    if current_user["role"] not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    employee = await db.employees.find_one({"id": bonus.employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    
    amount = bonus.amount or 0
    if not amount and bonus.hours:
        hourly_rate = employee.get("salary", 0) / (30 * employee.get("work_hours_per_day", 8))
        overtime_rate = hourly_rate * 1.5
        amount = bonus.hours * overtime_rate
    
    bonus_doc = {
        "id": str(uuid.uuid4()),
        **bonus.model_dump(),
        "employee_name": employee.get("name"),
        "amount": amount,
        "tenant_id": get_user_tenant_id(current_user),
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.bonuses.insert_one(bonus_doc)
    del bonus_doc["_id"]
    return bonus_doc

@router.get("/bonuses")
async def get_bonuses(
    employee_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """جلب قائمة المكافآت"""
    db = get_database()
    query = build_tenant_query(current_user)
    if employee_id:
        query["employee_id"] = employee_id
    if start_date:
        query["date"] = {"$gte": start_date}
    if end_date:
        query.setdefault("date", {})["$lte"] = end_date
    
    bonuses = await db.bonuses.find(query, {"_id": 0}).sort("date", -1).to_list(500)
    return bonuses

# ==================== PAYROLL CALCULATION ====================
@router.post("/payroll/calculate")
async def calculate_payroll(
    employee_id: str,
    month: str,  # YYYY-MM
    current_user: dict = Depends(get_current_user)
):
    """حساب الراتب للموظف"""
    db = get_database()
    employee = await db.employees.find_one({"id": employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    
    basic_salary = employee.get("salary", 0)
    
    # جلب الحضور
    attendance = await db.attendance.find({
        "employee_id": employee_id,
        "date": {"$regex": f"^{month}"}
    }).to_list(31)
    
    worked_days = len([a for a in attendance if a.get("status") == "present"])
    absent_days = len([a for a in attendance if a.get("status") == "absent"])
    late_hours = sum(a.get("late_hours", 0) for a in attendance)
    overtime_hours = sum(a.get("overtime_hours", 0) for a in attendance)
    
    # جلب الخصومات
    deductions = await db.deductions.find({
        "employee_id": employee_id,
        "date": {"$regex": f"^{month}"}
    }).to_list(100)
    total_deductions = sum(d.get("amount", 0) for d in deductions)
    
    # جلب المكافآت
    bonuses = await db.bonuses.find({
        "employee_id": employee_id,
        "date": {"$regex": f"^{month}"}
    }).to_list(100)
    total_bonuses = sum(b.get("amount", 0) for b in bonuses)
    
    # جلب السلف
    advances = await db.advances.find({
        "employee_id": employee_id,
        "date": {"$regex": f"^{month}"},
        "status": "approved"
    }).to_list(100)
    advance_deduction = sum(a.get("amount", 0) for a in advances)
    
    # حساب صافي الراتب
    net_salary = basic_salary + total_bonuses - total_deductions - advance_deduction
    
    return {
        "employee_id": employee_id,
        "employee_name": employee.get("name"),
        "month": month,
        "basic_salary": basic_salary,
        "worked_days": worked_days,
        "absent_days": absent_days,
        "late_hours": late_hours,
        "overtime_hours": overtime_hours,
        "total_deductions": total_deductions,
        "deductions_breakdown": deductions,
        "total_bonuses": total_bonuses,
        "bonuses_breakdown": bonuses,
        "advance_deduction": advance_deduction,
        "net_salary": net_salary
    }

# ==================== PAYROLL CRUD ====================
@router.post("/payroll", response_model=PayrollResponse)
async def create_payroll(payroll: PayrollCreate, current_user: dict = Depends(get_current_user)):
    """إنشاء كشف راتب"""
    db = get_database()
    if current_user["role"] not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    employee = await db.employees.find_one({"id": payroll.employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    
    payroll_doc = {
        "id": str(uuid.uuid4()),
        **payroll.model_dump(),
        "employee_name": employee.get("name"),
        "status": "draft",
        "tenant_id": get_user_tenant_id(current_user),
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payroll.insert_one(payroll_doc)
    del payroll_doc["_id"]
    return payroll_doc

@router.get("/payroll")
async def get_payroll(
    employee_id: Optional[str] = None,
    month: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """جلب كشوف الرواتب"""
    db = get_database()
    query = build_tenant_query(current_user)
    if employee_id:
        query["employee_id"] = employee_id
    if month:
        query["month"] = month
    if status:
        query["status"] = status
    
    payrolls = await db.payroll.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    return payrolls

@router.put("/payroll/{payroll_id}/pay")
async def pay_payroll(payroll_id: str, current_user: dict = Depends(get_current_user)):
    """صرف الراتب"""
    db = get_database()
    if current_user["role"] not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    payroll = await db.payroll.find_one({"id": payroll_id})
    if not payroll:
        raise HTTPException(status_code=404, detail="كشف الراتب غير موجود")
    
    await db.payroll.update_one(
        {"id": payroll_id},
        {"$set": {
            "status": "paid",
            "paid_at": datetime.now(timezone.utc).isoformat(),
            "paid_by": current_user["id"]
        }}
    )
    return {"message": "تم صرف الراتب"}

@router.post("/payroll/generate-all")
async def generate_all_payrolls(month: str, current_user: dict = Depends(get_current_user)):
    """إنشاء كشوف الرواتب لجميع الموظفين"""
    db = get_database()
    if current_user["role"] not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="غير مصرح")
    
    tenant_id = get_user_tenant_id(current_user)
    query = {"tenant_id": tenant_id, "is_active": True} if tenant_id else {"is_active": True}
    
    employees = await db.employees.find(query, {"_id": 0}).to_list(1000)
    
    generated = 0
    for emp in employees:
        existing = await db.payroll.find_one({
            "employee_id": emp["id"],
            "month": month
        })
        
        if not existing:
            # حساب الراتب
            basic_salary = emp.get("salary", 0)
            
            deductions = await db.deductions.find({
                "employee_id": emp["id"],
                "date": {"$regex": f"^{month}"}
            }).to_list(100)
            total_deductions = sum(d.get("amount", 0) for d in deductions)
            
            bonuses = await db.bonuses.find({
                "employee_id": emp["id"],
                "date": {"$regex": f"^{month}"}
            }).to_list(100)
            total_bonuses = sum(b.get("amount", 0) for b in bonuses)
            
            advances = await db.advances.find({
                "employee_id": emp["id"],
                "date": {"$regex": f"^{month}"},
                "status": "approved"
            }).to_list(100)
            advance_deduction = sum(a.get("amount", 0) for a in advances)
            
            net_salary = basic_salary + total_bonuses - total_deductions - advance_deduction
            
            payroll_doc = {
                "id": str(uuid.uuid4()),
                "employee_id": emp["id"],
                "employee_name": emp.get("name"),
                "month": month,
                "basic_salary": basic_salary,
                "total_deductions": total_deductions,
                "total_bonuses": total_bonuses,
                "advance_deduction": advance_deduction,
                "net_salary": net_salary,
                "status": "draft",
                "tenant_id": tenant_id,
                "created_by": current_user["id"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.payroll.insert_one(payroll_doc)
            generated += 1
    
    return {"message": f"تم إنشاء {generated} كشف راتب"}

# ==================== PAYROLL REPORTS ====================
@router.get("/reports/payroll-summary")
async def get_payroll_summary_report(
    month: str,
    branch_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """تقرير ملخص الرواتب"""
    db = get_database()
    tenant_id = get_user_tenant_id(current_user)
    
    emp_query = {}
    if tenant_id:
        emp_query["tenant_id"] = tenant_id
    if branch_id:
        emp_query["branch_id"] = branch_id
    
    employees = await db.employees.find(emp_query, {"_id": 0}).to_list(1000)
    
    payroll_query = {"month": month}
    if tenant_id:
        payroll_query["tenant_id"] = tenant_id
    
    payrolls = await db.payroll.find(payroll_query, {"_id": 0}).to_list(1000)
    payroll_by_emp = {p["employee_id"]: p for p in payrolls}
    
    result = []
    total_basic = 0
    total_deductions = 0
    total_bonuses = 0
    total_advances = 0
    total_net = 0
    
    for emp in employees:
        payroll = payroll_by_emp.get(emp["id"], {})
        
        basic = payroll.get("basic_salary", emp.get("salary", 0))
        deductions = payroll.get("total_deductions", 0)
        bonuses = payroll.get("total_bonuses", 0)
        advances = payroll.get("advance_deduction", 0)
        net = payroll.get("net_salary", basic + bonuses - deductions - advances)
        status = payroll.get("status", "not_generated")
        
        total_basic += basic
        total_deductions += deductions
        total_bonuses += bonuses
        total_advances += advances
        total_net += net
        
        result.append({
            "employee_id": emp["id"],
            "employee_name": emp.get("name"),
            "department": emp.get("department"),
            "job_title": emp.get("job_title"),
            "basic_salary": basic,
            "total_deductions": deductions,
            "total_bonuses": bonuses,
            "advance_deduction": advances,
            "net_salary": net,
            "status": status
        })
    
    return {
        "month": month,
        "employees": result,
        "summary": {
            "total_employees": len(employees),
            "total_basic_salaries": total_basic,
            "total_deductions": total_deductions,
            "total_bonuses": total_bonuses,
            "total_advances": total_advances,
            "total_net_salaries": total_net
        }
    }

@router.get("/reports/employee-salary-slip/{employee_id}")
async def get_employee_salary_slip(
    employee_id: str,
    month: str,
    current_user: dict = Depends(get_current_user)
):
    """كشف راتب موظف"""
    db = get_database()
    employee = await db.employees.find_one({"id": employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    
    # جلب الحضور
    attendance = await db.attendance.find({
        "employee_id": employee_id,
        "date": {"$regex": f"^{month}"}
    }).to_list(31)
    
    worked_days = len([a for a in attendance if a.get("status") == "present"])
    absent_days = len([a for a in attendance if a.get("status") == "absent"])
    late_count = len([a for a in attendance if a.get("late_minutes", 0) > 0])
    late_minutes = sum(a.get("late_minutes", 0) for a in attendance)
    overtime_hours = sum(a.get("overtime_hours", 0) for a in attendance)
    
    # جلب الخصومات
    deductions = await db.deductions.find({
        "employee_id": employee_id,
        "date": {"$regex": f"^{month}"}
    }, {"_id": 0}).to_list(100)
    total_deductions = sum(d.get("amount", 0) for d in deductions)
    
    # جلب المكافآت
    bonuses = await db.bonuses.find({
        "employee_id": employee_id,
        "date": {"$regex": f"^{month}"}
    }, {"_id": 0}).to_list(100)
    total_bonuses = sum(b.get("amount", 0) for b in bonuses)
    
    # جلب السلف
    advances = await db.advances.find({
        "employee_id": employee_id,
        "date": {"$regex": f"^{month}"},
        "status": "approved"
    }, {"_id": 0}).to_list(100)
    advance_deduction = sum(a.get("amount", 0) for a in advances)
    
    basic_salary = employee.get("salary", 0)
    net_salary = basic_salary + total_bonuses - total_deductions - advance_deduction
    
    return {
        "employee": employee,
        "month": month,
        "attendance_summary": {
            "worked_days": worked_days,
            "absent_days": absent_days,
            "late_count": late_count,
            "late_minutes": late_minutes,
            "overtime_hours": overtime_hours
        },
        "earnings": {
            "basic_salary": basic_salary,
            "bonuses": bonuses,
            "total_bonuses": total_bonuses
        },
        "deductions": {
            "items": deductions,
            "total_deductions": total_deductions,
            "advance_deduction": advance_deduction
        },
        "net_salary": net_salary
    }
