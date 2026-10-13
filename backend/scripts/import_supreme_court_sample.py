#!/usr/bin/env python
"""
Standalone import script for Supreme Court judgment sample.

Imports a verified Supreme Court judgment PDF and its metadata from parquet
into the existing JurisLink MongoDB database.

Usage:
    # Dry-run (default): shows what would be imported
    python scripts/import_supreme_court_sample.py

    # Execute: actually writes to MongoDB
    python scripts/import_supreme_court_sample.py --execute

Requirements:
    - pandas, pyarrow for metadata reading
    - pymupdf for PDF text extraction
    - motor for async MongoDB access
    - pydantic for validation

Input files (expected in backend directory):
    - supreme_court_2023_metadata.parquet
    - sample_judgment.pdf

Target:
    - Imports to 'legal_cases' collection in 'jurislink' database
    - Uses source_case_id '2023_16_872_887' as unique identifier
    - Upsert mode: rerunning updates existing record instead of creating duplicates
"""

import sys
import os
import asyncio
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from urllib.parse import urljoin

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pymupdf
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.legal_case_model import LegalCaseCreate
from app.db.mongodb import get_database, db_client


class SupremeCourtImporter:
    """Handles import of Supreme Court judgment samples."""

    CASE_ID = "2023_16_872_887"
    SOURCE = "Indian Supreme Court Judgments"
    METADATA_FILE = "supreme_court_2023_metadata.parquet"
    PDF_FILE = "sample_judgment.pdf"
    COLLECTION_NAME = "legal_cases"

    def __init__(self, backend_dir: str):
        """
        Initialize importer.

        Args:
            backend_dir: Path to backend directory containing input files
        """
        self.backend_dir = Path(backend_dir)
        self.metadata_path = self.backend_dir / self.METADATA_FILE
        self.pdf_path = self.backend_dir / self.PDF_FILE
        self.metadata_record: Optional[pd.Series] = None
        self.pdf_text: str = ""
        self.pdf_page_count: int = 0
        self.case_data: Optional[Dict[str, Any]] = None

    def validate_input_files(self) -> bool:
        """
        Verify input files exist.

        Returns:
            True if all files exist, False otherwise
        """
        if not self.metadata_path.exists():
            print(f"[ERROR] Metadata file not found: {self.metadata_path}")
            return False

        if not self.pdf_path.exists():
            print(f"[ERROR] PDF file not found: {self.pdf_path}")
            return False

        print(f"[✓] Input files found")
        return True

    def load_metadata(self) -> bool:
        """
        Load metadata from parquet and find matching record.

        Returns:
            True if record found and verified, False otherwise
        """
        try:
            df = pd.read_parquet(str(self.metadata_path))
            print(f"[✓] Metadata loaded: {len(df)} records")

            # Find record by path field
            matches = df[df["path"] == self.CASE_ID]

            if len(matches) == 0:
                print(f"[ERROR] No metadata record found for path: {self.CASE_ID}")
                return False

            if len(matches) > 1:
                print(f"[ERROR] Multiple metadata records found for path: {self.CASE_ID}")
                return False

            self.metadata_record = matches.iloc[0]
            print(f"[✓] Metadata record found and verified")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to load metadata: {e}")
            return False

    def extract_pdf_text(self) -> bool:
        """
        Extract full text from PDF using PyMuPDF.

        Returns:
            True if extraction successful, False otherwise
        """
        try:
            doc = pymupdf.open(str(self.pdf_path))
            page_count = doc.page_count
            self.pdf_text = ""

            for page_num in range(page_count):
                page = doc[page_num]
                self.pdf_text += page.get_text()

            doc.close()

            if not self.pdf_text.strip():
                print("[ERROR] PDF text extraction resulted in empty text")
                return False

            self.pdf_page_count = page_count
            print(
                f"[✓] PDF text extracted: {page_count} pages, "
                f"{len(self.pdf_text)} characters"
            )
            return True

        except Exception as e:
            print(f"[ERROR] Failed to extract PDF text: {e}")
            return False

    def parse_decision_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse decision date string to UTC-aware datetime.

        Args:
            date_str: Date string in format 'DD-MM-YYYY'

        Returns:
            UTC-aware datetime or None if parsing fails
        """
        if pd.isna(date_str) or not date_str:
            return None

        try:
            # Parse format: '30-11-2023'
            dt = datetime.strptime(str(date_str).strip(), "%d-%m-%Y")
            # Make it UTC-aware
            return dt.replace(tzinfo=timezone.utc)
        except Exception as e:
            print(f"[WARN] Failed to parse decision_date '{date_str}': {e}")
            return None

    def parse_judges_from_html(self, raw_html: str) -> list:
        """
        Parse judge names from raw HTML Coram section.

        Extracts judge names from the Coram line in the raw_html,
        removing HTML tags and footnote markers like <sup>*</sup>.

        Args:
            raw_html: HTML content from metadata record

        Returns:
            List of judge names, or empty list if parsing fails
        """
        import re
        
        if pd.isna(raw_html) or not raw_html:
            return []
        
        try:
            # Find the Coram section: "Coram : NAME<...>, NAME..." until closing tag
            # Match pattern: "Coram : " followed by text and HTML tags, stopping at </strong> or <br>
            coram_match = re.search(r'Coram\s*:\s*([^<]*(?:<[^>]+>[^<]*)*?)(?=</strong>|<br)', raw_html, re.IGNORECASE)
            if not coram_match:
                return []
            
            coram_text = coram_match.group(1)
            
            # Remove HTML tags (e.g., <sup style="...">*</sup>)
            coram_text = re.sub(r'<[^>]+>', '', coram_text)
            
            # Remove stray asterisks and extra whitespace
            coram_text = coram_text.replace('*', '').strip()
            
            # Split by comma and clean
            judges = [j.strip() for j in coram_text.split(',') if j.strip()]
            
            return judges
        except Exception as e:
            print(f"[WARN] Failed to parse judges from HTML: {e}")
            return []

    def build_case_data(self) -> bool:
        """
        Build LegalCaseCreate data from metadata and PDF.

        Returns:
            True if data successfully built and validated, False otherwise
        """
        if self.metadata_record is None or not self.pdf_text:
            print("[ERROR] Metadata or PDF not loaded")
            return False

        try:
            # Extract metadata fields
            case_title = str(self.metadata_record.get("title", "")).strip()
            petitioner = str(self.metadata_record.get("petitioner", "")).strip() or None
            respondent = str(self.metadata_record.get("respondent", "")).strip() or None
            judgment_date = self.parse_decision_date(self.metadata_record.get("decision_date"))
            citation = str(self.metadata_record.get("citation", "")).strip() or None
            disposal_nature = str(self.metadata_record.get("disposal_nature", "")).strip() or None

            # Parse judges - first try metadata 'judge' field (comma-separated)
            judges_raw = self.metadata_record.get("judge", "")
            judges = []
            if pd.notna(judges_raw) and judges_raw:
                judges = [j.strip() for j in str(judges_raw).split(",") if j.strip()]

            # Fallback: Parse from raw_html Coram section if metadata has fewer than 2 judges
            if len(judges) < 2:
                raw_html = self.metadata_record.get("raw_html", "")
                html_judges = self.parse_judges_from_html(raw_html)
                if len(html_judges) > len(judges):
                    judges = html_judges
                    if html_judges:
                        print(f"[!] Extracted {len(judges)} judges from HTML Coram: {', '.join(judges)}")

            # Validate required fields
            if not case_title:
                print("[ERROR] case_title is empty")
                return False

            if len(case_title) < 5 or len(case_title) > 500:
                print(f"[ERROR] case_title length {len(case_title)} outside 5-500 range")
                return False

            if not self.pdf_text.strip():
                print("[ERROR] judgment_text is empty")
                return False

            # Build case data dictionary
            # Note: disposal_nature semantics checked - it represents outcome (Appeal allowed, etc)
            # which differs from case_type (typically classification), so we leave case_type unset
            self.case_data = {
                "source": self.SOURCE,
                "source_case_id": self.CASE_ID,
                "case_title": case_title,
                "petitioner": petitioner,
                "respondent": respondent,
                "judgment_date": judgment_date,
                "judges": judges,
                "citation": citation,
                "case_type": None,  # disposal_nature semantics differ; don't mismap
                "legal_category": None,  # No reliable classification method available
                "judgment_text": self.pdf_text,
                "disposal_nature": disposal_nature,
                "summary": None,  # No explicit summary generation available
            }

            print(f"[✓] Case data built and validated")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to build case data: {e}")
            return False

    def print_dry_run_summary(self):
        """Print dry-run summary of data to be imported."""
        if self.case_data is None:
            print("[ERROR] No case data to summarize")
            return

        print("\n" + "=" * 70)
        print("DRY-RUN SUMMARY: Supreme Court Judgment Import")
        print("=" * 70)
        print(f"Source ID:          {self.case_data['source_case_id']}")
        print(f"Source:             {self.case_data['source']}")
        print(f"Case Title:         {self.case_data['case_title'][:60]}..." 
              if len(self.case_data['case_title']) > 60 
              else f"Case Title:         {self.case_data['case_title']}")
        print(f"Petitioner:         {self.case_data['petitioner'] or 'N/A'}")
        print(f"Respondent:         {self.case_data['respondent'] or 'N/A'}")
        print(f"Judgment Date:      {self.case_data['judgment_date']}")
        print(f"Citation:           {self.case_data['citation'] or 'N/A'}")
        print(f"Judges:             {', '.join(self.case_data['judges']) if self.case_data['judges'] else 'N/A'}")
        print(f"Disposal Nature:    {self.case_data['disposal_nature'] or 'N/A'}")
        print(f"PDF Pages:          {self.pdf_page_count}")
        print(f"Judgment Text Len:  {len(self.case_data['judgment_text'])} characters")
        print(f"Case Type:          {self.case_data['case_type'] or 'Not set'}")
        print(f"Legal Category:     {self.case_data['legal_category'] or 'Not set'}")
        print(f"Summary:            {self.case_data['summary'] or 'Not set'}")
        print("\nMode: DRY-RUN (no database changes)")
        print("To execute and write to MongoDB, add --execute flag")
        print("=" * 70 + "\n")

    async def execute_import(self) -> bool:
        """
        Execute import to MongoDB (upsert mode).

        Returns:
            True if import successful, False otherwise
        """
        if self.case_data is None:
            print("[ERROR] No case data to import")
            return False

        try:
            # Initialize async MongoDB connection
            global db_client
            db_client = AsyncIOMotorClient(settings.MONGODB_URI)
            await db_client.admin.command("ping")
            print("[✓] Connected to MongoDB")

            db = db_client[settings.DATABASE_NAME]

            # Prepare document for upsert
            case_doc = {
                "source": self.case_data["source"],
                "source_case_id": self.case_data["source_case_id"],
                "case_title": self.case_data["case_title"],
                "petitioner": self.case_data["petitioner"],
                "respondent": self.case_data["respondent"],
                "judgment_date": self.case_data["judgment_date"],
                "judges": self.case_data["judges"],
                "citation": self.case_data["citation"],
                "case_type": self.case_data["case_type"],
                "legal_category": self.case_data["legal_category"],
                "judgment_text": self.case_data["judgment_text"],
                "disposal_nature": self.case_data["disposal_nature"],
                "summary": self.case_data["summary"],
                "updated_at": datetime.now(timezone.utc),
            }

            # Upsert by source_case_id (keyed on unique constraint)
            result = await db[self.COLLECTION_NAME].update_one(
                {"source_case_id": self.CASE_ID},
                {
                    "$set": case_doc,
                    "$setOnInsert": {
                        "created_at": datetime.now(timezone.utc),
                    },
                },
                upsert=True,
            )

            if result.upserted_id:
                print(f"[✓] Record INSERTED with ID: {result.upserted_id}")
            else:
                print(f"[✓] Record UPDATED")

            return True

        except Exception as e:
            print(f"[ERROR] MongoDB import failed: {e}")
            return False
        finally:
            if db_client is not None:
                db_client.close()
                print("[✓] MongoDB connection closed")

    async def run(self, execute: bool = False) -> bool:
        """
        Execute full import workflow.

        Args:
            execute: If True, write to MongoDB; otherwise dry-run only

        Returns:
            True if successful, False if any step failed
        """
        print(f"[*] Starting Supreme Court Judgment Import")
        print(f"[*] Case ID: {self.CASE_ID}")
        print(f"[*] Backend Directory: {self.backend_dir}\n")

        # Step 1: Validate input files
        if not self.validate_input_files():
            return False

        # Step 2: Load metadata
        if not self.load_metadata():
            return False

        # Step 3: Extract PDF text
        if not self.extract_pdf_text():
            return False

        # Step 4: Build and validate case data
        if not self.build_case_data():
            return False

        # Step 5: Print dry-run summary
        self.print_dry_run_summary()

        # Step 6: Execute import if requested
        if execute:
            print("[*] Executing import to MongoDB...")
            return await self.execute_import()
        else:
            print("[*] Dry-run completed. No database changes made.")
            print("[*] Add --execute flag to write to MongoDB\n")
            return True


class PdfDownloader:
    """Handles downloading Supreme Court judgment PDFs from official dataset."""

    OFFICIAL_BASE_URL = "https://indian-supreme-court-judgments.s3.amazonaws.com"
    PDF_PATH_TEMPLATE = "data/pdf/year=2023/english/{filename}"
    REQUEST_TIMEOUT = 30

    def __init__(self, pdf_dir: Path):
        """
        Initialize downloader.

        Args:
            pdf_dir: Directory to save downloaded PDFs
        """
        self.pdf_dir = pdf_dir
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

    def path_to_pdf_filename(self, path: str) -> str:
        """
        Convert metadata path to PDF filename.

        Args:
            path: Metadata path (e.g., '2023_16_872_887')

        Returns:
            PDF filename (e.g., '2023_16_872_887_EN.pdf')
        """
        return f"{path}_EN.pdf"

    def get_pdf_url(self, path: str) -> str:
        """
        Construct official S3 URL for a PDF.

        Args:
            path: Metadata path

        Returns:
            Full URL to PDF
        """
        filename = self.path_to_pdf_filename(path)
        relative_path = self.PDF_PATH_TEMPLATE.format(filename=filename)
        return urljoin(self.OFFICIAL_BASE_URL, relative_path)

    def is_valid_pdf(self, pdf_path: Path) -> bool:
        """
        Check if file is a valid readable PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if valid PDF, False otherwise
        """
        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            return False

        try:
            doc = pymupdf.open(str(pdf_path))
            if doc.page_count == 0:
                doc.close()
                return False
            doc.close()
            return True
        except Exception:
            return False

    def download_pdf(self, path: str) -> tuple[bool, Optional[str]]:
        """
        Download a single PDF from official dataset.

        Args:
            path: Metadata path

        Returns:
            (success: bool, reason: Optional[str])
        """
        pdf_filename = self.path_to_pdf_filename(path)
        pdf_path = self.pdf_dir / pdf_filename
        url = self.get_pdf_url(path)

        # Check if already exists and is valid
        if self.is_valid_pdf(pdf_path):
            return (True, "already_cached")

        # Download
        try:
            response = requests.get(
                url,
                timeout=self.REQUEST_TIMEOUT,
                allow_redirects=True,
                stream=True
            )
            response.raise_for_status()

            # Write file
            pdf_path.write_bytes(response.content)

            # Validate
            if not self.is_valid_pdf(pdf_path):
                pdf_path.unlink()
                return (False, "invalid_pdf_content")

            return (True, "downloaded")

        except requests.exceptions.Timeout:
            return (False, "timeout")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return (False, "not_found_on_server")
            return (False, f"http_{e.response.status_code}")
        except requests.exceptions.RequestException as e:
            return (False, "network_error")
        except Exception as e:
            return (False, f"error_{type(e).__name__}")


class BatchSupremeCourtImporter:
    """Handles batch import of Supreme Court judgments."""

    SOURCE = "Indian Supreme Court Judgments"
    METADATA_FILE = "supreme_court_2023_metadata.parquet"
    COLLECTION_NAME = "legal_cases"

    def __init__(self, backend_dir: str, limit: int = 10, download_pdfs: bool = False):
        """
        Initialize batch importer.

        Args:
            backend_dir: Path to backend directory containing metadata
            limit: Maximum number of records to import (default: 10)
            download_pdfs: Whether to download missing PDFs (default: False)
        """
        self.backend_dir = Path(backend_dir)
        self.metadata_path = self.backend_dir / self.METADATA_FILE
        self.pdf_dir = self.backend_dir / "data" / "supreme_court_pdfs"
        self.limit = limit
        self.download_pdfs = download_pdfs
        self.metadata_df: Optional[pd.DataFrame] = None
        self.downloader = PdfDownloader(self.pdf_dir) if download_pdfs else None
        
        # Statistics
        self.attempted = 0
        self.downloaded = 0
        self.reused = 0
        self.inserted = 0
        self.updated = 0
        self.skipped = 0
        self.failed = 0
        self.skip_reasons: Dict[str, int] = {}
        self.download_reasons: Dict[str, int] = {}

    def validate_input_files(self) -> bool:
        """Verify metadata file exists."""
        if not self.metadata_path.exists():
            print(f"[ERROR] Metadata file not found: {self.metadata_path}")
            return False
        print(f"[OK] Metadata file found")
        return True

    def load_metadata(self) -> bool:
        """Load metadata from parquet."""
        try:
            self.metadata_df = pd.read_parquet(str(self.metadata_path))
            print(f"[OK] Metadata loaded: {len(self.metadata_df)} total records")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load metadata: {e}")
            return False

    def extract_pdf_text(self, path: str) -> Optional[str]:
        """
        Extract text from a PDF file.

        Args:
            path: Metadata path (e.g., '2023_16_872_887')

        Returns:
            Extracted text or None if extraction fails
        """
        pdf_filename = f"{path}_EN.pdf"
        pdf_path = self.pdf_dir / pdf_filename

        if not pdf_path.exists():
            return None

        try:
            doc = pymupdf.open(str(pdf_path))
            text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text()
            doc.close()
            return text.strip() if text.strip() else None
        except Exception:
            return None

    def parse_judges_from_html(self, raw_html: str) -> list:
        """Parse judge names from raw HTML Coram section."""
        import re
        
        if pd.isna(raw_html) or not raw_html:
            return []
        
        try:
            coram_match = re.search(r'Coram\s*:\s*([^<]*(?:<[^>]+>[^<]*)*?)(?=</strong>|<br)', raw_html, re.IGNORECASE)
            if not coram_match:
                return []
            
            coram_text = coram_match.group(1)
            coram_text = re.sub(r'<[^>]+>', '', coram_text)
            coram_text = coram_text.replace('*', '').strip()
            
            judges = [j.strip() for j in coram_text.split(',') if j.strip()]
            return judges
        except Exception:
            return []

    def parse_decision_date(self, date_str: str) -> Optional[datetime]:
        """Parse decision date string to UTC-aware datetime."""
        if pd.isna(date_str) or not date_str:
            return None
        try:
            dt = datetime.strptime(str(date_str).strip(), "%d-%m-%Y")
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None

    def build_case_data(self, row: pd.Series, judgment_text: str) -> Optional[Dict[str, Any]]:
        """
        Build case data from metadata row and judgment text.

        Args:
            row: Metadata row from dataframe
            judgment_text: Extracted PDF text

        Returns:
            Case data dict or None if validation fails
        """
        try:
            # Extract and validate required fields
            source_case_id = row.get("path", "")
            if not source_case_id:
                self.skip_reasons["Missing source_case_id"] = self.skip_reasons.get("Missing source_case_id", 0) + 1
                return None

            case_title = str(row.get("title", "")).strip()
            if not case_title or len(case_title) < 5 or len(case_title) > 500:
                self.skip_reasons["Invalid case_title"] = self.skip_reasons.get("Invalid case_title", 0) + 1
                return None

            if not judgment_text or len(judgment_text) < 100:
                self.skip_reasons["Empty/short judgment_text"] = self.skip_reasons.get("Empty/short judgment_text", 0) + 1
                return None

            # Extract optional fields
            petitioner = str(row.get("petitioner", "")).strip() or None
            respondent = str(row.get("respondent", "")).strip() or None
            judgment_date = self.parse_decision_date(row.get("decision_date"))
            citation = str(row.get("citation", "")).strip() or None
            disposal_nature = str(row.get("disposal_nature", "")).strip() or None

            # Parse judges
            judges_raw = row.get("judge", "")
            judges = []
            if pd.notna(judges_raw) and judges_raw:
                judges = [j.strip() for j in str(judges_raw).split(",") if j.strip()]

            # Fallback to HTML if needed
            if len(judges) < 2:
                raw_html = row.get("raw_html", "")
                html_judges = self.parse_judges_from_html(raw_html)
                if len(html_judges) > len(judges):
                    judges = html_judges

            return {
                "source": self.SOURCE,
                "source_case_id": source_case_id,
                "case_title": case_title,
                "petitioner": petitioner,
                "respondent": respondent,
                "judgment_date": judgment_date,
                "judges": judges,
                "citation": citation,
                "case_type": None,
                "legal_category": None,
                "judgment_text": judgment_text,
                "disposal_nature": disposal_nature,
                "summary": None,
                "updated_at": datetime.now(timezone.utc),
            }

        except Exception as e:
            self.skip_reasons["Build error"] = self.skip_reasons.get("Build error", 0) + 1
            return None

    async def import_record(self, case_data: Dict[str, Any], db) -> bool:
        """
        Import a single record to MongoDB.

        Args:
            case_data: Case data to import
            db: MongoDB database instance

        Returns:
            True if inserted/updated, False if error
        """
        try:
            # Prepare update document - remove updated_at from data for cleaner merge
            set_data = {k: v for k, v in case_data.items() if k != "updated_at"}
            set_data["updated_at"] = datetime.now(timezone.utc)
            
            result = await db[self.COLLECTION_NAME].update_one(
                {"source_case_id": case_data["source_case_id"]},
                {
                    "$set": set_data,
                    "$setOnInsert": {
                        "created_at": datetime.now(timezone.utc),
                    },
                },
                upsert=True,
            )

            if result.upserted_id:
                self.inserted += 1
                return True
            else:
                self.updated += 1
                return True
        except Exception as e:
            print(f"[ERROR] Import failed for {case_data['source_case_id']}: {e}")
            self.failed += 1
            return False

    async def run(self, execute: bool = False) -> bool:
        """
        Execute batch import workflow.

        Args:
            execute: If True, write to MongoDB; otherwise dry-run only

        Returns:
            True if successful, False if any step failed
        """
        print(f"[*] Starting Batch Supreme Court Import")
        print(f"[*] Limit: {self.limit} records")
        if self.download_pdfs:
            print(f"[*] PDF Download: ENABLED")
            print(f"[*] PDF Directory: {self.pdf_dir}")
        print(f"[*] Backend Directory: {self.backend_dir}\n")

        # Step 1: Validate input files
        if not self.validate_input_files():
            return False

        # Step 2: Load metadata
        if not self.load_metadata():
            return False

        # Step 3: Process records
        print(f"\n[*] Processing first {self.limit} records...\n")

        db = None
        if execute:
            try:
                db_client_batch = AsyncIOMotorClient(settings.MONGODB_URI)
                await db_client_batch.admin.command("ping")
                print("[OK] Connected to MongoDB")
                db = db_client_batch[settings.DATABASE_NAME]
            except Exception as e:
                print(f"[ERROR] MongoDB connection failed: {e}")
                return False

        for idx, (_, row) in enumerate(self.metadata_df.iterrows()):
            if idx >= self.limit:
                break

            self.attempted += 1
            source_case_id = row.get("path", "")

            # Step 3a: Download PDF if enabled
            if self.download_pdfs:
                success, reason = self.downloader.download_pdf(source_case_id)
                if success:
                    if reason == "already_cached":
                        self.reused += 1
                    else:
                        self.downloaded += 1
                    print(f"[DL] {source_case_id}: {reason}")
                else:
                    self.skipped += 1
                    self.download_reasons[reason] = self.download_reasons.get(reason, 0) + 1
                    print(f"[SKIP] {source_case_id}: Download failed ({reason})")
                    continue

            # Step 3b: Extract PDF text
            judgment_text = self.extract_pdf_text(source_case_id)
            if not judgment_text:
                self.skipped += 1
                reason = "Empty judgment text"
                self.skip_reasons[reason] = self.skip_reasons.get(reason, 0) + 1
                print(f"[⊘] {source_case_id}: {reason}")
                continue

            # Step 3c: Build case data
            case_data = self.build_case_data(row, judgment_text)
            if not case_data:
                self.skipped += 1
                print(f"[⊘] {source_case_id}: Validation failed")
                continue

            # Print summary
            print(f"[+] {source_case_id}: {case_data['case_title'][:60]}...")

            # Step 3d: Import if execute mode
            if execute:
                if not await self.import_record(case_data, db):
                    continue

        # Step 4: Print summary
        print(f"\n" + "=" * 70)
        print("BATCH IMPORT SUMMARY")
        print("=" * 70)
        print(f"Attempted:  {self.attempted}")
        if self.download_pdfs:
            print(f"Downloaded: {self.downloaded}")
            print(f"Reused:     {self.reused}")
        print(f"Inserted:   {self.inserted}")
        print(f"Updated:    {self.updated}")
        print(f"Skipped:    {self.skipped}")
        print(f"Failed:     {self.failed}")
        
        if self.download_reasons:
            print(f"\nDownload Failures:")
            for reason, count in sorted(self.download_reasons.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {reason}: {count}")
        
        if self.skip_reasons:
            print(f"\nSkip Reasons:")
            for reason, count in sorted(self.skip_reasons.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {reason}: {count}")

        print(f"\nMode: {'EXECUTE' if execute else 'DRY-RUN'}")
        print("=" * 70)

        if db is not None:
            db_client_batch.close()
            print("[OK] MongoDB connection closed")

        return True


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import Supreme Court judgments to JurisLink MongoDB"
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--sample",
        action="store_true",
        help="Import single sample record (2023_16_872_887) [default if no mode specified]",
    )
    mode_group.add_argument(
        "--batch",
        action="store_true",
        help="Import batch of records (requires local PDFs)",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of records to import in batch mode (default: 10)",
    )
    parser.add_argument(
        "--download-pdfs",
        action="store_true",
        help="Download missing PDFs from official dataset before import (batch mode only)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Write to MongoDB (default is dry-run only)",
    )
    parser.add_argument(
        "--backend-dir",
        type=str,
        default=".",
        help="Path to backend directory (default: current directory)",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.download_pdfs and not args.batch:
        print("[ERROR] --download-pdfs requires --batch mode")
        sys.exit(1)

    # Resolve backend directory
    backend_dir = Path(args.backend_dir).resolve()

    if not backend_dir.exists():
        print(f"[ERROR] Backend directory not found: {backend_dir}")
        sys.exit(1)

    # Default to sample mode if no mode specified
    if not args.batch:
        args.sample = True

    # Run appropriate importer
    if args.sample:
        importer = SupremeCourtImporter(str(backend_dir))
        success = await importer.run(execute=args.execute)
    else:  # batch mode
        batch_importer = BatchSupremeCourtImporter(
            str(backend_dir),
            limit=args.limit,
            download_pdfs=args.download_pdfs
        )
        success = await batch_importer.run(execute=args.execute)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
