from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from access_control import require_permission
from auth import get_current_user
from database import User

router = APIRouter(prefix="/api", tags=["business_resources"])

# Mock данные - имитация бизнес-объектов
MOCK_DOCUMENTS: List[Dict] = [
    {"id": 1, "title": "Финансовый отчет 2024", "status": "active", "owner_id": 1},
    {"id": 2, "title": "Договор поставки", "status": "active", "owner_id": 2},
    {"id": 3, "title": "Штатное расписание", "status": "draft", "owner_id": 1},
]

MOCK_ORDERS: List[Dict] = [
    {"id": 1, "order_number": "ORD-001", "amount": 15000, "status": "paid"},
    {"id": 2, "order_number": "ORD-002", "amount": 25000, "status": "pending"},
]

MOCK_USERS_LIST: List[Dict] = [
    {"id": 1, "email": "user1@example.com", "role": "viewer"},
    {"id": 2, "email": "user2@example.com", "role": "manager"},
]

# ============ РЕСУРС: Документы ============
@router.get("/documents")
async def get_documents(
    user: User = Depends(require_permission("document", "read"))
):
    """Просмотр документов (нужно право document:read)"""
    return {
        "status": "success",
        "data": MOCK_DOCUMENTS,
        "user": user.email,
        "permission_used": "document:read"
    }

@router.post("/documents")
async def create_document(
    title: str,
    user: User = Depends(require_permission("document", "create"))
):
    """Создание документа (нужно право document:create)"""
    new_doc = {
        "id": len(MOCK_DOCUMENTS) + 1,
        "title": title,
        "status": "draft",
        "owner_id": user.id
    }
    MOCK_DOCUMENTS.append(new_doc)
    return {
        "status": "success",
        "message": "Документ создан",
        "data": new_doc
    }

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    user: User = Depends(require_permission("document", "delete"))
):
    """Удаление документа (нужно право document:delete)"""
    for doc in MOCK_DOCUMENTS:
        if doc["id"] == doc_id:
            MOCK_DOCUMENTS.remove(doc)
            return {
                "status": "success",
                "message": f"Документ {doc_id} удален"
            }
    raise HTTPException(status_code=404, detail="Документ не найден")

# ============ РЕСУРС: Заказы ============
@router.get("/orders")
async def get_orders(
    user: User = Depends(require_permission("order", "read"))
):
    """Просмотр заказов (нужно право order:read)"""
    return {
        "status": "success",
        "data": MOCK_ORDERS,
        "user": user.email
    }

@router.post("/orders")
async def create_order(
    order_number: str,
    amount: float,
    user: User = Depends(require_permission("order", "create"))
):
    """Создание заказа (нужно право order:create)"""
    new_order = {
        "id": len(MOCK_ORDERS) + 1,
        "order_number": order_number,
        "amount": amount,
        "status": "pending"
    }
    MOCK_ORDERS.append(new_order)
    return {
        "status": "success",
        "message": "Заказ создан",
        "data": new_order
    }

# ============ РЕСУРС: Пользователи (админка) ============
@router.get("/admin/users")
async def list_all_users(
    user: User = Depends(require_permission("user", "manage"))
):
    """Список всех пользователей (нужно право user:manage)"""
    return {
        "status": "success",
        "data": MOCK_USERS_LIST,
        "admin": user.email
    }

# ============ РЕСУРС: Отчеты ============
@router.get("/reports/sales")
async def get_sales_report(
    user: User = Depends(require_permission("report", "read"))
):
    """Отчет по продажам (нужно право report:read)"""
    return {
        "status": "success",
        "data": {
            "total_sales": 1250000,
            "growth": "+15%",
            "period": "2024"
        },
        "generated_for": user.email
    }

# ============ ДОСТУП К СВОИМ ДАННЫМ (всегда доступно) ============
@router.get("/me/profile")
async def get_my_profile(user: User = Depends(get_current_user)):
    """Любой авторизованный пользователь может видеть свой профиль"""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "roles": [role.name for role in user.roles]
    }