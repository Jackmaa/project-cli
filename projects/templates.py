"""Project templates with language and framework configurations."""

from typing import TypedDict


class ProjectTemplate(TypedDict):
    """Template configuration for a project type."""
    name: str
    language: str
    tags: list[str]
    description: str
    scaffold_command: str | None  # Command to create project structure
    scaffold_note: str | None  # Note about what will be created


# Define all available templates
TEMPLATES: dict[str, ProjectTemplate] = {
    # Python Templates
    "python": {
        "name": "Python",
        "language": "Python",
        "tags": ["python"],
        "description": "General Python project",
        "scaffold_command": None,
        "scaffold_note": "Create basic Python project structure"
    },
    "python-django": {
        "name": "Python + Django",
        "language": "Python",
        "tags": ["python", "django", "web", "backend"],
        "description": "Django web framework"
    },
    "python-flask": {
        "name": "Python + Flask",
        "language": "Python",
        "tags": ["python", "flask", "web", "backend"],
        "description": "Flask web framework"
    },
    "python-fastapi": {
        "name": "Python + FastAPI",
        "language": "Python",
        "tags": ["python", "fastapi", "web", "backend", "api"],
        "description": "FastAPI framework"
    },
    "python-ml": {
        "name": "Python + ML/AI",
        "language": "Python",
        "tags": ["python", "ml", "ai", "data-science"],
        "description": "Machine Learning/AI project"
    },

    # JavaScript/TypeScript Templates
    "javascript": {
        "name": "JavaScript",
        "language": "JavaScript",
        "tags": ["javascript"],
        "description": "General JavaScript project"
    },
    "typescript": {
        "name": "TypeScript",
        "language": "TypeScript",
        "tags": ["typescript"],
        "description": "General TypeScript project"
    },
    "react": {
        "name": "React (Vite)",
        "language": "JavaScript",
        "tags": ["react", "vite", "frontend", "web"],
        "description": "React application with Vite"
    },
    "react-ts": {
        "name": "React + TypeScript (Vite)",
        "language": "TypeScript",
        "tags": ["react", "typescript", "vite", "frontend", "web"],
        "description": "React with TypeScript and Vite"
    },
    "nextjs": {
        "name": "Next.js",
        "language": "JavaScript",
        "tags": ["nextjs", "react", "frontend", "web", "ssr"],
        "description": "Next.js framework"
    },
    "nextjs-ts": {
        "name": "Next.js + TypeScript",
        "language": "TypeScript",
        "tags": ["nextjs", "react", "typescript", "frontend", "web", "ssr"],
        "description": "Next.js with TypeScript"
    },
    "vue": {
        "name": "Vue.js",
        "language": "JavaScript",
        "tags": ["vue", "frontend", "web"],
        "description": "Vue.js application"
    },
    "vue-ts": {
        "name": "Vue.js + TypeScript",
        "language": "TypeScript",
        "tags": ["vue", "typescript", "frontend", "web"],
        "description": "Vue.js with TypeScript"
    },
    "svelte": {
        "name": "Svelte",
        "language": "JavaScript",
        "tags": ["svelte", "frontend", "web"],
        "description": "Svelte application"
    },
    "nodejs": {
        "name": "Node.js",
        "language": "JavaScript",
        "tags": ["nodejs", "backend", "javascript"],
        "description": "Node.js backend"
    },
    "express": {
        "name": "Express.js",
        "language": "JavaScript",
        "tags": ["express", "nodejs", "backend", "web", "api"],
        "description": "Express.js framework"
    },
    "nestjs": {
        "name": "NestJS",
        "language": "TypeScript",
        "tags": ["nestjs", "nodejs", "typescript", "backend", "web", "api"],
        "description": "NestJS framework"
    },

    # CSS/Styling
    "tailwind": {
        "name": "Tailwind CSS",
        "language": "CSS",
        "tags": ["tailwind", "css", "frontend"],
        "description": "Tailwind CSS project"
    },

    # Full Stack Templates
    "mern": {
        "name": "MERN Stack",
        "language": "JavaScript",
        "tags": ["mern", "mongodb", "express", "react", "nodejs", "fullstack"],
        "description": "MongoDB + Express + React + Node.js"
    },
    "mean": {
        "name": "MEAN Stack",
        "language": "JavaScript",
        "tags": ["mean", "mongodb", "express", "angular", "nodejs", "fullstack"],
        "description": "MongoDB + Express + Angular + Node.js"
    },
    "t3": {
        "name": "T3 Stack",
        "language": "TypeScript",
        "tags": ["t3", "nextjs", "typescript", "trpc", "prisma", "tailwind", "fullstack"],
        "description": "Next.js + TypeScript + tRPC + Prisma + Tailwind"
    },

    # Other Languages
    "rust": {
        "name": "Rust",
        "language": "Rust",
        "tags": ["rust"],
        "description": "Rust project"
    },
    "go": {
        "name": "Go",
        "language": "Go",
        "tags": ["go", "golang"],
        "description": "Go project"
    },
    "java": {
        "name": "Java",
        "language": "Java",
        "tags": ["java"],
        "description": "Java project"
    },
    "spring": {
        "name": "Spring Boot",
        "language": "Java",
        "tags": ["java", "spring", "spring-boot", "backend"],
        "description": "Spring Boot framework"
    },
    "csharp": {
        "name": "C#",
        "language": "C#",
        "tags": ["csharp", "dotnet"],
        "description": "C# project"
    },
    "dotnet": {
        "name": ".NET",
        "language": "C#",
        "tags": ["csharp", "dotnet", "backend"],
        "description": ".NET framework"
    },
    "ruby": {
        "name": "Ruby",
        "language": "Ruby",
        "tags": ["ruby"],
        "description": "Ruby project"
    },
    "rails": {
        "name": "Ruby on Rails",
        "language": "Ruby",
        "tags": ["ruby", "rails", "web", "backend"],
        "description": "Ruby on Rails framework"
    },
    "php": {
        "name": "PHP",
        "language": "PHP",
        "tags": ["php"],
        "description": "PHP project"
    },
    "laravel": {
        "name": "Laravel",
        "language": "PHP",
        "tags": ["php", "laravel", "web", "backend"],
        "description": "Laravel framework"
    },

    # Mobile
    "react-native": {
        "name": "React Native",
        "language": "JavaScript",
        "tags": ["react-native", "mobile", "react"],
        "description": "React Native mobile app"
    },
    "flutter": {
        "name": "Flutter",
        "language": "Dart",
        "tags": ["flutter", "dart", "mobile"],
        "description": "Flutter mobile app"
    },
    "swift": {
        "name": "Swift",
        "language": "Swift",
        "tags": ["swift", "ios", "mobile"],
        "description": "Swift iOS app"
    },
    "kotlin": {
        "name": "Kotlin",
        "language": "Kotlin",
        "tags": ["kotlin", "android", "mobile"],
        "description": "Kotlin Android app"
    },

    # Other
    "custom": {
        "name": "Custom",
        "language": "",
        "tags": [],
        "description": "Custom project (manual configuration)"
    },
}


def get_template(template_id: str) -> ProjectTemplate | None:
    """Get a template by ID."""
    return TEMPLATES.get(template_id)


def get_all_templates() -> list[tuple[str, ProjectTemplate]]:
    """Get all templates as (id, template) pairs."""
    return list(TEMPLATES.items())


def get_templates_by_category() -> dict[str, list[tuple[str, str]]]:
    """
    Get templates organized by category for UI display.
    Returns: dict[category_name, list[(template_id, template_name)]]
    """
    return {
        "Python": [
            ("python", "Python"),
            ("python-django", "Python + Django"),
            ("python-flask", "Python + Flask"),
            ("python-fastapi", "Python + FastAPI"),
            ("python-ml", "Python + ML/AI"),
        ],
        "JavaScript": [
            ("javascript", "JavaScript"),
            ("nodejs", "Node.js"),
            ("express", "Express.js"),
        ],
        "TypeScript": [
            ("typescript", "TypeScript"),
            ("nestjs", "NestJS"),
        ],
        "Frontend": [
            ("react", "React (Vite)"),
            ("react-ts", "React + TypeScript (Vite)"),
            ("nextjs", "Next.js"),
            ("nextjs-ts", "Next.js + TypeScript"),
            ("vue", "Vue.js"),
            ("vue-ts", "Vue.js + TypeScript"),
            ("svelte", "Svelte"),
            ("tailwind", "Tailwind CSS"),
        ],
        "Full Stack": [
            ("mern", "MERN Stack"),
            ("mean", "MEAN Stack"),
            ("t3", "T3 Stack"),
        ],
        "Mobile": [
            ("react-native", "React Native"),
            ("flutter", "Flutter"),
            ("swift", "Swift (iOS)"),
            ("kotlin", "Kotlin (Android)"),
        ],
        "Other Languages": [
            ("rust", "Rust"),
            ("go", "Go"),
            ("java", "Java"),
            ("spring", "Spring Boot"),
            ("csharp", "C#"),
            ("dotnet", ".NET"),
            ("ruby", "Ruby"),
            ("rails", "Ruby on Rails"),
            ("php", "PHP"),
            ("laravel", "Laravel"),
        ],
        "Other": [
            ("custom", "Custom"),
        ],
    }
