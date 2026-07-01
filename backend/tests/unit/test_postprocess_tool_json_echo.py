"""
Unit tests for BaseAgent.postprocess_response stripping fabricated ```json```
echoes of a tool's clean Markdown result.

Guards the fix where Gemini re-emitted the branch_and_bound tool output wrapped
in a JSON code fence (with escaped \\n) as a preamble before its explanation.
"""

from app.agents.base_agent import BaseAgent


class TestStripToolJsonEcho:
    def test_strips_json_echo_with_escaped_newlines(self):
        response = (
            "Aquí tienes el resultado:\n\n"
            '```json\n{ "branch_and_bound_response": { "output": '
            '"**Ramificación y Acotamiento**\\n\\n| Nodo | Padre |\\n|---|---|\\n| 0 | — |" } }\n```'
            "\n\n**Explicación paso a paso:** empezamos por la relajación LP."
        )
        cleaned = BaseAgent.postprocess_response(response)

        assert "```json" not in cleaned
        assert "\\n" not in cleaned
        assert "branch_and_bound_response" not in cleaned
        assert "Explicación paso a paso" in cleaned
        assert "Aquí tienes el resultado" in cleaned

    def test_strips_inline_json_echo(self):
        response = (
            'Resultado: ```json { "output": "**Solución**\\n\\n**Valor:** 320" } ``` '
            "Ahora lo explico."
        )
        cleaned = BaseAgent.postprocess_response(response)

        assert "```json" not in cleaned
        assert "\\n" not in cleaned
        assert "Ahora lo explico." in cleaned

    def test_preserves_legitimate_json_with_real_newlines(self):
        response = (
            "Tu formulación en JSON:\n\n"
            "```json\n"
            "{\n"
            '  "variables": [{"name": "x1", "type": "integer", "lower": 0}],\n'
            '  "objective": {"sense": "maximize", "expression": "5*x1"}\n'
            "}\n"
            "```\n\n"
            "¿Quieres que lo resuelva?"
        )
        cleaned = BaseAgent.postprocess_response(response)

        assert cleaned == response.strip()
        assert "```json" in cleaned

    def test_plain_text_unchanged(self):
        response = "Branch and bound explora un árbol de subproblemas."
        assert BaseAgent.postprocess_response(response) == response
