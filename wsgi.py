from application import create_app
import logging
logging.basicConfig(filename='api.log',level=logging.DEBUG)


app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)