import platform

where = platform.uname().release.find("aws")

if where == -1:
    # Local.
    config = {
        "host": "127.0.0.1",
        "database": "swimdataDB",
        "user": "swimuser",
        "password": "swimpasswd",
    }
else:
    # Not on PythonAnywhere.
    config = {
        "host": "C00261172.mysql.pythonanywhere-services.com",
        "database": "C00261172$swimdataDB",
        "user": "C00261172",
        "password": "itcarlow",
    }
