from click.testing import CliRunner
from dothub.cli import dothub


base_args = ["--user=xxx", "--token=yyy"]


def test_dothub_help():
    runner = CliRunner()
    result = runner.invoke(dothub, ['--help'], obj={})
    assert result.exit_code == 0


def test_dothub_pull_help():
    runner = CliRunner()
    result = runner.invoke(dothub, base_args + ['pull', "--help"], obj={})
    assert result.exit_code == 0


def test_dothub_push_help():
    runner = CliRunner()
    result = runner.invoke(dothub, base_args + ['push', "--help"], obj={})
    assert result.exit_code == 0

