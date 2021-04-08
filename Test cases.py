import datetime
import json
import math
import time
from multiprocessing import Process

import pytest
from requests_futures.sessions import FuturesSession
import API_Requests as req
import Helpers as hp

file_name = 'valid_pswd_string_only.JSON'


@pytest.mark.run('first')
def test_post_to_hash_accepts_valid_password():
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 200 or res.status_code == 201, "Request was not successful"


@pytest.mark.run('first')
def test_post_to_hash_does_not_accept_empty_password():
    file_name = 'empty_string.JSON'
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 400, "System did not return a 400 code for empty string password"


@pytest.mark.run('first')
def test_post_to_hash_does_not_accept_some_special_characters_as_password():
    file_name = 'special_characters.JSON'
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 400, "Accepts most of the special characters"


@pytest.mark.run('first')
def test_post_to_hash_does_not_accept_very_long_string_as_password():
    file_name = 'long_string.JSON'
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 400, "System accepts more than 1100 characters string as a password"


@pytest.mark.run('first')
def test_post_to_hash_does_not_accept_invalid_json_file():
    file_name = 'invalid_json_file.JSON'
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 400, "System did not return a 400 code for empty string password"


@pytest.mark.run('first')
def test_post_to_hash_returns_job_identifier_immediately():
    res = req.get_post_response(file_name)
    var = res.elapsed.seconds
    assert int(var) < 1, "The job identifier is not returned in a second"


@pytest.mark.run('first')
def test_password_hash_is_computed_after_5_seconds():
    res = req.get_post_response(file_name)
    var = res.elapsed.seconds
    assert int(var) == 5, "the password hash is not computed at five seconds"


@pytest.mark.run('first')
def test_valid_sha512_hash_is_generated():
    res = req.get_post_response(file_name)
    work_id = int(res.content.decode('UTF-8'))
    work_id_str = str(work_id)
    cont = req.get_encoded_password(work_id_str)
    hashed_str = cont.content.decode('UTF-8')
    assert len(hashed_str) == 128, "The hashing algorithm is not SHA512."


@pytest.mark.run('first')
def test_get_to_hash_accepts_a_job_identifier():
    res = req.get_post_response(file_name)
    work_id = res.content.decode('UTF-8')
    cont = req.get_encoded_password(work_id)
    assert cont.status_code == 200, "the hash not accepting a job identifier"


@pytest.mark.run('first')
def test_function_returns_base64_encoded_password_hash():
    res = req.get_post_response(file_name)
    work_id = res.content.decode('UTF-8')
    cont = req.get_encoded_password(work_id)
    is_base_64 = hp.is_base64(cont.content)
    assert is_base_64 is True, "the password hash is not base64 encoded"


@pytest.mark.run('first')
def test_get_to_stats_accept_no_data():
    req.get_post_response(file_name)
    sub_url = "/stats/2"
    cont = req.get_stats(sub_url)
    assert cont.status_code == 404, "A GET to /stats accepts data."


@pytest.mark.run('first')
def test_get_to_stats_returns_json_type():
    req.get_post_response(file_name)
    cont = req.get_stats()
    conttype = cont.headers.get('content-type')
    is_json_type = "application/json" in conttype
    assert is_json_type, "The response is not type: 'application/json'"


@pytest.mark.run('first')
def test_get_to_stats_returns_correct_total_hash_requests():
    req.get_post_response(file_name)
    cont = req.get_stats()
    json_response = json.loads(cont.text)
    total_req = int(json_response["TotalRequests"])
    assert total_req >= 1, "Stat of TotalRequests is < 1"


@pytest.mark.run('first')
def test_get_to_stats_returns_correct_average_time():
    req.get_post_response(file_name)
    cont = req.get_stats()
    json_response = json.loads(cont.text)
    avg_time = math.floor(int(json_response["AverageTime"]) / 1000)
    assert avg_time >= 5, "The average time is less than 5 seconds. "


@pytest.mark.run('second')
def test_shutdown():
    shut_dwn = req.shutdown()
    cont_len = len(shut_dwn.content.decode('UTF-8'))
    is_shutdown = shut_dwn.status_code == 200 and cont_len == 0
    assert is_shutdown, "Shutdown is not returning status code 200 or is returning a " \
                        "response "


@pytest.mark.run('second')
def test_it_allows_in_flight_password_hashing_while_gracefully_shutdown():
    post_pr = Process(target=req.get_post_response(file_name))
    post_pr.start()
    shutdwn_pr = Process(target=req.shutdown())
    time.sleep(1)
    shutdwn_pr.start()
    post_pr.join()
    shutdwn_pr.join()
    post_status_code = req.stat.post_status
    shut_down_status_code = req.stat.shutdown_status
    assert (post_status_code == 200 and shut_down_status_code == 200), "Graceful shutdown is not respected"


@pytest.mark.run('third')
def test_it_rejects_new_requests_while_shutting_down():
    shutdwn_pr = Process(target=req.shutdown())
    post_pr = Process(target=req.get_post_response(file_name))
    shutdwn_pr.start()
    time.sleep(1)
    post_pr.start()
    shutdwn_pr.join()
    post_pr.join()
    post_status_code = req.stat.post_status
    shut_down_status_code = req.stat.shutdown_status
    assert (shut_down_status_code == 200 and post_status_code == 503), "New request is allowed while shutting down"


@pytest.mark.run('second')
def test_app_supports_multiple_concurrent_post_requests():
    url = req.base_url() + "/hash"
    with FuturesSession() as session:
        futures = [session.post(url, data='{"password":"angrymonkey"}') for _ in range(100)]
        for future in futures:
            val = future.result().status_code
            # print(datetime.datetime.now())
            assert val == 200, "one or more post calls are failing while running concurrently"


@pytest.mark.run('first')
def test_it_supports_multiple_get_requests_simultaneously():
    res = req.get_post_response(file_name)
    work_id = res.content.decode('UTF-8')
    get_url = req.base_url() + "/hash/" + work_id
    with FuturesSession() as session:
        futures = [session.get(get_url) for _ in range(100)]
        for future in futures:
            val = future.result().status_code
            print(datetime.datetime.now())
            assert val == 200, "one or more get calls are failing while running concurrently"


@pytest.mark.run('first')
def test_delete_is_not_supported_and_proper_code_is_returned():
    res = req.get_post_response(file_name)
    work_id = res.content.decode('UTF-8')
    resp = req.delete(work_id)
    assert resp.status_code == 405, "delete is supported or proper error is not displayed"


@pytest.mark.run('first')
def test_proper_response_for_get_request_with_invalid_work_id():
    res = req.get_post_response(file_name)
    work_id = int(res.content.decode('UTF-8')) + 2
    work_id_str = str(work_id)
    resp = req.get_encoded_password(work_id_str)
    # print(resp.status_code)
    assert resp.status_code == 400, "proper error message is not displayed when invalid ID is passed to a get request"
