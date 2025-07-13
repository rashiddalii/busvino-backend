from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
import traceback

app = FastAPI()


def create_response(success: bool, message: str, details=None, status_code=200):
    if details is None:
        details = []
    return JSONResponse(
        status_code=status_code,
        content={
            "success": success,
            "message": message,
            "details": details
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(map(str, err["loc"][1:])),  # Remove "body"
            "message": err["msg"]
        }
        for err in exc.errors()
    ]
    return create_response(
        success=False,
        message="Validation failed",
        details=errors,
        status_code=422
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict):
        details = [exc.detail]
        message = exc.detail.get("message", "Something went wrong")
        # Also override message if Auth0-like error_description is present
        if "error_description" in exc.detail:
            message = exc.detail["error_description"]
    else:
        details = [{"message": str(exc.detail)}]
        message = str(exc.detail)

    return create_response(
        success=False,
        message=message,
        details=details,
        status_code=exc.status_code
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    print("Unhandled Exception:", traceback.format_exc())
    return create_response(
        success=False,
        message="Internal server error",
        details=[{"message": str(exc)}],
        status_code=500
    )
