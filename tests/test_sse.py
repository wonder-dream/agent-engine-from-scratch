import asyncio
import httpx


async def test():
    async with httpx.AsyncClient(timeout=60) as c:
        async with c.stream(
            "POST",
            "http://localhost:8000/chat/stream",
            json={"session_id": "", "message": "你好"},
        ) as r:
            print(f"status: {r.status_code}")
            async for line in r.aiter_lines():
                print(line)
                if '"state": "final"' in line:
                    break


if __name__ == "__main__":
    asyncio.run(test())
