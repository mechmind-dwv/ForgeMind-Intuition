import json

from forgemind.cli import main
from forgemind.core import Node
from forgemind.project import ForgeMindProject, example_project


def test_project_round_trip(tmp_path):
    path = tmp_path / "project.json"
    project = example_project()
    project.save(path)
    restored = ForgeMindProject.load(path)
    assert restored.name == project.name
    assert restored.candidates[0][0] == Node("U", "rev")
    assert restored.probes == project.probes


def test_cli_init_and_advise(tmp_path, capsys):
    path = tmp_path / "project.json"
    assert main(["init", str(path)]) == 0
    assert json.loads(path.read_text())["name"] == "intuition-playground"
    capsys.readouterr()
    assert main(["advise", str(path)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["command"] == "advise"
    assert len(output["results"]) == 3
