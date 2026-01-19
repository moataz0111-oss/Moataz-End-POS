"""
Auth Helpers - دوال المصادقة المساعدة
"""

import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")

security = HTTPBearer()

def hash_password(password: str) -> str:
    """تشفير كلمة المرور"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    """التحقق من كلمة المرور"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, role: str, branch_id: Optional[str] = None, tenant_id: Optional[str] = None) -> str:
    """إنشاء JWT token"""
    payload = {
        "user_id": user_id,
        "role": role,
        "branch_id": branch_id,
        "tenant_id": tenant_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    """فك تشفير JWT token"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def has_role(user: dict, roles: list) -> bool:
    """التحقق من صلاحية المستخدم"""
    return user.get("role") in roles

def get_user_tenant_id(user: dict) -> Optional[str]:
    """جلب معرف العميل (tenant) للمستخدم"""
    if user.get("role") == "super_admin":
        return None
    return user.get("tenant_id")

def build_tenant_query(user: dict, base_query: dict = None) -> dict:
    """بناء استعلام يتضمن فلترة حسب العميل"""
    query = base_query.copy() if base_query else {}
    tenant_id = get_user_tenant_id(user)
    
    if tenant_id:
        query["tenant_id"] = tenant_id
    elif user.get("role") != "super_admin":
        query["tenant_id"] = {"$in": [None, ""]}
    
    return query

def build_branch_query(user: dict, base_query: dict = None) -> dict:
    """بناء استعلام يتضمن فلترة حسب الفرع"""
    query = build_tenant_query(user, base_query)
    
    if user.get("role") not in ["admin", "super_admin", "manager"]:
        if user.get("branch_id"):
            query["branch_id"] = user["branch_id"]
    
    return query

def user_can_access_branch(user: dict, branch_id: str) -> bool:
    """التحقق من صلاحية المستخدم للوصول للفرع"""
    if user.get("role") in ["admin", "super_admin", "manager"]:
        return True
    return user.get("branch_id") == branch_id
