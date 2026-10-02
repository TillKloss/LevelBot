import asyncio
import logging
import math
from dataclasses import dataclass
from uuid import uuid4

from .connection import close_pool, initialize_xp_storage
from . import user

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class XPProgress:
    total_xp: int
    level: int
    xp_in_level: int
    xp_required: int
    xp_to_next_level: int


def _validate_ids(guild_id: int, user_id: int) -> None:
    for name, value in (("guild_id", guild_id), ("user_id", user_id)):
        if type(value) is not int or not 0 < value < 2**64:
            raise ValueError(f"{name} must be a positive 64-bit integer.")


class XPBuffer:
    def __init__(self, interval: float = 5.0):
        if not math.isfinite(interval) or interval <= 0:
            raise ValueError("interval must be finite and greater than zero.")
        self._interval = interval
        self._writer_id = uuid4().hex
        self._sequence = 0
        self._pending: dict[tuple[int, int], int] = {}
        self._batch: dict[tuple[int, int], int] | None = None
        self._flush_lock = asyncio.Lock()
        self._lifecycle_lock = asyncio.Lock()
        self._stop = asyncio.Event()
        self._task: asyncio.Task | None = None
        self._accepting = False

    async def start(self) -> None:
        async with self._lifecycle_lock:
            if self._task is not None and not self._task.done():
                return
            await initialize_xp_storage()
            self._stop.clear()
            self._accepting = True
            self._task = asyncio.create_task(self._run(), name="database-xp-flush")

    async def add_xp(self, guild_id: int, user_id: int, amount: int = 2) -> None:
        _validate_ids(guild_id, user_id)
        if type(amount) is not int or not 0 < amount <= 2**31 - 1:
            raise ValueError("amount must be a positive 32-bit integer.")
        if not self._accepting:
            raise RuntimeError("Call await xp.start() before awarding XP.")
        key = (guild_id, user_id)
        self._pending[key] = self._pending.get(key, 0) + amount

    async def get_xp(self, guild_id: int, user_id: int) -> int:
        _validate_ids(guild_id, user_id)
        async with self._flush_lock:
            stored, saved_sequence = await user.get_xp_state(
                guild_id, user_id, self._writer_id
            )
            key = (guild_id, user_id)
            total = stored + self._pending.get(key, 0)
            if self._batch is not None and saved_sequence < self._sequence + 1:
                total += self._batch.get(key, 0)
            return total

    async def get_progress(self, guild_id: int, user_id: int) -> XPProgress:
        total = await self.get_xp(guild_id, user_id)
        level = user.calculate_level(total)
        xp_in_level = total - 50 * level * (level - 1)
        xp_required = 100 * level
        return XPProgress(
            total_xp=total,
            level=level,
            xp_in_level=xp_in_level,
            xp_required=xp_required,
            xp_to_next_level=xp_required - xp_in_level,
        )

    async def _save_batch(self) -> None:
        if self._batch is None:
            return
        await user.save_xp_batch(
            self._writer_id, self._sequence + 1, self._batch
        )
        self._sequence += 1
        self._batch = None

    async def flush(self) -> None:
        async with self._flush_lock:
            await self._save_batch()
            if self._pending:
                self._batch, self._pending = self._pending, {}
                await self._save_batch()

    async def _run(self) -> None:
        while not self._stop.is_set():
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self._interval)
            except TimeoutError:
                try:
                    await self.flush()
                except Exception as exc:
                    logger.error(
                        "Couldn't save XP (%s). Will retry on the next flush.",
                        type(exc).__name__,
                    )

    async def close(self) -> None:
        async with self._lifecycle_lock:
            self._accepting = False
            self._stop.set()
            if self._task is not None:
                await self._task
                self._task = None
            for attempt in range(3):
                try:
                    await self.flush()
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2**attempt)
            await close_pool()


xp = XPBuffer()
