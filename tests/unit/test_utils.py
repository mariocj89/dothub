from dothub import utils
import sealedmock

class StringContains(object):
    """Ensures the string contains a list of subsrtings"""
    def __init__(self, *substr):
        self._substr = substr

    def __eq__(self, other):
        return all(x in other for x in self._substr)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__,
                               ",".join(["'{}'".format(x) for x in self._substr]))

def test_extract_gh_info_for_ssh():
    owner, repo = utils.extract_gh_info_from_uri("git@github.com:mariocj89/dothub.git")
    assert owner == "mariocj89"
    assert repo == "dothub"


def test_extract_gh_info_for_http():
    owner, repo = utils.extract_gh_info_from_uri("https://github.com/mariocj89/dothub.git")
    assert owner == "mariocj89"
    assert repo == "dothub"


def test_split_org_only():
    owner, repo = utils.split_org_repo("etcaterva")
    assert owner == "etcaterva"
    assert repo is None


def test_split_org_only_with_slash():
    owner, repo = utils.split_org_repo("etcaterva/")
    assert owner == "etcaterva"
    assert repo is None


def test_split_org_and_repo():
    owner, repo = utils.split_org_repo("etcaterva/echaloasuerte")
    assert owner == "etcaterva"
    assert repo == "echaloasuerte"


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


@sealedmock.patch("dothub.utils.click.confirm")
def test_confirm_changes_str_unicode_changes_are_ignored(mock_confirm):
    mock_confirm.return_value = None
    mock_confirm.sealed = True

    utils.confirm_changes(dict(options=u"B"), dict(options="B"))
    assert 0 == mock_confirm.call_count


@sealedmock.patch("dothub.utils.LOG.info")
@sealedmock.patch("dothub.utils.click.confirm")
def test_output_for_diff_on_web_hooks(mock_confirm, log_info):
    mock_confirm.return_value = None
    log_info.return_value = None
    mock_confirm.sealed = True
    log_info.sealed = True

    current_hooks = [{
        "name":"web",
        "config":{ "url":"http://chooserandom.com"},
        "active": True
    }]
    new_hooks = [{
        "name":"web",
        "config":{ "url":"http://chooserandom.com"},
        "active": False
    }]

    utils.confirm_changes(dict(hooks=current_hooks), dict(hooks=new_hooks))

    assert 1 == mock_confirm.call_count
    log_info.assert_any_call(StringContains("C ", "http://chooserandom.com", "True", "False"))
