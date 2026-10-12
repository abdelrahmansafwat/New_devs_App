from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.services.cache import get_revenue_summary
from app.services.reservations import get_tenant_properties
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User must have valid tenant context")

    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    total_revenue = Decimal(revenue_data['total']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_revenue_float = float(total_revenue)
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": total_revenue_float,
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }

@router.get("/dashboard/properties")
async def get_dashboard_properties(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:

    tenant_id = getattr(current_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User must have valid tenant context")

    return await get_tenant_properties(tenant_id)
