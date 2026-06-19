from pathlib import Path
from django.conf import settings
from django.http import FileResponse, HttpResponse


def spa_view(request):
    index_path = settings.FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(open(index_path, "rb"), content_type="text/html")
    return HttpResponse(
        "<h1>Frontend not built</h1>"
        "<p>Run <code>cd frontend && npm run build</code> or use "
        "<code>npm run dev</code> at http://localhost:5173</p>",
        content_type="text/html",
    )
