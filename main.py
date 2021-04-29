# aaron berghash
# greg mockler
# tanner bradford
# ranen mirot

"""

main.py is the main class for the application

"""

from website import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
