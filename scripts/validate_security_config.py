from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[1]
for relative in (Path('.github/dependabot.yml'), Path('.github/workflows/security.yml')):
    path = root / relative
    with path.open(encoding='utf-8') as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"{path} did not parse as a mapping")
    print(f"validated {relative}")

security = yaml.safe_load((root / '.github/workflows/security.yml').read_text(encoding='utf-8'))
if 'jobs' not in security or not {'codeql', 'dependency-review', 'python-audit', 'secret-scan', 'scorecard'} <= set(security['jobs']):
    raise SystemExit('security workflow jobs are incomplete')

dependabot = yaml.safe_load((root / '.github/dependabot.yml').read_text(encoding='utf-8'))
if dependabot.get('version') != 2 or len(dependabot.get('updates', [])) != 3:
    raise SystemExit('dependabot configuration is incomplete')
print('security configuration checks passed')
