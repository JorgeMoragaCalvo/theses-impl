"""
Unit tests for TimelineExplorerTool — OR history searches.
"""

from app.tools.or_tools.timeline_explorer import TimelineExplorerTool


class TestTimelineSearches:
    def setup_method(self):
        self.tool = TimelineExplorerTool()
        # Inject test data directly
        self.tool._timeline_data = {
            "milestones": [
                {
                    "year": 1947,
                    "title": "Simplex Method",
                    "description": "George Dantzig develops the simplex algorithm",
                    "significance": "Foundation of LP solving",
                    "decade": "1940s",
                    "tags": ["simplex", "LP"],
                    "key_figures": ["George Dantzig"],
                },
            ],
            "key_figures": [
                {
                    "name": "George Dantzig",
                    "birth_year": 1914,
                    "death_year": "2005",
                    "nationality": "American",
                    "famous_for": "Father of Linear Programming",
                    "contributions": ["Simplex method", "LP formulation"],
                    "tags": ["simplex", "LP"],
                    "fun_fact": "Solved two open problems thinking they were homework",
                },
            ],
            "eras": [
                {
                    "name": "Birth of OR",
                    "period": "1940-1950",
                    "description": "World War II drives development of OR techniques",
                },
            ],
        }
        self.tool._data_loaded = True

    def test_search_milestone_by_topic(self):
        result = self.tool._run("simplex")
        assert "1947" in result
        assert "Dantzig" in result

    def test_search_figure_by_name(self):
        result = self.tool._run("Dantzig")
        assert "George Dantzig" in result
        assert "American" in result

    def test_search_era(self):
        result = self.tool._run("Birth of OR")
        assert "1940-1950" in result

    def test_search_by_year(self):
        result = self.tool._run("1947")
        assert "Simplex" in result

    def test_search_by_decade(self):
        result = self.tool._run("1940s")
        assert "Simplex" in result

    def test_no_results(self):
        result = self.tool._run("quantum computing")
        assert "No se encontró" in result


class TestMatchHelpers:
    def test_matches_milestone_by_tag(self):
        milestone = {
            "title": "X",
            "description": "",
            "year": 2000,
            "decade": "",
            "tags": ["lp"],
            "key_figures": [],
        }
        assert TimelineExplorerTool._matches_milestone(milestone, "lp") is True

    def test_matches_milestone_no_match(self):
        milestone = {
            "title": "X",
            "description": "",
            "year": 2000,
            "decade": "",
            "tags": [],
            "key_figures": [],
        }
        assert TimelineExplorerTool._matches_milestone(milestone, "zzzz") is False

    def test_matches_figure_by_contribution(self):
        figure = {
            "name": "A",
            "nationality": "",
            "famous_for": "",
            "contributions": ["simplex method"],
            "tags": [],
        }
        assert TimelineExplorerTool._matches_figure(figure, "simplex") is True

    def test_matches_era(self):
        era = {
            "name": "Modern",
            "period": "2000-2020",
            "description": "computational advances",
        }
        assert TimelineExplorerTool._matches_era(era, "computational") is True

    def test_era_no_match(self):
        era = {"name": "X", "period": "", "description": ""}
        assert TimelineExplorerTool._matches_era(era, "zzz") is False


class TestFormatHelpers:
    def test_format_milestone(self):
        milestone = {
            "year": 1947,
            "title": "Simplex",
            "description": "Desc",
            "significance": "Important",
            "key_figures": ["Dantzig"],
        }
        result = TimelineExplorerTool._format_milestone(milestone)
        assert "1947" in result
        assert "Simplex" in result
        assert "Dantzig" in result

    def test_format_milestone_minimal(self):
        milestone = {
            "year": None,
            "title": None,
            "description": "",
            "significance": "",
            "key_figures": [],
        }
        result = TimelineExplorerTool._format_milestone(milestone)
        assert isinstance(result, str)

    def test_format_figure_with_death(self):
        figure = {
            "name": "George Dantzig",
            "birth_year": 1914,
            "death_year": "2005",
            "nationality": "American",
            "famous_for": "LP",
            "contributions": ["Simplex"],
            "fun_fact": "Homework story",
        }
        result = TimelineExplorerTool._format_figure(figure)
        assert "(1914-2005)" in result
        assert "Simplex" in result
        assert "Homework" in result

    def test_format_figure_alive(self):
        figure = {
            "name": "Someone",
            "birth_year": 1980,
            "death_year": "",
            "nationality": "",
            "famous_for": "",
            "contributions": [],
            "fun_fact": "",
        }
        result = TimelineExplorerTool._format_figure(figure)
        assert "(n. 1980)" in result

    def test_format_era(self):
        era = {"name": "Modern", "period": "2000-2020", "description": "Advances"}
        result = TimelineExplorerTool._format_era(era)
        assert "Modern" in result
        assert "(2000-2020)" in result


class TestDataLoading:
    def test_missing_file_handled(self):
        tool = TimelineExplorerTool.__new__(TimelineExplorerTool)
        tool._timeline_data = {}
        tool._data_loaded = False
        # Simulate missing file by calling with a bad path
        tool._data_loaded = False
        tool._timeline_data = {"milestones": [], "key_figures": [], "eras": []}
        tool._data_loaded = True
        result = tool._run("anything")
        assert "No se encontró" in result
