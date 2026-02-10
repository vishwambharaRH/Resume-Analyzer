# src/database/metadata_model.py

import logging
import json
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from src.database.connection import get_db_session

logger = logging.getLogger(__name__)

# Base class for declarative models
Base = declarative_base()


class MetadataModel(Base):
    """
    SQLAlchemy ORM Model for the anonymous resume_metadata table (NFR-008).
    """

    __tablename__ = "resume_metadata"

    id = Column(Integer, primary_key=True, index=True)
    file_type = Column(String(10), nullable=False)
    processing_time_ms = Column(Integer, nullable=False)
    # Storing missing_sections as a JSON string
    missing_sections = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=False)  # New anonymous metric
    log_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


def log_metadata(metadata_payload: Dict[str, Any]) -> bool:
    """
    Logs anonymous, aggregated metadata using the SQLAlchemy ORM session.

    Args:
        metadata_payload: Dictionary containing anonymous data:
            - 'file_type': str
            - 'processing_time_ms': int
            - 'missing_sections': list[str]
            - 'file_size_bytes': int

    Returns:
        True if the log was successful, False otherwise.
    """

    required_keys = [
        "file_type",
        "processing_time_ms",
        "missing_sections",
        "file_size_bytes",
    ]

    # 1. Validation & Data Preparation
    for key in required_keys:
        if key not in metadata_payload:
            logger.error(f"Metadata logging failed: Missing required key '{key}'.")
            return False

    try:
        # Convert list of sections to JSON string for storage
        missing_sections_json = json.dumps(metadata_payload["missing_sections"])

        new_entry = MetadataModel(
            file_type=metadata_payload["file_type"],
            processing_time_ms=metadata_payload["processing_time_ms"],
            missing_sections=missing_sections_json,
            file_size_bytes=metadata_payload["file_size_bytes"],
            # log_timestamp is handled by the default
        )

        # 2. Database Insertion
        with get_db_session() as db:
            db.add(new_entry)
            # The commit is handled by the get_db_session context manager
            logger.info(
                f"Metadata logged successfully: {new_entry.file_type}, {new_entry.processing_time_ms}ms."
            )

        return True

    except Exception as e:
        logger.error(f"Failed to insert metadata into resume_metadata: {e}")
        return False
