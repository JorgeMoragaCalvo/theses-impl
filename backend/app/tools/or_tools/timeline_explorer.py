"""
Timeline Explorer Tool for Operations Research history.

This tool allows the OR agent to query historical information about
Operations Research, including milestones, key figures, and eras.
"""

import json
import logging
import os
from typing import Any

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class TimelineExplorerTool(BaseTool):
    """
    Tool for exploring Operations Research history and milestones.

    Searches through a curated database of OR history including
    - Key milestones and breakthroughs
    - Important figures and their contributions
    - Historical eras and their significance
    """

    name: str = "timeline_explorer"
    description: str = """Use this tool to find historical information about Operations Research.
Input can be:
- A topic (e.g., "simplex method", "linear programming origins")
- A time period (e.g., "1940s", "World War II era", "WWII")
- A key figure name (e.g., "Dantzig", "Kantorovich", "von Neumann")

Returns historical information formatted for teaching purposes.
Use this when students ask about OR history, origins, key figures, or timeline."""

    _timeline_data: dict = {}
    _data_loaded: bool = False

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._load_data()

    @staticmethod
    def _get_data_path() -> str:
        """Get the path to the timeline data file."""
        # Navigate from tools/or_tools/ to data/or_history/
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(
            current_dir, "..", "..", "..", "..", "data", "or_history", "timeline.json"
        )
        return os.path.normpath(data_path)

    def _load_data(self) -> None:
        """Load timeline data from JSON file."""
        if self._data_loaded:
            return

        data_path = self._get_data_path()

        try:
            with open(data_path, encoding="utf-8") as f:
                self._timeline_data = json.load(f)
            self._data_loaded = True
            logger.info(f"Timeline data loaded from {data_path}")
        except FileNotFoundError:
            logger.warning(f"Timeline data file not found: {data_path}")
            self._timeline_data = {"milestones": [], "key_figures": [], "eras": []}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing timeline JSON: {e}")
            self._timeline_data = {"milestones": [], "key_figures": [], "eras": []}

    def _run(self, query: str) -> str:
        """
        Execute the timeline search.

        Args:
            query: Search query (topic, figure name, or time period)

        Returns:
            Formatted historical information
        """
        if not self._data_loaded:
            self._load_data()

        query_lower = query.lower().strip()
        results = []

        # Search milestones
        for milestone in self._timeline_data.get("milestones", []):
            if self._matches_milestone(milestone, query_lower):
                results.append(self._format_milestone(milestone))

        # Search key figures
        for figure in self._timeline_data.get("key_figures", []):
            if self._matches_figure(figure, query_lower):
                results.append(self._format_figure(figure))

        # Search eras
        for era in self._timeline_data.get("eras", []):
            if self._matches_era(era, query_lower):
                results.append(self._format_era(era))

        if results:
            return "\n\n---\n\n".join(results)

        return (
            f"No se encontró información histórica para '{query}'.\n"
            "Intenta buscar temas como 'simplex', 'Dantzig', 'Segunda Guerra Mundial', "
            "'programación lineal', '1940s', o 'Kantorovich'."
        )

    @staticmethod
    def _matches_milestone(milestone: dict, query: str) -> bool:
        """Check if a milestone matches the query."""
        searchable = [
            milestone.get("title", "").lower(),
            milestone.get("description", "").lower(),
            str(milestone.get("year", "")),
            milestone.get("decade", "").lower(),
        ]
        # Add tags
        searchable.extend([tag.lower() for tag in milestone.get("tags", [])])
        # Add key figures
        searchable.extend([fig.lower() for fig in milestone.get("key_figures", [])])

        return any(query in field for field in searchable)

    @staticmethod
    def _matches_figure(figure: dict, query: str) -> bool:
        """Check if a key figure matches the query."""
        searchable = [
            figure.get("name", "").lower(),
            figure.get("nationality", "").lower(),
            figure.get("famous_for", "").lower(),
        ]
        # Add contributions
        searchable.extend([c.lower() for c in figure.get("contributions", [])])
        # Add tags
        searchable.extend([tag.lower() for tag in figure.get("tags", [])])

        return any(query in field for field in searchable)

    @staticmethod
    def _matches_era(era: dict, query: str) -> bool:
        """Check if an era matches the query."""
        searchable = [
            era.get("name", "").lower(),
            era.get("period", "").lower(),
            era.get("description", "").lower(),
        ]
        return any(query in field for field in searchable)

    @staticmethod
    def _format_milestone(milestone: dict) -> str:
        """Format a milestone for display."""
        year = milestone.get("year", "?")
        title = milestone.get("title", "Sin título")
        description = milestone.get("description", "")
        significance = milestone.get("significance", "")
        figures = milestone.get("key_figures", [])

        result = f"**{year} - {title}**\n{description}"

        if significance:
            result += f"\n\n*Importancia:* {significance}"

        if figures:
            result += f"\n\n*Figuras clave:* {', '.join(figures)}"

        return result

    @staticmethod
    def _format_figure(figure: dict) -> str:
        """Format a key figure for display."""
        name = figure.get("name", "Desconocido")
        birth = figure.get("birth_year", "?")
        death = figure.get("death_year", "")
        nationality = figure.get("nationality", "")
        famous_for = figure.get("famous_for", "")
        contributions = figure.get("contributions", [])
        fun_fact = figure.get("fun_fact", "")

        years = f"({birth}-{death})" if death else f"(n. {birth})"

        result = f"**{name}** {years}"

        if nationality:
            result += f" - {nationality}"

        if famous_for:
            result += f"\n*Conocido como:* {famous_for}"

        if contributions:
            result += "\n\n*Contribuciones:*"
            for contrib in contributions:
                result += f"\n- {contrib}"

        if fun_fact:
            result += f"\n\n*Dato curioso:* {fun_fact}"

        return result

    @staticmethod
    def _format_era(era: dict) -> str:
        """Format an era for display."""
        name = era.get("name", "Era desconocida")
        period = era.get("period", "")
        description = era.get("description", "")

        result = f"**{name}**"

        if period:
            result += f" ({period})"

        if description:
            result += f"\n{description}"

        return result

    async def _arun(self, query: str) -> str:
        """Async version - just calls sync version since no IO is async."""
        return self._run(query)
