"""Install the personal document skill, with preflight and recoverable migration.

Does not edit CLAUDE.md, install dependencies, register document collections or
create a routine. Those steps require the guided setup's explicit approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import uuid

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "dokumenti/scripts"))
from indeks import safe_path, write, blob

FILES = ("SKILL.md", "scripts/dokumenti.py", "scripts/indeks.py", "requirements.txt")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def install(home, workspace, approved=False, migrate=False):
    if not approved:
        raise ValueError("Manjka potrditev osebne namestitve.")
    home, workspace = safe_path(home), safe_path(workspace)
    target = home / ".claude/skills/dokumenti"
    safe_path(target)
    payload = {n: blob(SOURCE / "dokumenti" / n) for n in FILES}
    marker = target / ".starter-manifest.json"
    old_hashes = json.loads(blob(marker)) if marker.exists() else {}
    backup = home / ".claude-work-starter/backups" / uuid.uuid4().hex
    replacements = {}
    # Check every destination before changing anything, including customized project skills.
    if target.exists():
        allowed = {*FILES, ".starter-manifest.json"}
        for file in target.rglob("*"):
            safe_path(file)
            if file.is_file() and file.relative_to(target).as_posix() not in allowed:
                if "__pycache__" not in file.parts:
                    raise ValueError("Osebni skill vsebuje dodatne datoteke; potreben je pregled izvajalca.")
    for name, data in payload.items():
        path = safe_path(target / name)
        if path.exists():
            old = blob(path)
            if old != data:
                if digest(old) != old_hashes.get(name):
                    raise ValueError("Prilagojen osebni skill ni prepisan: " + name)
                replacements[name] = old
    project = safe_path(workspace / ".claude/skills/dokumenti")
    project_exists = project.exists() and project != target
    if project_exists:
        if not migrate:
            raise ValueError("Obstaja projektni /dokumenti. Preglej in potrdi migracijo.")
        prior = json.loads(blob(SOURCE / "setup/predhodne-izdaje.json"))
        current = {}
        for file in project.rglob("*"):
            safe_path(file)
            if file.is_file() and "__pycache__" not in file.parts:
                current[file.relative_to(project).as_posix()] = digest(blob(file))
        if not any(current == {k.removeprefix("dokumenti/"): v for k, v in version.items()
                               if k.startswith("dokumenti/")} for version in prior.values()):
            raise ValueError("Projektni skill je prilagojen ali neznan. Nič ni spremenjeno; najprej prenesi njegove omejitve z izvajalcem.")
    safe_path(backup)
    for name, old in replacements.items():
        saved = backup / "osebni" / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(old)
    for name, data in payload.items():
        path = target / name
        if not path.exists() or blob(path) != data:
            write(path, data.decode("utf-8"))
    write(marker, {n: digest(data) for n, data in payload.items()})
    if project_exists:
        backup.mkdir(parents=True, exist_ok=True)
        shutil.move(str(project), str(backup / "projektni-dokumenti"))
    for name, data in payload.items():
        if blob(target / name) != data:
            raise ValueError("Končno preverjanje osebnega skilla ni uspelo.")
    return {"installed": str(target), "migrated_project": project_exists,
            "backup": str(backup) if project_exists or replacements else None,
            "next": "Preveri odvisnosti, združi potrjena globalna navodila in opravi preizkus v novem pogovoru."}


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--home", default=str(Path.home()))
    p.add_argument("--workspace", required=True)
    p.add_argument("--approve-personal", action="store_true")
    p.add_argument("--migrate-known-project", action="store_true")
    a = p.parse_args()
    try:
        print(json.dumps(install(a.home, a.workspace, a.approve_personal, a.migrate_known_project), ensure_ascii=False, indent=2))
    except Exception as exc:
        p.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
