from app.core.config import settings
from fastapi import HTTPException

def require_testing():
    """Dependencia para restringir endpoints solo a entornos de testing"""
    if settings.ENVIRONMENT not in ["testing", "development"]:
        raise HTTPException(status_code=404, detail="Not found")
    return True