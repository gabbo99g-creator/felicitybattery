import asyncio
import aiohttp
from typing import Dict, Any

class FelicityBmsApiError(Exception):
    """Exception to indicate general API error."""
    pass

class FelicityBmsApiConnectionError(FelicityBmsApiError):
    """Exception to indicate connection error."""
    pass

class FelicityBmsApiClient:
    """Async API Client for felicity-bms-bridge REST API."""
    
    def __init__(self, host: str, port: int, session: aiohttp.ClientSession):
        self.host = host
        self.port = port
        self.session = session
        self.base_url = f"http://{host}:{port}"

    async def get_latest(self) -> Dict[str, Any]:
        """Fetch latest telemetry from bridge."""
        return await self._get("/api/v1/bms/felicity/latest")

    async def get_status(self) -> Dict[str, Any]:
        """Fetch status from bridge."""
        return await self._get("/api/v1/bms/felicity/status")

    async def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    raise FelicityBmsApiError(f"Bridge returned HTTP status: {response.status}")
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise FelicityBmsApiConnectionError(f"Connection error to bridge at {self.host}:{self.port}: {e}") from e
        except Exception as e:
            raise FelicityBmsApiError(f"Unexpected error: {e}") from e
