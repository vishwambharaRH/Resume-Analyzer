# In tests/unit/parsing/test_analyzer.py

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the function we are testing
from src.parser.analyzer import run_analysis


@pytest.mark.asyncio
# 1. We patch the functions where they are *imported*
@patch("src.parser.analyzer.get_text_from_parser")
@patch("src.parser.analyzer.extract_skills")
@patch("src.parser.analyzer.SectionDetector")
@patch("src.parser.analyzer.validate_content")  # <-- ADD THIS LINE
async def test_run_analysis_orchestration(
    mock_validate_content,  # <-- ADD THIS ARGUMENT (order matters)
    mock_SectionDetector,
    mock_extract_skills,
    mock_get_text_from_parser,
    capsys,
):
    """
    Tests the analyzer's orchestration logic...
    """
    # 2. Define what the mocks should return
    mock_get_text_from_parser.return_value = "This is a resume with python"

    mock_extract_skills.return_value = {"technical_skills": ["Python"]}

    mock_SectionDetector.return_value.validate_resume_structure.return_value = {
        "missing_sections": ["projects"]
    }

    # --- ADD MOCK FOR THE NEW VALIDATOR ---
    mock_validate_content.return_value = {
        "dates": {"consistent": True, "format": "MMM YYYY"}
    }
    # --- ---

    job_id = "test-job-123"
    test_file_path = "dummy/path.pdf"

    # 3. Run the function
    await run_analysis(test_file_path, job_id)

    # 4. Check that the correct functions were called
    mock_get_text_from_parser.assert_called_once_with(Path(test_file_path))
    mock_extract_skills.assert_called_once_with("This is a resume with python")
    mock_SectionDetector.return_value.validate_resume_structure.assert_called_once()

    # --- ADD ASSERTION FOR NEW VALIDATOR ---
    mock_validate_content.assert_called_once_with("This is a resume with python")
    # --- ---

    # 5. Check the final print output (using single quotes)
    captured = capsys.readouterr()
    output = captured.out

    assert f"Job {job_id} complete" in output
    assert "'status': 'complete'" in output

    # Check that your logic's output is present
    assert "'skills': {'technical_skills': ['Python']}" in output

    # Check that the other logic's output is present
    assert "'structure': {'missing_sections': ['projects']}" in output

    # --- ADD ASSERTION FOR NEW VALIDATOR'S OUTPUT ---
    assert (
        "'validation': {'dates': {'consistent': True, 'format': 'MMM YYYY'}}" in output
    )
    # --- ---
