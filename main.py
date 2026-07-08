import time, uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

ALLOWED_ORIGIN = "https://dash-r7bicf.example.com"
EMAIL = "your-email@example.com"  # replace with your actual logged-in email

app = FastAPI()

class TimingRequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        request_id = str(uuid.uuid4())
        response = await call_next(request)
        process_time = time.perf_counter() - start
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        return response

app.add_middleware(TimingRequestIDMiddleware)

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method == "OPTIONS":
        if origin == ALLOWED_ORIGIN:
            resp = JSONResponse(content={}, status_code=200)
            resp.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "*"
            resp.headers["Vary"] = "Origin"
            return resp
        return JSONResponse(content={}, status_code=400)
    response = await call_next(request)
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Vary"] = "Origin"
    return response

@app.get("/stats")
async def stats(values: str):
    nums = [int(x.strip()) for x in values.split(",") if x.strip() != ""]
    count = len(nums)
    total = sum(nums)
    mn = min(nums) if nums else None
    mx = max(nums) if nums else None
    mean = total / count if count else 0.0
    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": mn,
        "max": mx,
        "mean": mean,
    }