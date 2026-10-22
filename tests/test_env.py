import json

import pytest


def pair(tmp_path, template, actual):
    example, env = tmp_path / ".env.example", tmp_path / ".env"
    example.write_text(template, encoding="utf-8-sig")
    env.write_text(actual, encoding="utf-8")
    return example, env


def test_reports_keys_not_values(tmp_path, env_tool):
    example, env = pair(tmp_path, "KEY=\nDATABASE=\nEMPTY=\nPLACE=\n",
                        "KEY=SECRET_SENTINEL_123\nKEY=SECOND_SECRET\nEMPTY=\nPLACE=changeme\nEXTRA=hidden\n")
    before = env.read_bytes()
    report = env_tool.check(example, env)
    assert report["missing"] == ["DATABASE"]
    assert report["empty"] == ["EMPTY"]
    assert report["placeholders"] == ["PLACE"]
    assert report["extra"] == ["EXTRA"]
    assert report["duplicates"] == [{"key": "KEY", "line": 2}]
    for secret in ["SECRET_SENTINEL_123", "SECOND_SECRET", "hidden"]:
        assert secret not in json.dumps(report)
    assert env.read_bytes() == before


@pytest.mark.parametrize("value", ['"abc#def" # comment', "'abc#def'", "abc#def", "abc # comment",
                                   '"escaped\\\"quote"', "'C:\\path'", "$(echo NEVER_RUN)"])
def test_supported_values(tmp_path, env_tool, value):
    example, env = pair(tmp_path, "TOKEN=\n", f"export TOKEN = {value}\n")
    assert env_tool.check(example, env)["ok"]


@pytest.mark.parametrize("actual", ['TOKEN="unterminated\nSECRET PRIVATE LINE\n', "MALFORMED_SECRET\n", 'TOKEN="a"tail\n'])
def test_syntax_errors_do_not_echo_input(tmp_path, env_tool, actual):
    example, env = pair(tmp_path, "TOKEN=\n", actual)
    report = env_tool.check(example, env)
    assert report["syntax_errors"]
    assert not report["ok"]
    assert "SECRET" not in json.dumps(report)


def test_optional_empty_and_strict_extra(tmp_path, env_tool):
    example, env = pair(tmp_path, "OPTIONAL=\n", "OPTIONAL=\nEXTRA=abc\n")
    assert env_tool.check(example, env, allow_empty=["OPTIONAL"])["ok"]
    assert not env_tool.check(example, env, allow_empty=["OPTIONAL"], strict_extra=True)["ok"]
    assert env_tool.check(example, env, allow_empty=["TYPO"])["unknown_allow_empty"] == ["TYPO"]


def test_template_duplicates_are_errors(tmp_path, env_tool):
    example, env = pair(tmp_path, "KEY=\nKEY=\n", "KEY=value\n")
    assert not env_tool.check(example, env)["ok"]


def test_decode_error_does_not_echo_secret(tmp_path, env_tool, capsys):
    example, env = pair(tmp_path, "TOKEN=\n", "")
    env.write_bytes(b"TOKEN=SECRET\xff")
    assert env_tool.main(["--example", str(example), "--env", str(env)]) == 2
    output = capsys.readouterr()
    assert "SECRET" not in output.out + output.err


def test_interpolation_reported_without_evaluation(tmp_path, env_tool):
    example, env = pair(tmp_path, "TOKEN=\n", "TOKEN=${SECRET}\n")
    assert env_tool.check(example, env)["unexpanded"] == ["TOKEN"]
