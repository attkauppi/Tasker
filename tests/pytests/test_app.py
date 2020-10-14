

def test_index(testapp):
    """ Tests if index page can be reached """
    response = testapp.get("/")

    print("TEST INDEX")
    print("TESTED TEST_INDEX")
    print("Response.data: ", response.data)
    assert b"ciao" in response.data
    assert b"viesti" in response.data

def test_register(testapp):
    """ Tests registering """
    response = testapp.get("/auth/register")
    assert b"Tunnus" in response.data
    assert b"Salasana" in response.data
    assert b"register.html" in response.data
    assert 200 == response.status_code

# def test_send_registration(testapp):
#     response = testapp.post("/register", data={"username": "testityyppi", "password":"salasana"})
#     print("response.status_code: ", response.status_code)
#     assert 200 == response.status_code

#     print("Response.body")
    

    


