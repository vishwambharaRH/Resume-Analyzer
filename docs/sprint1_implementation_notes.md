# Sprint 1 Implementation Notes

This document summarizes the Sprint 1 implementation for the Dynamic Resume Analyzer.

Modules added
- `src/utils/errors.py` - custom exceptions: `ResumeUploadError`, `ResumeParsingError`, `ReportGenerationError`.
- `src/upload_handler.py` - `UploadHandler` for validating and storing uploads. Performs extension and size checks and writes to a temporary storage directory.
- `src/parser.py` - `Parser` with `parse_text` and `parse_file`. Performs simple skill extraction and section detection.
- `src/report_generator.py` - `ReportGenerator` that creates human-readable summaries and JSON payloads.

Tests
- `tests/test_upload_handler.py`- covers upload validation, large file rejection, nonexistent path error, and a 50-concurrency smoke test using ThreadPoolExecutor.
- `tests/test_parser.py`- covers parsing text/files and empty-text errors.
- `tests/test_report_generator.py`- covers summary generation, JSON serialization, and invalid-data error handling.

How to run tests locally

1. Create a Python environment with Python 3.10+.
2. Install pytest: `pip install pytest`.
3. Run tests: `pytest -q`

Design notes & assumptions
- For Sprint 1 we intentionally support text files for parsing. PDF/DOCX extraction will be added in Sprint 2.
- Skill extraction uses a small canonical set (`Parser.COMMON_SKILLS`). This will be made configurable later.
- Upload limit default is 5 MB; configurable via `UploadHandler(max_bytes=...)`.
- Error classes are designed to carry both a user-facing message and an optional debug detail.

Performance & NFRs
- NFR-001 (≤10s per resume): the parser is simple and text-based to be fast. Heavy extraction (pdf/docx/ML models) will be offloaded to asynchronous workers in future sprints.
- Concurrency: tests include a smoke test that simulates 50 concurrent small uploads. In production, consider using a queue and worker pool for heavy jobs.

Next steps for Sprint 2
- Add PDF and DOCX extraction modules.
- Add persistent storage layer (S3 or DB) and streaming uploads.
- Add more robust skill/entity extraction (NLP/ML) and richer test coverage.
