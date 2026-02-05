from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de rate limiting que limita el número de requests por cliente.
    Utiliza la IP del cliente como identificador.
    """
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # Estructura: {ip: [(timestamp1, ), (timestamp2, ), ...]}
        self.request_counts: Dict[str, list[datetime]] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Obtener IP del cliente
        client_ip = request.client.host if request.client else "unknown"
        
        # Tiempo actual
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Limpiar requests antiguos
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if req_time > minute_ago
        ]
        
        # Verificar límite
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
            )
        
        # Registrar request actual
        self.request_counts[client_ip].append(now)
        
        # Continuar con el request
        response = await call_next(request)
        return response
