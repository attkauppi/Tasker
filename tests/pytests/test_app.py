

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
    response = testapp.get("/register")
    assert b"Username" in response.data
    assert b"Password" in response.data
    assert b"Repeat password" in response.data
    assert 200 == response.status_code

def test_send_registration(testapp):
    response = testapp.post("/register", data={"Username": "testityyppi", "Password":"salasana", "Repeat password":"salasana"})
    print("response.status_code: ", response.status_code)
    assert 200 == response.status_code

    print("Response.body")

def test_404(testapp):
    """ Tests 404 error """
    response = testapp.get("/olematon")
    assert b"Not found" in response.data
    assert 404 == response.status_code


    


