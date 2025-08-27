import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_engine_connect(test_engine):
    async with test_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
