# aaron berghash
# greg mockler
# tanner bradford
# ranen mirot

"""
 TODO:

    [ ] rename collections

    [ ] delete songs from collections

    [ ] add albums to collections
            -> do this by adding a button to each song search result

    [ ] delete albums from collections

    [ ] play album from search
            -> do this by adding a button to each song search result


    [ ] display this in the playlist list view:
        total length: 8.8 minutes
        number of songs: 2

    [ ] remove 'Playlist' part of explore tab

  Quality of life stuff:

    [ ] display a message if the user is already following that user instead of just skipping

* make the application look good if we make it...

"""

from website import create_app
# from connection import add_songs
app = create_app()

# add_songs()
if __name__ == "__main__":
    app.run(debug=True)
