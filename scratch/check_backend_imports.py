import ast
import glob
import os
import sys

stdlib = sys.stdlib_module_names

requirements_pkgs = {
    "fastapi", "uvicorn", "pydantic", "pydantic_settings",
    "sqlalchemy", "bcrypt", "jwt", "pyjwt", "multipart",
    "python_multipart", "httpx", "pytest", "requests"
}

imported_pkgs = set()
for f in glob.glob("backend/app/**/*.py", recursive=True):
    try:
        tree = ast.parse(open(f, encoding="utf-8").read(), filename=f)
    except Exception:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split(".")[0]
                imported_pkgs.add(root_pkg)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split(".")[0]
                imported_pkgs.add(root_pkg)

third_party = set()
for pkg in imported_pkgs:
    if pkg not in stdlib and pkg not in {"app", "scripts", "conftest"}:
        third_party.add(pkg)

print("All third-party packages imported in backend/app:")
for p in sorted(third_party):
    in_req = p in requirements_pkgs or p in {"starlette"} # starlette is bundled with fastapi
    print(f"  {p:<20} in requirements.txt? {in_req}")

