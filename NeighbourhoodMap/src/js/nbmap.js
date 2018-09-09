var mapModule = (function () {
	var markers = new Map();
	var map;
	var bounds;
	var aLocations = sharedData.getLocations();
	var currInfoWindow;
	var vm;
    var icon = "images/tree.png"
	var init = function () {
		vm = ViewModel;
		map = new google.maps.Map(document.getElementById("map"), {
				center: {
					lat: 0,
					lng: 0
				},
				styles: [{
    				"stylers": [
      					{ "saturation": 10 },
      					{ "lightness": 0 }
    				]
    			}]
			});
		currInfoWindow =  new google.maps.InfoWindow();
		bounds = new google.maps.LatLngBounds();
		/* Adjust map to fit all locations in it */
		aLocations.forEach(function (loc) {
			var marker = new google.maps.Marker({
					map: map,
					position: loc.coord,
					title: loc.name,
					icon: icon
				});
			google.maps.event.addListener(marker, "click", onClickMarker);
			markers.set(loc.name, marker);
			bounds.extend(loc.coord);
		});
		map.fitBounds(bounds);
		map.setCenter(bounds.getCenter());
		/* window resize
			=> user should see the same map section
			=> original map section should not be cut off */
    	google.maps.event.addDomListener(window, "resize", function() {
     		var center = map.getCenter();
     		/* Google API:
     			Developers should trigger this event on the map
     			when the div changes size */
     		google.maps.event.trigger(map, "resize");
     		map.setCenter(center);
     		map.fitBounds(bounds);
     		// reopen infowindow
     		if(currInfoWindow.getContent() && currInfoWindow.getContent() !== ""){
	     		currInfoWindow.close();
	     		currInfoWindow.open(map);
     		}
    	});
	};
	var displayInfoWindow = function (loc) {
		var aRestaurants = [];
		var oWeather = {};
		var aRequests = [];
		var jqXHRWeather,
			jqXHRRestaurant;
		var sRestaurantTemplate = "";
		var sWeatherTemplate = "";

		var requestRestaurants = function (loc) {
			// Yelp Fusion does not support CORS
			// need to call backend coding to execute API call
			var jqXHR =  $.get({
				url: "/getYelpAPI",
				type: "GET",
        		data: {
            		"latitude": loc.coord.lat,
            		"longitude": loc.coord.lng,
            		"radius": 1000,
            		"categories": ["Restaurants"],
            		"limit": 5,
            		"sort_by": "rating"
        		},
        		dataType: "json"
			});
			return jqXHR;
		};
		var requestWeather = function (loc) {
			var sUrl = "http://api.openweathermap.org/data/2.5/weather";
			var jqXHR = $.ajax({
					url: sUrl,
					type: "GET",
					data: {
						"lat": loc.coord.lat,
						"lon": loc.coord.lng,
						"APPID": weatherAPIKey,
						"units": "metric"
					},
					dataType: "json"
				});
			return jqXHR;
		};
		var buildWeatherTemplate = function(oWeather){
			return `<img src="${oWeather.icon}">${oWeather.city}<br>
					${oWeather.text}<br>
					${oWeather.temp}&deg;C`;
		};
		var buildRestaurantTemplate = function(aRestaurants){
			return `<ul>
					${aRestaurants.map( (restaurant)=>{
						var distance = Math.round(restaurant.distance);
						var rating = "";
						for(var i=0; i<Math.floor(restaurant.rating); i++){
							rating += `<i class="fa fa-star" aria-hidden="true"></i>`;
						}
						if (restaurant.rating !== Math.floor(restaurant.rating)){
							rating += `<i class="fa fa-star-half-o" aria-hidden="true"></i>`;
						}
						return `<li><a href="${restaurant.url}" target="_blank">${restaurant.name}</a>
						<br>Rating: ${rating}
						(${restaurant.review_count} reviews)
							<br>${restaurant.address} (${distance} meters)</li>`
					} ).join("")}
					</ul>`;

		};
		var fillContent = function (loc, sWeatherTemplate, sRestaurantTemplate) {
				return `<div class="info-window">${loc.name}<br>
						<h4>Weather</h4>
						${sWeatherTemplate}
						<h4>Nearby Restaurants</h4>
						${sRestaurantTemplate}
						</div>`;
		};
		var onWeatherSuccess = function (data, textStatus, jqXHR) {
			if (textStatus === "success") {
				oWeather = {
					icon: "http://openweathermap.org/img/w/" + data.weather[0].icon + ".png",
					city: data.name,
					coord: {
						lat: data.coord.lat,
						lon: data.coord.lon
					},
					text: data.weather[0].description,
					temp: data.main.temp,
					humidity: data.main.humidity,
					pressure: data.main.pressure,
					wind: data.wind.speed,
				};
				sWeatherTemplate = buildWeatherTemplate(oWeather);
			}
		};
		var onRestaurantSuccess = function (data, textStatus, jqXHR) {
			if (textStatus === "success") {
				for (var i = 0; i < Math.min(5, data.businesses.length); i++) {
					var business = data.businesses[i];
					var restaurant = {};
					restaurant.name = business.name;
					restaurant.url = business.url;
					restaurant.review_count = business.review_count;
					restaurant.rating = business.rating;
					restaurant.img = business.image_url;
					restaurant.address = business.location.address1;
					restaurant.distance = business.distance;
					restaurant.coordinates =  {
						"lat": business.coordinates.latitude,
						"lng": business.coordinates.longitude
					};
					aRestaurants.push(restaurant);
				}
				sRestaurantTemplate = buildRestaurantTemplate(aRestaurants);
			}
		};
		jqXHRWeather = requestWeather(loc);
		jqXHRRestaurant = requestRestaurants(loc);
		aRequests.push(jqXHRWeather, jqXHRRestaurant);
		jqXHRWeather
				.then(onWeatherSuccess,
					  function (jqXHR, textStatus, errorThrown) {
						sWeatherTemplate = `Could not retrieve weather data: ${errorThrown}`;
				});
		jqXHRRestaurant
				.then(onRestaurantSuccess,
					  function (jqXHR, textStatus, errorThrown) {
						sRestaurantTemplate = `Could not retrieve restaurant data: ${errorThrown}`;
				});

		// Promise.all rejects when the first promise rejects
		// for this app, events should be displayed even if weather request fails and vice versa
		// turn the array of original promises into an array of state objects (=resolved promises by default)
		// promise.then, promise.then will execute then on the same promise in the order they were attached

		Promise
			.all(aRequests.map( (promise)=>{
									return promise.then(function(){
															return {state: "resolved"};
														},
														function(){
															return {state: "rejected"};
														})
								}))
			.then(function () {
				// close previously opened infowindow
				if(currInfoWindow){
					currInfoWindow.close();
				}
				var marker = markers.get(loc.name);
				currInfoWindow.setContent(fillContent(loc, sWeatherTemplate, sRestaurantTemplate));
				currInfoWindow.open(map, marker);
			});
	};
	var onFilter = function (mapVisibility) {
		// new selection
		if(currInfoWindow){
			currInfoWindow.close();
			currInfoWindow.setContent(undefined);
		}
		// close infowindow before bounds is reset
		// or else infowindow remains opened when location
		// becomes visible again (for example after deleting the filter)
		bounds = new google.maps.LatLngBounds();
		aLocations.forEach(function (loc) {
			if (mapVisibility.get(loc.name) === true) {
				markers.get(loc.name).setMap(null);
			} else {
				markers.get(loc.name).setMap(map);
			}
			bounds.extend(loc.coord);
		});
		map.fitBounds(bounds);
		map.setCenter(bounds.getCenter());
	};
	var onClickMarker = function (event) {
		handleMarker(this.title);
	};
	var handleMarker = function (locName) {
		var selectedMarker = markers.get(locName);

		map.setCenter(selectedMarker.getPosition());

		selectedMarker.setAnimation(google.maps.Animation.BOUNCE);
		setTimeout(function () {
			selectedMarker.setAnimation(null);
		}, 1500);
		aLocations.forEach(function(loc){
			if (loc.name === locName) {
				displayInfoWindow(loc);
				return;
			}
		})
	};
	var mapResize = function() {
		google.maps.event.trigger(map, "resize");
	}
	return {
		init: init,
		onFilter: onFilter,
		handleMarker: handleMarker,
		mapResize: mapResize
	};
})();
