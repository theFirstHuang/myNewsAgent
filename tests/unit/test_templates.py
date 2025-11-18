"""Tests for email templates."""

import pytest
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateError


class TestEmailTemplates:
    """Test email templates."""

    def test_all_templates_exist(self):
        """Test all three templates exist."""
        template_dir = Path("templates")
        assert template_dir.exists()

        templates = ["email_modern.html", "email_academic.html", "email_minimal.html"]

        for template_name in templates:
            template_path = template_dir / template_name
            assert template_path.exists(), f"Template not found: {template_name}"

    def test_templates_valid_jinja2(self):
        """Test templates are valid Jinja2."""
        template_dir = Path("templates")
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        templates = ["email_modern.html", "email_academic.html", "email_minimal.html"]

        for template_name in templates:
            try:
                template = env.get_template(template_name)
                assert template is not None
            except TemplateError as e:
                pytest.fail(f"Template {template_name} has syntax errors: {e}")

    def test_template_variables(self):
        """Test templates use expected variables."""
        template_dir = Path("templates")

        required_vars = [
            '{{ date_range }}',
            '{{ total_papers }}',
            '{{ papers }}'
        ]

        templates = ["email_modern.html", "email_academic.html", "email_minimal.html"]

        for template_name in templates:
            template_path = template_dir / template_name
            content = template_path.read_text()

            for var in required_vars:
                # Check if variable or loop exists
                assert '{{ papers' in content or '{% for paper in papers %}' in content, \
                    f"Template {template_name} missing variable usage"

    def test_template_rendering(self):
        """Test templates can be rendered with sample data."""
        template_dir = Path("templates")
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        sample_data = {
            'date_range': 'Nov 15 - Nov 22, 2024',
            'total_papers': 3,
            'relevant_papers': 2,
            'papers': [
                {
                    'title': 'Test Paper 1',
                    'authors': 'Author 1 et al.',
                    'abstract': 'Test abstract 1',
                    'arxiv_url': 'https://arxiv.org/abs/2401.12345',
                    'pdf_url': 'https://arxiv.org/pdf/2401.12345',
                    'arxiv_id': '2401.12345',
                    'date': 'Nov 15, 2024',
                    'category': 'cs.CL',
                    'relevance_score': 0.85,
                    'summary': {
                        'key_points': ['Point 1', 'Point 2'],
                        'methodology': 'Test methodology',
                        'relevance_reason': 'Test reason'
                    }
                }
            ],
            'generation_time': '2024-11-18 10:00:00'
        }

        templates = ["email_modern.html", "email_academic.html", "email_minimal.html"]

        for template_name in templates:
            template = env.get_template(template_name)
            try:
                html = template.render(**sample_data)
                assert len(html) > 1000, f"Template {template_name} rendered too short"
                assert 'Test Paper 1' in html
            except Exception as e:
                pytest.fail(f"Failed to render {template_name}: {e}")

    def test_preview_html_exists(self):
        """Test preview.html exists."""
        preview_path = Path("templates/preview.html")
        assert preview_path.exists()
