# aaron berghash
# greg mockler
# tanner bradford

"""
TODO:

* link data base to appliction

* fill data base with data sets

* link functions to get the data requested from data base
  and display data

 * PHASE 3 requirments by ap april 2:

  • Users will be able to create new accounts and access via login.
    The system must record the date and time an account is created.
    It must also stored the date and time an useraccess into the application

   •Users will be able to create collections of music.

   •Users will be to see the list of all their collections by:
        name in ascending order

    •The list must show the following information per collection:
        name
        Number of songs in the collection
        Total duration in minutes

    •Users will be able to search for songs by:
        name
        artist
        album
        genre

        The resulting list of songs must be in alphabetical order by song's name
        and artist's name

        (Users can also sort list by artist's name, genre, and released year)
        EACH song in list shows:
            name
            artist's name
            the album
            the length
            the listen count.


    •Users can add and delete albums, and songs from their collection

    • Users can modify the name of a collection.
    • They can also delete an entire collection

    •Users can listen to a song individually or it can play an entire collection.
     You must record every time a song is played by a user. You do not need to
     actually be able toplay songs, simply mark them as played

    •Users can follow a friend.
    •Users can search for new friends by email
    •The application must also allow an user to unfollow a friend

* make the application look good if we make it

"""

from website import create_app
#from connection import add_songs
app = create_app()
#add_songs()
if __name__ == "__main__":
    app.run(debug=True)
