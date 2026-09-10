"""Download the workshop package into an explicitly selected folder; never overwrite."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import stat
import urllib.request
import zipfile

VERSION = "2026-09-10-v3"
BASE = "https://claude-delavnica-starter.luka36512.chatgpt.site"
ARCHIVE_URL = f"{BASE}/claude-work-starter-{VERSION}.zip"
MANIFEST_URL = f"{BASE}/claude-work-starter-{VERSION}.json"
FILES = (
    "README.md", "NASTAVI-CLAUDE.md", "ZA-IZVAJALCA.md", "PREVERJANJE.md",
    "ZACNI-TUKAJ.txt", "dokumenti/SKILL.md", "dokumenti/scripts/dokumenti.py",
    "preverjanje/test_dokumenti.py", "setup/pripravi.py", "preverjanje/test_pripravi.py",
)
LIMIT = 5 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def download(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Claude-Work-Starter/" + VERSION})
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.geturl() != url:
            raise ValueError("Nepričakovana preusmeritev prenosa.")
        data = response.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError("Prenos presega dovoljeno velikost.")
    return data


def unpack(root, archive, manifest):
    """Validate every member and destination before creating any package files."""
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Izbrana delovna mapa ne obstaja.")
    if manifest.get("version") != VERSION or manifest.get("archive_url") != ARCHIVE_URL:
        raise ValueError("Napačna izdaja paketa.")
    if set(manifest.get("files", {})) != set(FILES):
        raise ValueError("Nepopoln ali nepričakovan seznam datotek.")
    if len(archive) > LIMIT or digest(archive) != manifest.get("sha256"):
        raise ValueError("Kontrolni odtis ZIP-a se ne ujema.")
    payload = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        members = z.infolist()
        if len(members) != len(FILES) or {m.filename for m in members} != set(FILES):
            raise ValueError("ZIP vsebuje nepričakovane, podvojene ali manjkajoče poti.")
        if sum(m.file_size for m in members) > LIMIT:
            raise ValueError("Razširjeni paket je prevelik.")
        for m in members:
            mode = m.external_attr >> 16
            if m.is_dir() or stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG)):
                raise ValueError("ZIP vsebuje nedovoljeno vrsto datoteke.")
            data = z.read(m)  # zipfile also checks CRC.
            if digest(data) != manifest["files"][m.filename]:
                raise ValueError("Kontrolni odtis datoteke se ne ujema: " + m.filename)
            payload[m.filename] = data

    def check_path(name):
        current = root
        for i, part in enumerate(Path(name).parts):
            if current.exists():
                # Refuse case-only collisions, also when testing on case-sensitive disks.
                if any(p.name.casefold() == part.casefold() and p.name != part for p in current.iterdir()):
                    raise ValueError("Konflikt zapisa imena: " + name)
            current = current / part
            if current.is_symlink():
                raise ValueError("Simbolna povezava v ciljni poti: " + name)
            if current.exists():
                last = i == len(Path(name).parts) - 1
                if (last and not current.is_file()) or (not last and not current.is_dir()):
                    raise ValueError("Konflikt datoteke in mape: " + name)
        return current

    pending = []
    for name, data in payload.items():
        target = check_path(name)
        if target.exists():
            if target.read_bytes() != data:
                raise ValueError("Obstoječa datoteka se razlikuje; nič ni prepisano: " + name)
        else:
            pending.append(name)
    for name in pending:
        target = check_path(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        check_path(name)
        # Exclusive creation also preserves a file created since the preflight check.
        with target.open("xb") as output:
            output.write(payload[name])
    for name, data in payload.items():
        if check_path(name).read_bytes() != data:
            raise ValueError("Končno preverjanje ni uspelo: " + name)
    return {"root": str(root), "version": VERSION, "files": len(payload),
            "created": len(pending), "unchanged": len(payload) - len(pending),
            "next": str(root / "NASTAVI-CLAUDE.md")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Potrjena absolutna delovna mapa")
    args = parser.parse_args()
    if not Path(args.root).is_absolute():
        parser.error("--root mora biti absolutna pot")
    try:
        manifest = json.loads(download(MANIFEST_URL))
        result = unpack(args.root, download(ARCHIVE_URL), manifest)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f"Priprava ni zaključena: {error}\nNe prepisuj datotek; blokado predaj izvajalcu.\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("Preberi lokalni NASTAVI-CLAUDE.md in nadaljuj pri 1. koraku. Ne zaganjaj prenosa znova.")


if __name__ == "__main__":
    main()
