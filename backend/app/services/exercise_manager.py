"""
Exercise Manager - Loads and provides access to mathematical modeling exercises.
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Exercise:
    """
    Represents a mathematical modeling exercise.

    Attributes:
        id: Exercise identifier (e.g., "mm_01")
        title: Exercise title extracted from statement
        statement: Full statement Markdown content
        hints: List of hints parsed from statement
        model: Full model/solution Markdown content
        model_type: Type of optimization model (e.g., "PL", "PLI")
    """
    id: str
    title: str
    statement: str
    hints: list[str] = field(default_factory=list)
    model: str = ""
    model_type: str = ""
    difficulty: str = ""
    rank: int = 0
    tier: int = 0


class ExerciseManager:
    """
    Manages loading and accessing mathematical modeling exercises.

    Exercises are stored in directories with the structure:
        exercises_path/
        ├── mm_01/
        │   ├── statement.md
        │   └── model.md
        ├── mm_02/
        │   ├── statement.md
        │   └── model.md
        ...
    """

    def __init__(self, exercises_path: str):
        """
        Initialize the ExerciseManager.

        Args:
            exercises_path: Path to the directory containing exercise folders
        """
        self.exercises_path = exercises_path
        self.exercises: dict[str, Exercise] = {}
        self._load_exercises()

    def _load_exercises(self) -> None:
        """Load all exercises from the exercises directory."""
        if not os.path.exists(self.exercises_path):
            logger.warning(f"Exercises directory not found: {self.exercises_path}")
            return

        # Find all exercise directories (mm_01, mm_02, etc.)
        try:
            entries = os.listdir(self.exercises_path)
        except OSError as e:
            logger.error(f"Error reading exercises directory: {e}")
            return

        # Iterates exercises; loads valid ones; logs errors
        for entry in sorted(entries):
            exercise_dir = os.path.join(self.exercises_path, entry)

            if not os.path.isdir(exercise_dir):
                continue

            # Check for required files
            statement_path = os.path.join(exercise_dir, "statement.md")
            model_path = os.path.join(exercise_dir, "model.md")

            if not os.path.exists(statement_path):
                logger.warning(f"Missing statement.md in {exercise_dir}")
                continue

            try:
                exercise = self._load_exercise(entry, statement_path, model_path)
                if exercise is not None:
                    self.exercises[entry] = exercise
                    logger.info(f"Loaded exercise: {entry} - {exercise.title}")
            except Exception as e:
                logger.error(f"Error loading exercise {entry}: {e}")

        logger.info(f"ExerciseManager loaded {len(self.exercises)} exercises")

    def _load_exercise(
        self, exercise_id: str, statement_path: str, model_path: str
    ) -> Exercise | None:
        """
        Load a single exercise from its files.

        Args:
            exercise_id: The exercise identifier
            statement_path: Path to statement.md
            model_path: Path to model.md

        Returns:
            Exercise object with all data loaded, or None if the exercise is incomplete/template
        """
        # Read statement
        with open(statement_path, encoding="utf-8") as f:
            statement_content = f.read()

        # Check if the statement has actual content (not just template)
        if not self._has_actual_content(statement_content):
            logger.debug(f"Skipping {exercise_id}: statement.md contains only template content")
            return None

        # Parse title from statement
        title = self._parse_title(statement_content)

        # Parse hints from a statement
        hints = self._parse_hints(statement_content)

        # Read the model if it exists
        model_content = ""
        # model_type = ""
        if os.path.exists(model_path):
            with open(model_path, encoding="utf-8") as f:
                model_content = f.read()

            # Check if model has actual content
            if not self._has_actual_content(model_content):
                logger.debug(f"Skipping {exercise_id}: model.md contains only template content")
                return None

            model_type = self._parse_model_type(model_content)
        else:
            # model.md is required for complete exercises
            logger.debug(f"Skipping {exercise_id}: missing model.md")
            return None

        # Read metadata if it exists
        metadata = self._load_metadata(os.path.dirname(statement_path))

        return Exercise(
            id=exercise_id,
            title=title,
            statement=statement_content,
            hints=hints,
            model=model_content,
            model_type=model_type,
            difficulty=metadata.get("difficulty", ""),
            rank=metadata.get("rank", 0),
            tier=metadata.get("tier", 0),
        )

    @staticmethod
    def _load_metadata(exercise_dir: str) -> dict[str, Any]:
        """
        Load metadata from meta-data.json in the exercise directory.

        Args:
            exercise_dir: Path to the exercise directory

        Returns:
            Dictionary with metadata or empty dict if a file doesn't exist
        """
        metadata_path = os.path.join(exercise_dir, "meta-data.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Error reading metadata from {metadata_path}: {e}")
        return {}

    @staticmethod
    def _has_actual_content(content: str) -> bool:
        """
        Check if the content has actual exercise data vs. just template placeholders.

        Returns False if content contains template placeholders or is too short.
        """
        # Template placeholder patterns to detect
        template_markers = [
            "[Enunciado del problema aquí]",
            "[Formulación matemática aquí]",
            "# Título del Ejercicio",
            "# Solución\n\n[",
        ]

        for marker in template_markers:
            if marker in content:
                return False

        # Content should be significant (more than just headers)
        # Remove Markdown headers and check remaining content length
        stripped = re.sub(r'^#+\s.*$', '', content, flags=re.MULTILINE)
        stripped = re.sub(r'<!--.*?-->', '', stripped, flags=re.DOTALL)
        stripped = stripped.strip()

        # Require at least 50 characters of actual content
        return len(stripped) >= 50

    @staticmethod
    def _parse_title(content: str) -> str:
        """
        Parse the title from exercise content.

        Expects a format: # P{n} — {Title}
        """
        match = re.search(r"^#\s*P\d+\s*[—–-]\s*(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Untitled Exercise"

    @staticmethod
    def _parse_hints(content: str) -> list[str]:
        """
        Parse hints from the statement content.

        Looks for the ## Pistas section and extracts bullet points.
        """
        hints = []

        # Find the Pistas section
        pistas_match = re.search(
            r"##\s*Pistas\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE
        )

        if pistas_match:
            pistas_section = pistas_match.group(1)
            # Extract bullet points (- item)
            bullet_pattern = re.compile(r"^\s*[-*]\s*(.+)$", re.MULTILINE)
            for match in bullet_pattern.finditer(pistas_section):
                hint = match.group(1).strip()
                if hint:
                    hints.append(hint)

        return hints

    @staticmethod
    def _parse_model_type(content: str) -> str:
        """
        Parse the model type from model content.

        Looks for ## Tipo de modelo section.
        """
        match = re.search(
            r"##\s*Tipo de modelo\s*\n+(.+?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE
        )
        if match:
            # Get the first non-empty line after the header
            lines = match.group(1).strip().split("\n")
            for line in lines:
                line = line.strip()
                if line:
                    return line
        return ""

    def get_exercise(self, exercise_id: str) -> Exercise | None:
        """
        Get an exercise by its ID.

        Args:
            exercise_id: The exercise identifier (e.g., "mm_01")

        Returns:
            Exercise object or None if not found
        """
        return self.exercises.get(exercise_id)

    def list_exercises(self) -> list[dict[str, Any]]:
        """
        List all available exercises with their metadata.

        Returns:
            List of dictionaries with exercise info (id, title, model_type)
        """
        return [
            {
                "id": ex.id,
                "title": ex.title,
                "model_type": ex.model_type,
                "difficulty": ex.difficulty,
                "rank": ex.rank,
                "tier": ex.tier,
            }
            for ex in self.exercises.values()
        ]

    def get_statement(self, exercise_id: str) -> str | None:
        """
        Get only the statement of an exercise (without a solution).

        Args:
            exercise_id: The exercise identifier

        Returns:
            Statement content or None if exercise is not found
        """
        exercise = self.exercises.get(exercise_id)
        return exercise.statement if exercise else None

    def get_hints(self, exercise_id: str) -> list[str]:
        """
        Get the hints for an exercise.

        Args:
            exercise_id: The exercise identifier

        Returns:
            List of hints or empty list if the exercise is not found
        """
        exercise = self.exercises.get(exercise_id)
        return exercise.hints if exercise else []

    def get_solution(self, exercise_id: str) -> str | None:
        """
        Get the solution/model of an exercise.

        Args:
            exercise_id: The exercise identifier

        Returns:
            Model content or None if exercise is not found
        """
        exercise = self.exercises.get(exercise_id)
        return exercise.model if exercise else None

    def get_hint(self, exercise_id: str, hint_index: int) -> str | None:
        """
        Get a specific hint by index.

        Args:
            exercise_id: The exercise identifier
            hint_index: Zero-based index of the hint

        Returns:
            Hint text or None if not found
        """
        hints = self.get_hints(exercise_id)
        if 0 <= hint_index < len(hints):
            return hints[hint_index]
        return None

    def exercise_exists(self, exercise_id: str) -> bool:
        """Check if an exercise exists."""
        return exercise_id in self.exercises

    def get_exercise_count(self) -> int:
        """Get the number of loaded exercises."""
        return len(self.exercises)
