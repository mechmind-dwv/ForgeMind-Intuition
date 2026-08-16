"""Export ForgeMind Bayesian snapshots into an Obsidian-compatible vault.

The exporter writes plain Markdown and JSON only. It never copies credentials,
files outside the supplied snapshot, or hidden application state.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def _slug(value: str, *, fallback: str) -> str:
    cleaned = _SAFE_NAME.sub("-", value.strip()).strip(".-_")
    return cleaned[:96] or fallback


def _frontmatter(values: Mapping[str, Any]) -> str:
    lines = ["---"]
    for key, value in values.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            rendered = json.dumps(value, ensure_ascii=False)
        else:
            rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
        lines.append(f"{key}: {rendered}")
    lines.append("---")
    return "\n".join(lines)


def _hypothesis_note(hypothesis: Mapping[str, Any]) -> str:
    hypothesis_id = str(hypothesis.get("hypothesis_id", "unknown"))
    state = str(hypothesis.get("state", "unknown"))
    posterior = hypothesis.get("posterior", 0.0)
    prior = hypothesis.get("prior", 0.0)
    evidence_ids = [str(item) for item in hypothesis.get("evidence_ids", [])]
    reasons = [str(item) for item in hypothesis.get("reasons", [])]
    metadata = hypothesis.get("metadata", {})
    lines = [
        _frontmatter(
            {
                "type": "forgemind-hypothesis",
                "hypothesis_id": hypothesis_id,
                "state": state,
                "prior": prior,
                "posterior": posterior,
                "evidence_count": len(evidence_ids),
            }
        ),
        "",
        f"# {hypothesis.get('description', hypothesis_id)}",
        "",
        f"**Estado:** `{state}`  ",
        f"**Posterior:** `{posterior}`  ",
        f"**Prior:** `{prior}`",
        "",
        "## Evidencia relacionada",
        "",
    ]
    lines.extend(f"- [[../evidence/{_slug(item, fallback='evidence')}|{item}]]" for item in evidence_ids)
    if not evidence_ids:
        lines.append("- Sin evidencia registrada.")
    lines.extend(["", "## Razones y trazabilidad", ""])
    lines.extend(f"- {reason}" for reason in reasons) or lines.append("- Sin razones registradas.")
    lines.extend(["", "## Metadatos", "", "```json", json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True), "```", ""])
    return "\n".join(lines)


def export_snapshot(
    snapshot: Mapping[str, Any],
    vault_path: str | Path,
    *,
    project_name: str = "ForgeMind",
    project_id: str = "project",
) -> Path:
    """Write a ForgeMind snapshot into ``vault_path`` and return its project directory."""

    beliefs = snapshot.get("beliefs")
    if not isinstance(beliefs, list) or not beliefs:
        raise ValueError("snapshot must contain a non-empty beliefs list")

    project_slug = _slug(project_id, fallback="project")
    project_dir = Path(vault_path).expanduser() / "ForgeMind" / "Projects" / project_slug
    hypotheses_dir = project_dir / "hypotheses"
    hypotheses_dir.mkdir(parents=True, exist_ok=True)

    exported = {
        "project_name": project_name,
        "project_id": project_id,
        "elimination_threshold": snapshot.get("elimination_threshold"),
        "min_evidence": snapshot.get("min_evidence"),
        "hypothesis_count": len(beliefs),
    }
    (project_dir / "snapshot.json").write_text(
        json.dumps({"metadata": exported, "snapshot": snapshot}, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    index_lines = [
        _frontmatter({"type": "forgemind-project", "project_id": project_id, "hypothesis_count": len(beliefs)}),
        "",
        f"# {project_name}",
        "",
        "Exportación de un snapshot de ForgeMind para consulta en Obsidian.",
        "",
        f"- Umbral de eliminación: `{snapshot.get('elimination_threshold')}`",
        f"- Evidencia mínima: `{snapshot.get('min_evidence')}`",
        f"- Hipótesis exportadas: `{len(beliefs)}`",
        "",
        "## Hipótesis",
        "",
    ]
    for belief in beliefs:
        hypothesis_id = str(belief.get("hypothesis_id", "unknown"))
        filename = _slug(hypothesis_id, fallback="hypothesis") + ".md"
        index_lines.append(f"- [[hypotheses/{filename[:-3]}|{hypothesis_id}]] — {belief.get('state', 'unknown')}")
        (hypotheses_dir / filename).write_text(_hypothesis_note(belief), encoding="utf-8")
    (project_dir / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return project_dir


__all__ = ["export_snapshot"]
