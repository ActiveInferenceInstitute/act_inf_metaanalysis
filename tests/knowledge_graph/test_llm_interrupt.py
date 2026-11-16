"""Interrupt real extraction subprocesses while local HTTP calls are in flight."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from knowledge_graph.llm_extraction import LLMConfig, extract_assertions_llm
from knowledge_graph.nanopublication import deserialize_nanopubs
from literature.models import Paper
from tests.knowledge_graph.llm_extraction_fixtures import valid_llm_response

PROJECT = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(os.name != "posix", reason="real SIGINT subprocess contract")
@pytest.mark.parametrize("workers", [1, 2])
def test_interrupt_flushes_accepted_results_and_stops_pending_requests(tmp_path: Path, workers: int):
    release = threading.Event()
    blocked = threading.Event()
    lock = threading.Lock()
    requested: list[int] = []
    response_body = json.dumps({"response": json.dumps(valid_llm_response()), "done": True}).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            index = next(index for index in range(8) if f"Interrupt paper {index}" in request["prompt"])
            with lock:
                requested.append(index)
                if sum(index != 0 for index in requested) >= workers:
                    blocked.set()
            if index == 0:
                status, body = 200, response_body
            else:
                release.wait(10)
                # A retryable failure after SIGINT must not start a new call.
                status, body = 503, b"interrupted local request"
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}"
    nanopubs = tmp_path / "nanopublications.jsonl"
    code = f'''
import sys
from knowledge_graph.llm_extraction import LLMConfig, extract_assertions_llm
from literature.models import Paper
papers = [Paper(f"Interrupt paper {{index}}", "A test abstract.", doi=f"10.1/{{index}}") for index in range(8)]
config = LLMConfig(base_url={url!r}, worker_urls=({url!r},) * {workers},
                   model="test-model", max_retries=3, retry_delay=0.01,
                   timeout_seconds=5, checkpoint_interval=50, nanopub_path={str(nanopubs)!r})
try:
    extract_assertions_llm(papers, config, run_id="interrupted-run")
except KeyboardInterrupt:
    sys.exit(130)
'''
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(PROJECT / "src")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    process = None
    try:
        process = subprocess.Popen(
            [sys.executable, "-c", code], cwd=tmp_path, env=environment,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        assert blocked.wait(10), "extraction did not reach the controlled in-flight request"
        process.send_signal(signal.SIGINT)
        deadline = time.monotonic() + 3
        state = {}
        while time.monotonic() < deadline:
            state_path = tmp_path / "extraction_state.json"
            if state_path.exists():
                state = json.loads(state_path.read_text())
                if state.get("status") == "interrupted":
                    break
            time.sleep(0.01)
        assert state.get("status") == "interrupted", state
        assert state["processed_paper_ids"] == ["doi:10.1/0"]
        assert state["processed_papers"] == 1
        assert state["failed_papers"] == 0
        assert state["unprocessed_papers"] == 7
        assert state["run_id"] == "interrupted-run"
        records = deserialize_nanopubs(nanopubs)
        assert len(records) == 3
        assert {record.assertion.paper_id for record in records} == {"doi:10.1/0"}
        release.set()
        stdout, stderr = process.communicate(timeout=10)
        assert process.returncode == 130, (stdout, stderr)
        assert sorted(requested) == list(range(workers + 1))
        completed = Paper("Interrupt paper 0", "A test abstract.", doi="10.1/0")
        resumed = extract_assertions_llm(
            [completed], LLMConfig(base_url=url, model="test-model", nanopub_path=str(nanopubs)),
        )
        assert {assertion.assertion_id for assertion in resumed} == {
            record.assertion.assertion_id for record in records
        }
        assert sorted(requested) == list(range(workers + 1))
    finally:
        release.set()
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
