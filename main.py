# aaron berghash
# greg mockler
# tanner bradford
# ranen mirot

"""

main.py is the main class for the application



-------TODO phase 4-------

•The application user profile that displays:
    [X] The number of collections the user has
    [X] The number of follower
    [X] The number of following
    [X] users top 10 artists

•A song recommendation system with the following options:
    [ ] The top 50 most popular songs of the month
    [ ] The top 50 most popular songs among my friend
    [X] The top 5 most popular genres of the month
    [...] For you: Recommend songs based on your play history
        (e.g. genre,artist) and the play history of similar users

•NON app things TODO
    [ ] POSTER
    [ ] poster showing
    [ ] VIDEO
    [ ] update report
    [ ] peer reveiw
    [ ] data analysis



"""

from website import create_app

# from connection import add_songs
app = create_app()

# add_songs()
if __name__ == "__main__":
    app.run(debug=True)
