import webbrowser
import os
import re

# Document header including CSS
main_page_head = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Movie Collection</title>

    <!-- Bootstrap 3 -->
    <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.1.0/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.1.0/css/bootstrap-theme.min.css">
    <script src="https://code.jquery.com/jquery-1.10.1.min.js"></script>
    <script src="https://netdna.bootstrapcdn.com/bootstrap/3.1.0/js/bootstrap.min.js"></script>
    <style type="text/css" media="screen">
        body {
            background-color: #31363f;
            margin-top: 70px;
            margin-bottom: 70px;
        }
        #trailer .modal-dialog {
            margin-top: 200px;
            width: 640px;
            height: 480px;
        }
        header{
            z-index: 1;
            box-sizing: border-box;
            background: linear-gradient(to bottom, #FFF 0%,#F4F4F4 100%);
            border-bottom: 10px solid #212122;
            color: #212122;
            position: fixed;
            top: 0px;
            left: 0px;
            height: 60px;
            width: 100%;
            padding: 0.5rem;
        }        
        .my-footer{
            position: fixed;
            bottom:0px;
            background: linear-gradient(to bottom, #FFF 0%,#F4F4F4 100%);
            border-top: 10px solid #212122;
            color: #212122;
            width: 100%;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
        }
        .main-content{
            width: 100%;
            overflow-y: auto;
        }
        .hanging-close {
            position: absolute;
            top: -12px;
            right: -12px;
            z-index: 9001;
        }
        #trailer-video {
            width: 100%;
            height: 100%;
        }
        .movie-tile {
            margin-bottom: 20px;
            padding-top: 20px;
        }
        .movie-tile:hover {
            background-color: #4c5360;
            cursor: pointer;
        }
        .movie-details{
            background-color: rgba(0,0,0,0.75);
            color: #ffffff;
            position: absolute;
            left: 0px;
            bottom: 0px;
            width:100%;
            text-align: center;
            padding:1.5rem;
        }
        .hide{
            display: none;
        }
        .scale-media {
            padding-bottom: 56.25%;
            position: relative;
        }
        .scale-media iframe {
            border: none;
            height: 100%;
            position: absolute;
            width: 100%;
            left: 0;
            top: 0;
            background-color: white;
        }
    </style>

</head>
'''

# Footer and JavaScript
main_page_footer= '''
    <div class="my-footer">
        <span>Movie descriptions and posters were taken from <a href="https://www.imdb.com">IMDb</a></span>
    </div>
    <script type="text/javascript" charset="utf-8">
        // display movie info on hover
        $(".movie-tile").on("mouseenter",function(e){
            var $popover = $("#"+$(e.currentTarget).attr("id")+"-info");
            $popover.removeClass("hide");
        });
        // hide movie info when leaving tile
        $(".movie-tile").on("mouseleave",function(e){
            var $popover = $("#"+$(e.currentTarget).attr("id")+"-info");
            $popover.addClass("hide");
        }); 
        // Pause the video when the modal is closed
        $(document).on('click', '.hanging-close, .modal-backdrop, .modal', function (event) {
            // Remove the src so the player itself gets removed, as this is the only
            // reliable way to ensure the video stops playing in IE
            $("#trailer-video-container").empty();
            return false;
        });
        // Start playing the video whenever the trailer modal is opened
        $(document).on('click', function (event) {
            var trailerYouTubeId = $(event.target).attr('data-trailer-youtube-id')
            var sourceUrl = 'https://www.youtube.com/embed/' + trailerYouTubeId + '?autoplay=1&html5=1';
            $("#trailer-video-container").empty().append($("<iframe></iframe>", {
              'id': 'trailer-video',
              'type': 'text-html',
              'src': sourceUrl,
              'frameborder': 0
            }));
        });
        // Animate in the movies when the page loads
        $(document).ready(function () {
          $('.movie-tile').hide().first().show("fast", function showNext() {
            $(this).next("div").show("fast", showNext);
          });
        });
    </script>
  </body>
</html>
'''

# Header bar and main content
main_page_content = '''
  <body>
    <!-- Trailer Video Modal -->
    <div class="modal" id="trailer">
      <div class="modal-dialog">
        <div class="modal-content">
          <a href="#" class="hanging-close" data-dismiss="modal" aria-hidden="true">
            <img src="https://lh5.ggpht.com/v4-628SilF0HtHuHdu5EzxD7WRqOrrTIDi_MhEG6_qkNtUK5Wg7KPkofp_VJoF7RS2LhxwEFCO1ICHZlc-o_=s0#w=24&h=24"/>
          </a>
          <div class="scale-media" id="trailer-video-container">
          </div>
        </div>
      </div>
    </div>

    <!-- Main Page Content -->
    <header class="text-center" role="navigation">
        <h4>Movie Collection</h4>
    </header>
    </div>
    <div class="main-content">
        <div class="container">
            {movie_tiles}
        </div>
    </div>
'''

# A single movie entry html template
movie_tile_content = '''
    <div class="col-md-6 col-lg-4 movie-tile text-center" id="{movie_id}">
        <img src="{poster_image_url}" width="220" height="342">
        <div class="hide movie-details" id="{movie_id}-info">
            <h2>{movie_title}</h2>
            <h4>{movie_year}</h4>
            {movie_plot}<br>
            <a data-trailer-youtube-id="{trailer_youtube_id}" data-toggle="modal" data-target="#trailer">Watch Trailer</a>
        </div>
    </div>
'''


def create_movie_tiles_content(movies):
    # The HTML content for this section of the page
    content = ''
    for movie in movies:
        # Extract the youtube ID from the url
        youtube_id_match = re.search(
            r'(?<=v=)[^&#]+', movie.trailer)
        youtube_id_match = youtube_id_match or re.search(
            r'(?<=be/)[^&#]+', movie.trailer)
        trailer_youtube_id = (youtube_id_match.group(0) if youtube_id_match
                              else None)

        # Retrieve movie data for insertion in template
        content += movie_tile_content.format(
            movie_title = movie.title,
            movie_id = movie.id,
            movie_plot = movie.plot,
            movie_year = movie.year,
            poster_image_url = movie.poster,
            trailer_youtube_id = trailer_youtube_id
        )
    return content


def open_movies_page(movies):
    # Create or overwrite the output file
    output_file = open('index.html', 'w')

    # Replace the movie tiles placeholder generated content
    rendered_content = main_page_content.format(
        movie_tiles=create_movie_tiles_content(movies))

    # Output the file
    output_file.write(main_page_head + rendered_content + main_page_footer)
    output_file.close()

    # open the output file in the browser (in a new tab, if possible)
    url = os.path.abspath(output_file.name)
    webbrowser.open('file://' + url, new=2)
