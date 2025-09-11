import time
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from utils.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Starlette 기반 로깅 미들웨어
    HTTP 요청/응답을 로깅하고 처리 시간을 측정합니다.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        start_time = time.time()

        # 요청 body 캐싱 (한 번만 읽고 재사용)
        request_body: Optional[bytes] = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                request_body = await request.body()
                if request_body:
                    logger.info(
                        "request body received",
                        method=request.method,
                        path=request.url.path,
                        body_size=len(request_body),
                    )
                else:
                    logger.warning("empty request body received")
            except Exception:
                logger.error("failed to read request body", exc_info=True, stack_info=True)

        try:
            # 다음 미들웨어/핸들러 호출
            response = await call_next(request)

            # 처리 시간 계산
            process_time = time.time() - start_time

            # 응답 로깅
            await self._log_response(
                request=request,
                response=response,
                process_time=process_time,
                request_body=request_body,
            )

            # 응답에 처리 시간 헤더 추가
            response.headers["X-Process-Time"] = str(round(process_time, 4))

            return response

        except Exception as e:
            # 예외 발생 시 에러 로깅 및 응답 생성
            process_time = time.time() - start_time

            error_response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred while processing your request",
                    "timestamp": time.time(),
                    "path": request.url.path,
                },
            )

            await self._log_exception(
                request=request,
                exception=e,
                process_time=process_time,
                request_body=request_body,
                error_response=error_response,
            )

            return error_response

    async def _log_response(
        self,
        request: Request,
        response: Response,
        process_time: float,
        request_body: Optional[bytes] = None,
    ) -> None:
        """응답 로깅"""
        base_log_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "client": request.client.host if request.client else None,
        }

        if response.status_code >= 400:
            # 에러 응답 로깅 - response body와 추가 정보 포함
            response_headers = dict(response.headers) if hasattr(response, "headers") else {}
            log_data = {
                **base_log_data,
                "request_body": request_body.decode("utf-8") if request_body else None,
                "response_headers": response_headers,
                "response_media_type": getattr(response, "media_type", None),
            }
            logger.error("HTTP error response", **log_data)
        else:
            # 성공 응답 로깅
            logger.info("HTTP response sent", **base_log_data)

    async def _log_exception(
        self,
        request: Request,
        exception: Exception,
        process_time: float,
        request_body: Optional[bytes] = None,
        error_response: Optional[Response] = None,
    ) -> None:
        """예외 로깅"""
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "error": str(exception),
            "error_type": type(exception).__name__,
            "process_time": round(process_time, 4),
            "client": request.client.host if request.client else None,
            "request_body_size": len(request_body) if request_body else 0,
        }

        # 에러 응답 정보 추가
        if error_response:
            log_data["error_response_status"] = getattr(error_response, "status_code", None)
            log_data["error_response_headers"] = (
                dict(error_response.headers) if hasattr(error_response, "headers") else {}
            )

        logger.error(
            "Unhandled exception in request processing",
            **log_data,
            exc_info=True,
            stack_info=True,
        )
