import anyio
import time
import pytest

from src.upload.service import save_file


class DummyUpload:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self._content = content

    async def read(self):
        # small async read
        await anyio.sleep(0)
        return self._content


@pytest.mark.anyio
async def test_concurrent_save_file_performance():
    """Integration-like test: simulate 50 concurrent uploads and assert timing.

    This is a lightweight test; it verifies the save path can handle 50
    concurrent small files within the NFR-001 time budget.
    """
    results = []
    count = 50
    start = time.perf_counter()

    async with anyio.create_task_group() as tg:
        for i in range(count):
            dummy = DummyUpload(f"r{i}.txt", f"Resume {i} content".encode("utf-8"))

            async def worker(d):
                res = await save_file(d)
                results.append(res)

            tg.start_soon(worker, dummy)

    elapsed = time.perf_counter() - start

    # Ensure all returned metadata and within per-file budget (batch budget conservative)
    assert len(results) == count
    assert elapsed < 10.0, f"Concurrent save exceeded 10s: {elapsed:.2f}s"
