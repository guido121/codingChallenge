import requests

ENDPOINT_1 = "http://127.0.0.1:5000/api/employees_hired_quarter/2021"
ENDPOINT_2 = "http://127.0.0.1:5000/api/employees_by_department/2021"


def test_can_call_endpoint1():
  response = requests.get(ENDPOINT_1)
  assert response.status_code == 200

def test_can_call_endpoint2():
  response = requests.get(ENDPOINT_2)
  assert response.status_code == 200

def test_num_rows_endpoint1():
    response = requests.get(ENDPOINT_1)
    data = response.json()
    assert len(data) == 597
  
def test_num_rows_endpoint2():
    response = requests.get(ENDPOINT_2)
    data = response.json()
    assert len(data) == 8

def test_validate_names_endpoint1():
    response = requests.get(ENDPOINT_1)
    data = response.json()
    assert list(data[0].keys()) == ['department','job','Q1','Q2','Q3','Q4']


def test_validate_column_names_endpoint2():
    response = requests.get(ENDPOINT_2)
    data = response.json()
    assert list(data[0].keys()) == ['id','department','hired']
