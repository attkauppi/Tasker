

def test_index(testapp):
    """ Tests if index page can be reached """
    response = testapp.get("/")

    print("TEST INDEX")
    print("TESTED TEST_INDEX")
    print("Response.data: ", response.data)
    assert b"ciao" in response.data
    assert b"viesti" in response.data
    


