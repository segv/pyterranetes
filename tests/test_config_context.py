import configparser
import json
import yaml

from pathlib import Path

from p10s import cfg


def test_ini(tmp_dir):
    c = cfg.INIContext(tmp_dir / 'test')

    c += {
        'section': {
            'a': 1,
            'b': "2",
        }
    }

    c.render()

    output = Path(tmp_dir / 'test.ini')
    assert output.exists()

    cp = configparser.ConfigParser()
    cp.read(str(output))

    assert cp.sections() == ['section']
    assert sorted(list(cp['section'].keys())) == ["a", "b"]
    assert cp['section']["a"] == "1"
    assert cp['section']["b"] == "2"
    assert cp['section'].getint("a") == 1


DATUM = {
    'section': {
        'a': 1,
        'b': ['c', 2, "2"],
        'd': {
            'e': None,
            'f': True,
        }
    }
}


def test_json(tmp_dir):
    c = cfg.JSONContext(tmp_dir / 'test') + DATUM
    c.render()

    output = Path(tmp_dir / 'test.json')
    assert output.exists()
    out = output.open("r")

    assert json.load(out) == DATUM


def test_yaml(tmp_dir):
    c = cfg.YAMLContext(tmp_dir / 'test') + DATUM
    c.render()

    output = Path(tmp_dir / 'test.yaml')
    assert output.exists()
    out = output.open("r")

    assert yaml.safe_load(out) == DATUM
