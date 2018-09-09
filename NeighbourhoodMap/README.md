# Neighbourhood Map
The Neighbourhood Map app displays a list of parks which you can visit if you're living somewhere between the cities Mannheim, Heidelberg and Karlsruhe. You can select a park to view weather information and nearby restaurants if you plan a visit.

## Run the App
To run the application, please install [nodejs](https://nodejs.org) first. After cloning the repository, run `npm install` from the command line in the directory of the repository to install all dependencies. Once this is done, change directory either to the `src` or `dist` directory. Run `node app.js` to start the server. Open your browser and view the app under `http://localhost:8080`.

## Remarks
The list of parks is provided as a `locations.json` file. The file is requested during initialization of the app. To retrieve the geocoordinates of the locations for display on the map, the [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding/start) is used. When a location is selected, the [OpenWeatherMap API](https://openweathermap.org/api) is called for weather information. To retrieve a list of nearby restaurants, the new [Yelp Fusion Search API](https://www.yelp.com/developers/documentation/v3) is called. Since the Yelp API does not support CORS, the request is done server-side in the file `app.js`.

## Build the App
To build the app, [grunt-cli](https://gruntjs.com/getting-started) should be installed globally. Run `npm run babel` to transpile the javascript files in `src/js/`. This is necessary because the source files use template literals, which is not supported by all browsers. The resulting files are written to `dist/js/`. After that, run `grunt` to do the following:
* minify the javascript files in `src/js/`.
* concatenate the javascript file `src/js/main.js` with the babel polyfill file. The polyfill file is located in the installed `node_modules` folder. Including the polyfill is necessary to support promises in browsers such as IE.
* minify the css files.
* minify the HTML files.

## Resources
* [Map Icons Collection](https://mapicons.mapsmarker.com/) for map markers
* [Font Awesome](http://fontawesome.io/) for icon fonts
* [jQuery](https://jquery.com/) for AJAX requests
* [Knockout](http://knockoutjs.com/)
* [Google Maps](https://developers.google.com/maps/)
* [Babel](https://babeljs.io/) to support new JS language features in older browsers