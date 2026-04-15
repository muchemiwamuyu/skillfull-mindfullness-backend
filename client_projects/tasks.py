import os
import json
import shutil
import tempfile
import subprocess
from datetime import datetime, timezone

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def scaffold_project_task(self, project_id: int):
    from .models import ClientProject  # local import — avoids app registry issues

    try:
        project = ClientProject.objects.get(pk=project_id)
    except ClientProject.DoesNotExist:
        logger.error(f"ClientProject {project_id} not found.")
        return

    if not project.repo_url:
        _fail(project, "No repo URL provided.")
        return

    tmp_dir = tempfile.mkdtemp(prefix=f"scaffold_{project_id}_")

    try:
        # ── 1. CLONE ──────────────────────────────────────────────────
        _set_status(project, "cloning")
        clone_url = _build_clone_url(project)

        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", project.repo_branch, clone_url, tmp_dir],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")

        # ── 2. ANALYZE ────────────────────────────────────────────────
        _set_status(project, "analyzing")

        detected_stack = _detect_stack(tmp_dir)
        scaffold_output = _build_file_tree(tmp_dir)
        scaffold_graph = _build_graph(scaffold_output)
        error_flags = _detect_error_flags(tmp_dir, scaffold_output)
        completeness_score = _score_completeness(tmp_dir, scaffold_output)
        integrity_score = _score_integrity(error_flags)

        # ── 3. SAVE RESULTS ───────────────────────────────────────────
        project.scaffold_status = "scaffolded"
        project.detected_stack = detected_stack
        project.scaffold_output = scaffold_output
        project.scaffold_graph = scaffold_graph
        project.error_flags = error_flags
        project.completeness_score = completeness_score
        project.integrity_score = integrity_score
        project.scaffold_error = None
        project.scaffolded_at = datetime.now(tz=timezone.utc)
        project.save(update_fields=[
            "scaffold_status", "detected_stack", "scaffold_output",
            "scaffold_graph", "error_flags", "completeness_score",
            "integrity_score", "scaffold_error", "scaffolded_at", "updated_at",
        ])

        logger.info(f"Scaffolded project {project_id} successfully.")

    except Exception as exc:
        logger.exception(f"Scaffold failed for project {project_id}: {exc}")
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            _fail(project, str(exc))

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _set_status(project, status: str):
    project.scaffold_status = status
    project.save(update_fields=["scaffold_status", "updated_at"])


def _fail(project, error: str):
    project.scaffold_status = "failed"
    project.scaffold_error = error
    project.save(update_fields=["scaffold_status", "scaffold_error", "updated_at"])


def _build_clone_url(project) -> str:
    """Inject access token into URL for private repos."""
    url = project.repo_url
    if project.repo_access_token:
        # https://token@github.com/user/repo
        proto, rest = url.split("://", 1)
        url = f"{proto}://{project.repo_access_token}@{rest}"
    return url


def _detect_stack(path: str) -> dict:
    stack = {}
    files = os.listdir(path)

    if "package.json" in files:
        try:
            with open(os.path.join(path, "package.json")) as f:
                pkg = json.load(f)
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            stack["language"] = "TypeScript" if "typescript" in deps else "JavaScript"
            if "next" in deps:
                stack["framework"] = "Next.js"
            elif "react" in deps:
                stack["framework"] = "React"
            elif "vue" in deps:
                stack["framework"] = "Vue"
            elif "express" in deps:
                stack["framework"] = "Express"
            stack["runtime"] = "Node.js"
        except Exception:
            stack["runtime"] = "Node.js"

    if "requirements.txt" in files or "pyproject.toml" in files:
        stack["language"] = "Python"
        if "manage.py" in files:
            stack["framework"] = "Django"
        elif "main.py" in files:
            stack["framework"] = "FastAPI / Flask"

    if "pubspec.yaml" in files:
        stack["language"] = "Dart"
        stack["framework"] = "Flutter"

    if "go.mod" in files:
        stack["language"] = "Go"

    if "Dockerfile" in files:
        stack["containerized"] = True

    if "docker-compose.yml" in files or "docker-compose.yaml" in files:
        stack["compose"] = True

    return stack


def _build_file_tree(base_path: str, max_depth: int = 4) -> dict:
    """Recursively builds a file tree dict."""
    tree = {"name": os.path.basename(base_path), "type": "dir", "children": []}
    IGNORE = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", ".next", "build"}

    def walk(current_path, node, depth):
        if depth > max_depth:
            return
        try:
            entries = sorted(os.scandir(current_path), key=lambda e: (e.is_file(), e.name))
        except PermissionError:
            return
        for entry in entries:
            if entry.name in IGNORE:
                continue
            if entry.is_dir():
                child = {"name": entry.name, "type": "dir", "children": []}
                node["children"].append(child)
                walk(entry.path, child, depth + 1)
            else:
                node["children"].append({"name": entry.name, "type": "file"})

    walk(base_path, tree, 1)
    return tree


def _build_graph(file_tree: dict) -> dict:
    """Flatten the file tree into graph nodes and edges for the frontend."""
    nodes, edges = [], []
    counter = {"id": 0}

    def traverse(node, parent_id=None):
        node_id = counter["id"]
        counter["id"] += 1
        nodes.append({"id": node_id, "label": node["name"], "type": node["type"]})
        if parent_id is not None:
            edges.append({"source": parent_id, "target": node_id})
        for child in node.get("children", []):
            traverse(child, node_id)

    traverse(file_tree)
    return {"nodes": nodes, "edges": edges}


def _detect_error_flags(path: str, tree: dict) -> list:
    flags = []
    top_level = {c["name"] for c in tree.get("children", [])}

    if ".env" not in top_level and ".env.example" not in top_level:
        flags.append("missing .env or .env.example")
    if not any(n in top_level for n in ["tests", "test", "__tests__", "spec"]):
        flags.append("no test suite detected")
    if "README.md" not in top_level and "README" not in top_level:
        flags.append("missing README")
    if ".gitignore" not in top_level:
        flags.append("missing .gitignore")

    return flags


def _score_completeness(path: str, tree: dict) -> float:
    top_level = {c["name"] for c in tree.get("children", [])}
    checks = [
        "README.md" in top_level or "README" in top_level,
        ".gitignore" in top_level,
        any(n in top_level for n in ["tests", "test", "__tests__"]),
        ".env.example" in top_level,
        any(n in top_level for n in ["Dockerfile", "docker-compose.yml"]),
        len(tree.get("children", [])) > 3,  # has some structure
    ]
    return round(sum(checks) / len(checks), 2)


def _score_integrity(error_flags: list) -> float:
    penalty = len(error_flags) * 0.15
    return round(max(0.0, 1.0 - penalty), 2)