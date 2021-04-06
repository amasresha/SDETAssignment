import json
import multiprocessing
from multiprocessing import Process
import time
from SDETAssignment.SDETAssignment import API_Requests as req, Helpers as hp
import math


from requests_futures.sessions import FuturesSession


def test_post_to_hash_accepts_valid_password():
    file_name = 'valid_pswd_string_only.JSON'
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 200 | res.status_code == 201, "Request was not successful"


def test_post_to_hash_does_not_accept_empty_password():
    file_name = 'empty_string.JSON'
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 400, "System did not return a 400 code for empty string password"


def test_post_to_hash_accepts_special_characters_as_password():
    file_name = 'special_characters.JSON'
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 200, "System did not accept special characters as a password string"


def test_post_to_hash_accepts_long_string_as_password():
    file_name = 'long_string.JSON'
    res = req.get_post_response(file_name)
    # assert the request is accepted
    assert res.status_code == 200, "System did not accept long string as a password"


def verify_post_to_hash_returns_job_identifier_immediately() -> object:
    file_name = 'valid_pswd_string_only.JSON'
    res = req.get_post_response(file_name)
    var = res.elapsed.seconds
    assert int(var) < 1, "The job identifier is not returned in a second"


def test_password_hash_is_computed_after_5_seconds():
    file_name = 'valid_pswd_string_only.JSON'
    res = req.get_post_response(file_name)
    var = res.elapsed.seconds
    assert int(var) == 5, "the password hash is not computed at five seconds"


def test_valid_sha512_hash_is_generated():
    cont = req.get_encoded_password("1")
    hashed_str = cont.content.decode('UTF-8')
    assert len(hashed_str) == 128, "The hashing algorithm is not SHA512."


def verify_get_to_hash_accepts_a_job_identifier():
    cont = req.get_encoded_password("1")
    assert cont.status_code == 200, "the hash not accepting a job identifier"


def verify_function_returns_base64_encoded_password_hash():
    cont = req.get_encoded_password("1")
    is_base_64 = hp.is_base64(cont.content)
    assert is_base_64 == True, "the password hash is not base64 encoded"


def verify_get_to_stats_accept_no_data():
    sub_url = "/stats/2"
    cont = req.get_stats(sub_url)
    assert cont.status_code == 400, "A GET to /stats accepts data."


def verify_get_to_stats_returns_json_type():
    cont = req.get_stats()
    conttype = cont.headers.get('content-type')
    is_json_type = "application/json" in conttype
    assert is_json_type, "The response is not type: 'application/json'"


def verify_get_to_stats_returns_correct_total_hash_requests():
    cont = req.get_stats()
    json_response = json.loads(cont.text)
    total_req = int(json_response["TotalRequests"])
    assert total_req >= 1, "Stat of TotalRequests is <1 "


def verify_get_to_stats_returns_correct_average_time():
    cont = req.get_stats()
    json_response = json.loads(cont.text)
    avg_time = math.floor(int(json_response["AverageTime"]) / 1000)
    assert avg_time == 5, "The average time is not 5 seconds"


def verify_shutdown():
    shut_dwn = req.shutdown()
    cont_len = len(shut_dwn.content.decode('UTF-8'))
    is_shutdown = shut_dwn.status_code == 200 and cont_len == 0
    assert is_shutdown, "Shutdown is not returning status code 200 or is returning a " \
                        "response "


def verify_it_allows_in_flight_password_hashing_while_gracefully_shutdown():
    file_name = 'valid_pswd_string_only.JSON'
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


def verify_it_rejects_new_requests_while_shutting_down():
    file_name = 'valid_pswd_string_only.JSON'
    shut_down_status_code = req.shutdown().status_code
    res = req.get_post_response(file_name)
    assert (shut_down_status_code == 200 and res.status_code == 404), "Graceful shutdown is not respected"


def verify_it_supports_multiple_connections_simultaneously():
    file_name = 'valid_pswd_string_only.JSON'
    with FuturesSession() as session:
        futures = [session.req.get_post_response(file_name) for _ in range(5)]
        for future in futures:
            val = future.result()
            print(val)
