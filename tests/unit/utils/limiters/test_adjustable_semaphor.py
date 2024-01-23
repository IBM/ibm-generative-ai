import asyncio
import logging

import pytest
from pydantic import BaseModel, model_validator

from genai._utils.limiters.adjustable_semaphor import AdjustableAsyncSemaphore


class TestState(BaseModel):
    tasks: int
    """Total number of tasks"""

    limits: list[int]
    """New limit to be set"""

    ticks: list[float]
    """Time offset in which next iteration happens"""

    execution_time: list[float]
    """For how long given worker should works"""

    final_order: list[int]
    """Final order in which workers should end"""

    waiting_counts: list[int]
    """Number of waiting workers in given iteration"""

    @model_validator(mode="after")
    def check_consistency(self):
        assert self.tasks == len(self.execution_time)
        assert self.tasks == len(self.final_order)

        assert len(self.ticks) == len(self.limits)
        assert len(self.ticks) == len(self.waiting_counts)


logger = logging.getLogger()


@pytest.mark.unit
class TestAdjustableSemaphore:
    @pytest.mark.asyncio
    async def test_limit_edge_case(self):
        semaphore = AdjustableAsyncSemaphore(0)
        for new_limit in [5, 10, 15, 1, 2]:
            semaphore.change_max_limit(new_limit)
            assert semaphore.limit == new_limit
            assert semaphore.waiting == 0
            assert semaphore.processing == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "state",
        [
            TestState(
                tasks=10,
                limits=[1] * 10,
                ticks=[0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                waiting_counts=[10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                execution_time=[1.0] * 10,
                final_order=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            ),
            TestState(
                tasks=2,
                execution_time=[2, 1],
                final_order=[1, 0],
                limits=[2, 2],
                ticks=[0, 1],
                waiting_counts=[2, 0],
            ),
            TestState(
                tasks=0,
                execution_time=[],
                final_order=[],
                limits=[],
                ticks=[],
                waiting_counts=[],
            ),
            TestState(
                tasks=9,
                execution_time=[1] * 9,
                final_order=[0, 1, 2, 3, 4, 5, 6, 7, 8],
                limits=[3, 1, 1, 1, 1, 2, 2],
                ticks=[0, 0.5, 1, 1, 1, 1, 1],
                waiting_counts=[9, 6, 5, 4, 3, 2, 0],
            ),
            TestState(
                tasks=10,
                execution_time=[1] * 10,
                final_order=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                limits=[6, 1, 1, 6, 6],
                ticks=[0, 1, 1, 0.5, 0],
                waiting_counts=[10, 4, 3, 2, 0],
            ),
            TestState(
                tasks=5,
                execution_time=[5, 1, 1, 2, 2],
                limits=[2, 2, 2, 2, 2, 2],
                ticks=[0, 1, 1, 1, 0.5, 1],
                waiting_counts=[5, 3, 2, 1, 1, 0],
                final_order=[1, 2, 3, 0, 4],
            ),
        ],
    )
    async def test_semaphore_processing(self, state: TestState):
        # Saves workers in order they finishes
        execution_order: list[int] = []

        semaphore = AdjustableAsyncSemaphore(0)
        assert semaphore.locked()
        assert semaphore.limit == 0
        assert semaphore.processing == 0

        def get_sleep_time(sleep_time_seconds: float):
            return sleep_time_seconds / 100

        async def semaphore_worker(worker_id: int):
            async with semaphore:
                sleep_interval = state.execution_time[worker_id]
                await asyncio.sleep(get_sleep_time(sleep_interval))
                execution_order.append(worker_id)

        tasks = [asyncio.create_task(semaphore_worker(i)) for i in range(state.tasks)]
        for idx, (new_limit, sleep_interval, waiting_count) in enumerate(
            zip(state.limits, state.ticks, state.waiting_counts)
        ):
            logger.info(f"Current iteration {idx}/{len(state.limits)}")
            await asyncio.sleep(get_sleep_time(sleep_interval))
            assert semaphore.waiting == waiting_count
            logger.info(f"Changing max limit from {semaphore.limit} to {new_limit}")
            semaphore.change_max_limit(new_limit)
            assert semaphore.limit == new_limit
            assert semaphore.processing <= new_limit

        await asyncio.gather(*tasks)
        assert execution_order == state.final_order
