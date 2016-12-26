from dothub import utils


def test_extract_gh_info_for_ssh():
    owner, repo = utils.extract_gh_info_from_uri("git@github.com:Mariocj89/dothub.git")
    assert owner == "Mariocj89"
    assert repo == "dothub"


def test_extract_gh_info_for_http():
    owner, repo = utils.extract_gh_info_from_uri("https://github.com/Mariocj89/dothub.git")
    assert owner == "Mariocj89"
    assert repo == "dothub"
