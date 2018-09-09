class Movie():
    def __init__(self, title, year):
        """Constructor function initializes object with title and year
        Args:
            title (str): title of the movie
            year (str): year of release
        """
        self.title = title
        self.year = year
        # id is a field that is required for rendering of the website later
        self.id = "-".join(title.split())
    def set_plot(self, plot):
        """Sets plot of movie
        Args:
            plot (str): short plot description
        """
        self.plot = plot
    def set_poster(self, poster):
        """Sets poster image of movie
        Args:
            poster (str): poster image uri
        """
        self.poster = poster
    def set_trailer(self, trailer):
        """Sets trailer of movie
        Args:
            trailer (str): trailer url of movie
        """
        self.trailer = trailer
