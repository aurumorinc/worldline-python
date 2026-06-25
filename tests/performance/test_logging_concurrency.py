import uuid
import structlog
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from unittest import mock

from lume.logging import setup_logging, get_logger
from lume.config import LoggingSettings


def test_thread_safe_contextvars():
    """
    Test that bound contextvars in structlog do not bleed across threads
    under concurrent load.
    """
    # Arrange
    settings = LoggingSettings()
    out = StringIO()

    with mock.patch("sys.stdout", out):
        setup_logging(settings)
        logger = get_logger("concurrency_test")

        num_threads = 10
        messages_per_thread = 100

        def worker(thread_idx: int):
            # Bind a unique identifier for this thread
            thread_uuid = str(uuid.uuid4())
            structlog.contextvars.bind_contextvars(thread_uuid=thread_uuid)

            for i in range(messages_per_thread):
                logger.info(f"msg-{thread_idx}-{i}", expected_uuid=thread_uuid)

            return thread_uuid

        # Act
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]

        # Collect the UUIDs that were actually generated
        expected_uuids = {f.result() for f in futures}

        # Assert
        output_str = out.getvalue()
        
        import re

        expected_matches = re.finditer(r"expected_uuid=([a-f0-9\-]+)", output_str)
        thread_matches = re.finditer(r"thread_uuid=([a-f0-9\-]+)", output_str)
        
        expected_list = [m.group(1) for m in expected_matches]
        thread_list = [m.group(1) for m in thread_matches]
        
        assert len(expected_list) == num_threads * messages_per_thread
        assert len(thread_list) == num_threads * messages_per_thread

        for expected_val, thread_val in zip(expected_list, thread_list):
            assert expected_val == thread_val, "Context bleed detected!"
            assert expected_val in expected_uuids, "Unknown UUID detected"
