from SDETAssignment.SDETAssignment import API_Requests as req
import pytest

def verify_post_to_hash_accepts_password():
    # read input
    file_name = 'valid_pswd_string_only.JSON'
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 200 | res.status_code == 201, "Request was not successful"


def verify_post_to_hash_returns_job_identifier_immediately() -> object:
    file_name = 'valid_pswd_string_only.JSON'
    res = req.get_post_response(file_name)
    var = res.elapsed.seconds
    assert int(var) < 1, "The job identifier is not returned in a second"


def test_password_hash_is_computed_after_5_seconds():
    file_name = 'valid_pswd_string_only.JSON'
    res = req.get_post_response(file_name)
    var = res.elapsed.seconds
    print(int(var))
    assert int(var) == 5, "the password hash is not computed at five seconds"
