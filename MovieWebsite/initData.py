import media
import fresh_tomatoes as tomato

# Create movies and push to array
gone_girl = media.Movie("Gone Girl", "2014")
gone_girl.set_plot("With his wife's disappearance having become the focus "
                   "of an intense media circus, a man sees the spotlight "
                   "turned on him when it's suspected that he may not "
                   "be innocent.")
gone_girl.set_poster("poster/GoneGirl.jpg")
gone_girl.set_trailer("https://www.youtube.com/watch?v=0VGD_jLyE9Y")

kingsman = media.Movie("Kingsman", "2014")
kingsman.set_plot("A spy organization recruits an unrefined, "
                  "but promising street kid into the agency's "
                  "ultra-competitive training program, "
                  "just as a global threat emerges from a "
                  "twisted tech genius.")
kingsman.set_poster("poster/Kingsman.jpg")
kingsman.set_trailer("https://www.youtube.com/watch?v=hN0JkFrvO_M")

up_air = media.Movie("Up in the Air", "2009")
up_air.set_plot("Ryan Bingham enjoys living out of a suitcase for "
                "his job traveling around the country firing people, "
                "but finds that lifestyle threatened by the presence of "
                "a potential love interest and a new hire.")
up_air.set_poster("poster/UpInTheAir.jpg")
up_air.set_trailer("https://www.youtube.com/watch?v=rTL1FmvVCuA")

arrival = media.Movie("Arrival", "2016")
arrival.set_plot("When twelve mysterious spacecraft appear around "
                 "the world, linguistics professor Louise Banks is "
                 "tasked with interpreting the language of the "
                 "apparent alien visitors.")
arrival.set_poster("poster/Arrival.jpg")
arrival.set_trailer("https://www.youtube.com/watch?v=tFMo3UJ4B4g")

murder_orient_express = media.Movie("Murder on the Orient Express", "1974")
murder_orient_express.set_plot("In December 1935, when his train is stopped "
                               "by deep snow, detective Hercule Poirot is "
                               "called on to solve a murder that occurred "
                               "in his car the night before.")
murder_orient_express.set_poster("poster/MurderOnTheOrientExpress.jpg")
murder_orient_express.set_trailer("https://www.youtube.com/watch?v=u0ykCP1AYlk")

gone_wind = media.Movie("Gone with the Wind", "1939")
gone_wind.set_plot("A manipulative woman and a roguish man conduct a "
                   "turbulent romance during the American Civil War "
                   "and Reconstruction periods.")
gone_wind.set_poster("poster/GoneWithTheWind.jpg")
gone_wind.set_trailer("https://www.youtube.com/watch?v=cTjeIJ7P-kg")

movies = [gone_girl, kingsman, up_air, arrival, murder_orient_express, gone_wind]

# Open movies in browser
tomato.open_movies_page(movies)
