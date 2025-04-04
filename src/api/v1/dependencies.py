from fastapi import status, Request, Response, HTTPException
import time

RATE_LIMIT = 100
RATE_RESET_TIME = 60

rate_limits = {}


def rate_limiter(request: Request, response: Response):
    client_ip = request.client.host
    now = int(time.time())

    if client_ip in rate_limits:
        remaining, reset_time = rate_limits[client_ip]
    else:
        remaining, reset_time = RATE_LIMIT, now + RATE_RESET_TIME

    if remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.⏳",
            headers={"Retry-After": str(reset_time - now)},
        )

    rate_limits[client_ip] = [remaining - 1, reset_time]

    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
    response.headers["X-RateLimit-Reset"] = str(reset_time)
