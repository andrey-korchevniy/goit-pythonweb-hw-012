import time
from fastapi import Request, HTTPException, status
from typing import Callable, Dict, Optional

class RateLimiter:
    def __init__(self, times: int = 10, seconds: int = 60):
        self.times = times  
        self.seconds = seconds  
        self.requests: Dict[str, list] = {} 
    
    async def __call__(self, request: Request, endpoint: Optional[str] = None):
        ip = request.client.host
        path = request.url.path if not endpoint else endpoint
        key = f"{ip}:{path}"
        
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        self.requests[key] = [timestamp for timestamp in self.requests[key] if now - timestamp < self.seconds]
        
        if len(self.requests[key]) >= self.times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Слишком много запросов. Пожалуйста, попробуйте снова через {self.seconds} секунд."
            )
        
        self.requests[key].append(now)
        
        return True 