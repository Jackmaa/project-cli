"""Project scaffolding utilities for creating project structures from templates."""

import subprocess
from pathlib import Path
from typing import Literal


ScaffoldResult = Literal["success", "exists", "error", "unsupported"]


def scaffold_project(template_id: str, project_name: str, base_dir: Path) -> tuple[ScaffoldResult, str]:
    """
    Create a project structure from a template.

    Args:
        template_id: The template identifier (e.g., "react-ts", "nextjs", etc.)
        project_name: Name of the project
        base_dir: Base directory where project will be created

    Returns:
        Tuple of (result_status, message)
    """
    project_path = base_dir / project_name

    # Check if path already exists
    if project_path.exists():
        return ("exists", f"Directory {project_path} already exists")

    # Create parent directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)

    # Map of template IDs to scaffold commands
    scaffold_commands = {
        # React - Use Vite instead of CRA (much faster, modern)
        "react": ["npm", "create", "vite@latest", project_name, "--", "--template", "react"],
        "react-ts": ["npm", "create", "vite@latest", project_name, "--", "--template", "react-ts"],

        # Next.js - Add --yes to skip prompts
        "nextjs": ["npx", "create-next-app@latest", project_name, "--js", "--eslint", "--no-tailwind", "--no-src-dir", "--app", "--import-alias", "@/*", "--yes"],
        "nextjs-ts": ["npx", "create-next-app@latest", project_name, "--ts", "--eslint", "--no-tailwind", "--no-src-dir", "--app", "--import-alias", "@/*", "--yes"],

        # Vue
        "vue": ["npm", "create", "vue@latest", project_name],
        "vue-ts": ["npm", "create", "vue@latest", project_name, "--", "--typescript"],

        # Vite-based (faster alternative)
        "vite-react": ["npm", "create", "vite@latest", project_name, "--", "--template", "react"],
        "vite-react-ts": ["npm", "create", "vite@latest", project_name, "--", "--template", "react-ts"],
        "vite-vue": ["npm", "create", "vite@latest", project_name, "--", "--template", "vue"],
        "vite-vue-ts": ["npm", "create", "vite@latest", project_name, "--", "--template", "vue-ts"],
        "svelte": ["npm", "create", "vite@latest", project_name, "--", "--template", "svelte"],

        # T3 Stack
        "t3": ["npx", "create-t3-app@latest", project_name, "--noGit"],

        # Python
        "python": None,  # Will create basic structure manually
        "python-django": None,  # Will use django-admin
        "python-flask": None,  # Will create basic Flask structure
        "python-fastapi": None,  # Will create basic FastAPI structure

        # Node/Express
        "express": None,  # Will create basic Express structure
        "nestjs": ["npx", "@nestjs/cli", "new", project_name, "--skip-git"],

        # Mobile
        "react-native": ["npx", "react-native", "init", project_name],
        "flutter": ["flutter", "create", project_name],

        # Rust
        "rust": ["cargo", "new", project_name],

        # Go
        "go": None,  # Will create basic Go structure
    }

    if template_id not in scaffold_commands:
        return ("unsupported", f"Template '{template_id}' does not support automatic scaffolding")

    command = scaffold_commands[template_id]

    # Handle manual scaffolding
    if command is None:
        result = _manual_scaffold(template_id, project_path)
        return result

    # Run scaffold command
    try:
        # Use stdin=subprocess.DEVNULL to prevent interactive prompts
        # Use a reasonable timeout to prevent hanging
        result = subprocess.run(
            command,
            cwd=base_dir,
            check=True,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=300  # 5 minute timeout
        )
        return ("success", f"Created project at {project_path}")
    except subprocess.TimeoutExpired:
        return ("error", f"Scaffolding timed out after 5 minutes")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr if e.stderr else "Unknown error"
        return ("error", f"Failed to create project: {stderr[:200]}")
    except FileNotFoundError:
        tool = command[0]
        return ("error", f"Tool '{tool}' not found. Please install it first.")


def _manual_scaffold(template_id: str, project_path: Path) -> tuple[ScaffoldResult, str]:
    """Create project structure manually for templates without CLI tools."""

    try:
        project_path.mkdir(parents=True, exist_ok=False)

        if template_id == "python":
            _create_python_project(project_path)
        elif template_id == "python-django":
            _create_django_project(project_path)
        elif template_id == "python-flask":
            _create_flask_project(project_path)
        elif template_id == "python-fastapi":
            _create_fastapi_project(project_path)
        elif template_id == "express":
            _create_express_project(project_path)
        elif template_id == "go":
            _create_go_project(project_path)
        else:
            # Create basic structure
            (project_path / "README.md").write_text(f"# {project_path.name}\n")

        return ("success", f"Created project at {project_path}")
    except Exception as e:
        return ("error", f"Failed to create project: {str(e)}")


def _create_python_project(path: Path):
    """Create basic Python project structure."""
    # Create directories
    (path / "src").mkdir()
    (path / "tests").mkdir()

    # Create files
    (path / "README.md").write_text(f"# {path.name}\n")
    (path / "requirements.txt").write_text("")
    (path / ".gitignore").write_text("__pycache__/\n*.py[cod]\n*$py.class\n.venv/\nvenv/\n.env\n")
    (path / "src" / "__init__.py").write_text("")


def _create_django_project(path: Path):
    """Create Django project using django-admin."""
    try:
        subprocess.run(
            ["django-admin", "startproject", "config", "."],
            cwd=path,
            check=True,
            capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: create basic structure
        _create_python_project(path)
        (path / "manage.py").write_text("# Django manage.py placeholder\n")


def _create_flask_project(path: Path):
    """Create basic Flask project structure."""
    (path / "app").mkdir()
    (path / "static").mkdir()
    (path / "templates").mkdir()

    (path / "README.md").write_text(f"# {path.name}\n\nFlask application\n")
    (path / "requirements.txt").write_text("flask\n")
    (path / ".gitignore").write_text("__pycache__/\n*.py[cod]\n.venv/\nvenv/\n.env\n")

    (path / "app" / "__init__.py").write_text(
        'from flask import Flask\n\n'
        'app = Flask(__name__)\n\n'
        'from app import routes\n'
    )
    (path / "app" / "routes.py").write_text(
        'from app import app\n\n'
        '@app.route("/")\n'
        'def index():\n'
        '    return "Hello, World!"\n'
    )
    (path / "run.py").write_text(
        'from app import app\n\n'
        'if __name__ == "__main__":\n'
        '    app.run(debug=True)\n'
    )


def _create_fastapi_project(path: Path):
    """Create basic FastAPI project structure."""
    (path / "app").mkdir()

    (path / "README.md").write_text(f"# {path.name}\n\nFastAPI application\n")
    (path / "requirements.txt").write_text("fastapi\nuvicorn[standard]\n")
    (path / ".gitignore").write_text("__pycache__/\n*.py[cod]\n.venv/\nvenv/\n.env\n")

    (path / "app" / "__init__.py").write_text("")
    (path / "app" / "main.py").write_text(
        'from fastapi import FastAPI\n\n'
        'app = FastAPI()\n\n'
        '@app.get("/")\n'
        'async def root():\n'
        '    return {"message": "Hello World"}\n'
    )
    (path / "main.py").write_text(
        'import uvicorn\n\n'
        'if __name__ == "__main__":\n'
        '    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)\n'
    )


def _create_express_project(path: Path):
    """Create basic Express.js project structure."""
    (path / "src").mkdir()
    (path / "public").mkdir()

    (path / "README.md").write_text(f"# {path.name}\n\nExpress.js application\n")
    (path / ".gitignore").write_text("node_modules/\n.env\n")

    (path / "package.json").write_text(
        '{\n'
        f'  "name": "{path.name}",\n'
        '  "version": "1.0.0",\n'
        '  "main": "src/index.js",\n'
        '  "scripts": {\n'
        '    "start": "node src/index.js",\n'
        '    "dev": "nodemon src/index.js"\n'
        '  },\n'
        '  "dependencies": {\n'
        '    "express": "^4.18.2"\n'
        '  },\n'
        '  "devDependencies": {\n'
        '    "nodemon": "^3.0.1"\n'
        '  }\n'
        '}\n'
    )

    (path / "src" / "index.js").write_text(
        'const express = require("express");\n'
        'const app = express();\n'
        'const port = process.env.PORT || 3000;\n\n'
        'app.get("/", (req, res) => {\n'
        '  res.send("Hello World!");\n'
        '});\n\n'
        'app.listen(port, () => {\n'
        '  console.log(`Server running on port ${port}`);\n'
        '});\n'
    )


def _create_go_project(path: Path):
    """Create basic Go project structure."""
    (path / "cmd").mkdir()
    (path / "cmd" / path.name).mkdir()
    (path / "internal").mkdir()
    (path / "pkg").mkdir()

    (path / "README.md").write_text(f"# {path.name}\n")
    (path / ".gitignore").write_text("*.exe\n*.exe~\n*.dll\n*.so\n*.dylib\n")
    (path / "go.mod").write_text(f"module {path.name}\n\ngo 1.21\n")
    (path / "cmd" / path.name / "main.go").write_text(
        'package main\n\n'
        'import "fmt"\n\n'
        'func main() {\n'
        '    fmt.Println("Hello, World!")\n'
        '}\n'
    )
