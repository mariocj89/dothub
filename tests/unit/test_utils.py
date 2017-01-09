from dothub import utils
import sealedmock


def test_extract_gh_info_for_ssh():
    owner, repo = utils.extract_gh_info_from_uri("git@github.com:Mariocj89/dothub.git")
    assert owner == "Mariocj89"
    assert repo == "dothub"


def test_extract_gh_info_for_http():
    owner, repo = utils.extract_gh_info_from_uri("https://github.com/Mariocj89/dothub.git")
    assert owner == "Mariocj89"
    assert repo == "dothub"


@sealedmock.patch("dothub.utils.click.confirm")
def test_confirm_changes_no_change(mock_confirm):
    mock_confirm.return_value = None
    mock_confirm.sealed = True

    utils.confirm_changes({}, {})
    assert 0 == mock_confirm.call_count


@sealedmock.patch("dothub.utils.click.confirm")
def test_confirm_changes_with_changes(mock_confirm):
    mock_confirm.return_value = None
    mock_confirm.sealed = True

    utils.confirm_changes(dict(options="B"), dict(options="A"))
    assert 1 == mock_confirm.call_count


@sealedmock.patch("dothub.utils.click.confirm")
def test_confirm_changes_missing_keys_are_ignored(mock_confirm):
    mock_confirm.return_value = None
    mock_confirm.sealed = True

    utils.confirm_changes(dict(options="B", hooks="C"), dict(options="B"))
    assert 0 == mock_confirm.call_count
