#!/usr/bin/env python3
"""
Smart File Organizer - AI-Powered File Categorization
Reads files from a folder, uses AI to categorize them, and moves them to organized folders.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional

# ============================================================
# CONFIGURATION - Add your API key here
# ============================================================
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key
AI_PROVIDER = "gemini"  # Options: "gemini", "openai", "anthropic"
# ============================================================

# Category folders to create
CATEGORIES = [
    "Receipts",
    "Code",
    "Documents",
    "Images",
    "Archives",
    "Other"
]


def get_ai_category(file_content: str, filename: str) -> str:
    """
    Send file content to AI and get category classification.
    Returns one of the CATEGORIES.
    """
    prompt = f"""Classify this file into ONE of these categories: {', '.join(CATEGORIES)}

Filename: {filename}
Content (first 500 chars):
{file_content[:500]}

Respond with ONLY the category name, nothing else."""

    if AI_PROVIDER == "gemini":
        return _call_gemini(prompt)
    elif AI_PROVIDER == "openai":
        return _call_openai(prompt)
    elif AI_PROVIDER == "anthropic":
        return _call_anthropic(prompt)
    else:
        return "Other"


def _call_gemini(prompt: str) -> str:
    """Call Google Gemini API."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        category = response.text.strip()
        return category if category in CATEGORIES else "Other"
    except Exception as e:
        print(f"  Gemini API error: {e}")
        return "Other"


def _call_openai(prompt: str) -> str:
    """Call OpenAI API."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category if category in CATEGORIES else "Other"
    except Exception as e:
        print(f"  OpenAI API error: {e}")
        return "Other"


def _call_anthropic(prompt: str) -> str:
    """Call Anthropic Claude API."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=API_KEY)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        category = response.content[0].text.strip()
        return category if category in CATEGORIES else "Other"
    except Exception as e:
        print(f"  Anthropic API error: {e}")
        return "Other"


def ensure_category_folders(base_path: Path):
    """Create category folders if they don't exist."""
    for category in CATEGORIES:
        folder = base_path / category
        folder.mkdir(exist_ok=True)


def organize_files(source_folder: Path):
    """Main organization logic."""
    if not source_folder.exists() or not source_folder.is_dir():
        print(f"Source folder '{source_folder}' does not exist or is not a directory.")
        return

    # Create category folders
    ensure_category_folders(source_folder)

    # Get all files (not directories) in source folder
    files = [f for f in source_folder.iterdir() if f.is_file()]
    
    if not files:
        print(f"No files found in '{source_folder}'.")
        return

    print(f"Found {len(files)} file(s) to organize.\n")

    for file_path in files:
        # Skip files already in category folders
        if file_path.parent.name in CATEGORIES:
            continue

        print(f"Processing: {file_path.name}")

        # Read file content (first 500 chars for classification)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(500)
        except Exception as e:
            print(f"  Error reading file: {e}")
            continue

        # Get AI category
        category = get_ai_category(content, file_path.name)
        print(f"  AI Category: {category}")

        # Move file to category folder
        dest_folder = source_folder / category
        dest_path = dest_folder / file_path.name

        # Handle duplicate filenames
        counter = 1
        original_dest = dest_path
        while dest_path.exists():
            stem = original_dest.stem
            suffix = original_dest.suffix
            dest_path = dest_folder / f"{stem}_{counter}{suffix}"
            counter += 1

        try:
            shutil.move(str(file_path), str(dest_path))
            print(f"  Moved to: {category}/{dest_path.name}")
        except Exception as e:
            print(f"  Error moving file: {e}")

        print()  # Empty line for readability


def main():
    print("=" * 60)
    print("Smart File Organizer")
    print("=" * 60)
    print(f"AI Provider: {AI_PROVIDER}")
    print(f"API Key: {'Set' if API_KEY != 'YOUR_API_KEY_HERE' else 'NOT SET (placeholder)'}")
    print()

    if API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  WARNING: Please set your API_KEY in the CONFIGURATION section!")
        print("   Edit organizer.py and replace 'YOUR_API_KEY_HERE' with your actual key.")
        return

    source_folder = Path("TestFolder")
    organize_files(source_folder)
    print("Organization complete!")


if __name__ == "__main__":
    main()