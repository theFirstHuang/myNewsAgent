"""Tests for overall project structure."""

import pytest
from pathlib import Path


class TestProjectStructure:
    """Test project has correct structure."""

    def test_required_files_exist(self):
        """Test all required files exist."""
        required_files = [
            "README.md",
            "requirements.txt",
            "setup.py",
            ".gitignore",
            ".env.example",
            "config.yaml.example",
            "my_research.md.example"
        ]

        for filename in required_files:
            filepath = Path(filename)
            assert filepath.exists(), f"Required file missing: {filename}"

    def test_source_directories_exist(self):
        """Test all source directories exist."""
        required_dirs = [
            "src",
            "src/fetchers",
            "src/analyzers",
            "src/processors",
            "src/summarizers",
            "src/generators",
            "src/notifiers",
            "src/utils",
            "templates",
            "scripts"
        ]

        for dirname in required_dirs:
            dirpath = Path(dirname)
            assert dirpath.exists(), f"Required directory missing: {dirname}"

    def test_all_modules_have_init(self):
        """Test all Python packages have __init__.py."""
        package_dirs = [
            "src",
            "src/fetchers",
            "src/analyzers",
            "src/processors",
            "src/summarizers",
            "src/generators",
            "src/notifiers",
            "src/utils"
        ]

        for dirname in package_dirs:
            init_file = Path(dirname) / "__init__.py"
            assert init_file.exists(), f"Missing __init__.py in {dirname}"

    def test_scripts_are_executable(self):
        """Test script files exist and have proper structure."""
        scripts = [
            "scripts/run_digest.py",
            "scripts/test_email.py",
            "scripts/setup_cron.sh"
        ]

        for script in scripts:
            script_path = Path(script)
            assert script_path.exists(), f"Script missing: {script}"

            # Check shebang for Python scripts
            if script.endswith('.py'):
                with open(script_path, 'r') as f:
                    first_line = f.readline()
                    assert first_line.startswith('#!'), f"Missing shebang in {script}"

    def test_templates_exist(self):
        """Test all email templates exist."""
        templates = [
            "templates/email_modern.html",
            "templates/email_academic.html",
            "templates/email_minimal.html",
            "templates/preview.html"
        ]

        for template in templates:
            template_path = Path(template)
            assert template_path.exists(), f"Template missing: {template}"

    def test_requirements_file_valid(self):
        """Test requirements.txt is valid."""
        req_file = Path("requirements.txt")
        assert req_file.exists()

        with open(req_file, 'r') as f:
            lines = f.readlines()

        # Should have at least some dependencies
        non_comment_lines = [l for l in lines if l.strip() and not l.startswith('#')]
        assert len(non_comment_lines) >= 10, "requirements.txt seems incomplete"

        # Check for key dependencies
        content = '\n'.join(lines)
        key_deps = ['arxiv', 'openai', 'jinja2', 'pyyaml']
        for dep in key_deps:
            assert dep in content, f"Missing key dependency: {dep}"

    def test_readme_has_content(self):
        """Test README has substantial content."""
        readme = Path("README.md")
        assert readme.exists()

        content = readme.read_text()
        assert len(content) > 1000, "README seems too short"
        assert "LLM News Digest Agent" in content
        assert "Installation" in content or "installation" in content
