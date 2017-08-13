from dothub import organization
import sealedmock


def test_get_org_repos():
    gh_helper = sealedmock.SealedMock()
    gh_helper.get.return_value = [
        {
            "name": "repo1",
            "fork": True
        },
        {
            "name": "repo2",
            "fork": False
        },
    ]
    org = organization.Organization(gh_helper, "orgname")

    assert ["repo2"] == list(org.repos)
