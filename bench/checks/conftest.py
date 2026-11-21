"""Bench checks run on a recorded bench run: pytest -m bench --bench-run <run folder>."""

from __future__ import annotations

from pathlib import Path

import pytest

from run import BenchRun, load_bench_run


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--bench-run",
        type=Path,
        help="a bench run folder: plan.csv and card/, the trap's card from that run",
    )


@pytest.fixture
def bench_run(request: pytest.FixtureRequest) -> BenchRun:
    """The bench run named by --bench-run; the checks marked bench are skipped without one."""
    folder = request.config.getoption("--bench-run")
    if folder is None:
        pytest.skip("no bench run given; run with --bench-run <run folder>")
    return load_bench_run(folder)
