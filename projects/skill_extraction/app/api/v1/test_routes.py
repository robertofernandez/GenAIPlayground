from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.core.config import settings
from jinja2 import Environment, FileSystemLoader, select_autoescape

router = APIRouter(prefix="/test", tags=["testing"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
print(f"📁 loading templates from: {TEMPLATES_DIR}")

# ✅ Crear entorno Jinja2 manualmente
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html', 'xml']),
    auto_reload=True,
    cache_size=0  # Deshabilitar caché
)

def require_testing():
    if settings.ENVIRONMENT not in ["testing", "development"]:
        raise HTTPException(status_code=404, detail="Not found")
    return True

@router.get("/skills-extract", response_class=HTMLResponse, 
            dependencies=[Depends(require_testing)])
async def test_skills_extract_page(request: Request):
    # ✅ Renderizar el template manualmente
    template = env.get_template("test_skills_extract.html")
    html_content = template.render(request=request)
    return HTMLResponse(content=html_content)