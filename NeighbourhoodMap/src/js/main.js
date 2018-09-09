var filterAttr = ["name", "city"];
var geocodingAPIKey = "AIzaSyBj07gL_Lr5ayh0lvhV01Vys6W1d1j-UT0";
var weatherAPIKey = "e68029aa5eea565274d1d9a2c71898e5";
var yelpToken = "NMurae0tVFW6NvhG7PzrMT3VQc5DHkOUgYux-uNUPVsNwrYc6dC5Jzf9HbX98B0hOsWSLNlwo_db5FqwrCEnAZSE9dzT9rXIA_sFSTj0dG7GkPMKaHGxlKosvnFmWXYx";
var aTimeoutsLiveSearch = [];

var Location = function (data) {
	this.name = data.name;
	this.street = data.street;
	this.zip = data.zip;
	this.city = data.city;
	this.country = data.country;
	this.coord = {
		lat: data.lat,
		lng: data.lng
	};
};
var sharedData = (function () {
	var aLocations = [];
	var aErrorMessages = [];
	var requestLocations = function () {
		var jqXHR = $.get({
				url: "json/locations.json",
				dataType: "json"
			});
		return jqXHR;
	};
	var requestCoord = function (aAllLocations) {
		var promises = [];

		aAllLocations.forEach(function (elem) {
			var sUrl = "https://maps.googleapis.com/maps/api/geocode/json";
			var sAddress = `${elem.street} ${elem.zip} ${elem.city} ${elem.country}`;
			var jqXHR = $.ajax({
					url: sUrl,
					data: {
						"address": sAddress,
						"key": geocodingAPIKey
					},
					dataType: "json"
				});
			jqXHR
				.then(function (data,textStatus,jqXHR) {
						if (data.status === "OK"){
							elem.coord.lng = data.results[0].geometry.location.lng;
							elem.coord.lat = data.results[0].geometry.location.lat;
							// only work with locations with coordinates
							aLocations.push(elem);
						}
						else{
							if(data.error_message){
								// display every error message only once
								if(!aErrorMessages.includes(data.error_message)){
									aErrorMessages.push(data.error_message);
								}
							};
							throw data.status;
						}
				})
				.catch(function(){
					aErrorMessages.push(`${elem.name}: Could not retrieve coordinates`);
				});
			promises.push(jqXHR);
		});
		// even if coordinate requests fail for some locations,
		// app should still work for the other locations
		// Promise.all only useful for "all-or-nothing" approach
		return Promise
				.all(promises.map(function(promise){
						return promise.then(
							function(){
								return {status: "resolved"};
							},
							function(){
								return {status: "rejected"};
							});
					}));
	};
	var init = function () {
		return requestLocations()
						.then(
							function(data,textStatus,jqXHR){
								var aAllLocations = [];
								data.forEach((elem) => {
									aAllLocations.push(new Location(elem));
								});
								return requestCoord(aAllLocations);
							},
							function(data,textStatus,jqXHR){
								//error handler for requestLocations()
								aErrorMessages.push("Failed to load locations from server");
								throw "Failed to load locations from server";
						});
	};
	var getLocations = function () {
		return aLocations;
	};
	var getMessages = function(){
		return aErrorMessages;
	};
	return {
		init: init,
		getMessages: getMessages,
		getLocations: getLocations
	};
})();

var ViewModel = function (aInitErrorMessages) {
	/* live search: timeout keeps track of last change */
	var timeout;
	var self = this;
	if(aInitErrorMessages){
		self.errorMessages = ko.observableArray(aInitErrorMessages);
		self.msgClose = ko.observable(false);
	}
	else{
		self.errorMessages = ko.observableArray([]);
		self.msgClose = ko.observable(true);
	}
	self.errorsExist = ko.computed(function () {
			return self.errorMessages().length > 0 ? true : false;
		});
	self.filter = ko.observable(filterAttr[0]);
	self.placeholder = ko.computed(function(){
		return `Enter ${self.filter()}`;
	});
	self.filterTerm = ko.observable("");
	self.locations = ko.observableArray(sharedData.getLocations());
	self.menuExpanded = ko.observable(!window.matchMedia("(max-width: 600px)").matches);

	self.filterTerm.subscribe(function(){
		/* clear previous timeout
		=> filter method will only be triggered if >0.5s passed */
		clearTimeout(timeout);
		/* overwrite with new timeout */
		timeout = setTimeout(self.onFilter,500)
	});
	self.filter.subscribe(function(){
		if (self.filterTerm() !== ""){
			self.onFilter();
		}
	});
	self.onFilter = function () {
		var aSelectedLoc = [];
		var mapVisibility = new Map();
		sharedData.getLocations().forEach(function (loc, idx) {
			var hide = false;
			/* empty filter --> display all */
			if (self.filterTerm() !== "") {
				/* starts with case-insensitive filterTerm */
				var regExp = new RegExp("^" + self.filterTerm() + "+", "i")
				var hide = loc[self.filter()].match(regExp) ? false : true;
			}
			if (!hide) {
				aSelectedLoc.push(loc);
			};
			mapVisibility.set(loc.name, hide);
		});
		self.locations(aSelectedLoc);
		mapModule.onFilter(mapVisibility);
	};
	self.onCloseMsg = function(){
		self.msgClose(true);
	}
	self.onClick = function (oSelectedLoc) {
		// hide list on small screen if list is already displayed
		if(self.menuExpanded() && window.matchMedia("(max-width: 600px)").matches){
			self.menuExpanded(!self.menuExpanded());
		}
		mapModule.handleMarker(oSelectedLoc.name);
	};
	self.toggleMenu = function(){
		self.menuExpanded(!self.menuExpanded());
		// resize map properly (or else grey areas will appear in the map)
		mapModule.mapResize();
	};
	self.redetermineMediaQuery = function(){
		self.menuExpanded(window.matchMedia("(max-width: 600px)").matches ? false : true);
	};
};
var startApp = function(){
	sharedData.init().done(function () {
		var vm = new ViewModel(sharedData.getMessages());
		ko.applyBindings(vm);
		mapModule.init(vm);
		$(window).on("resize",function(){
		vm.redetermineMediaQuery();
		})
	})
	.fail(function(){
		ko.applyBindings(new ViewModel(sharedData.getMessages()));
	});
};
var onGoogleError = function(){
	sharedData.init().done(function(){
		var aErrorMsg = ["Google maps failed to load"];
		ko.applyBindings(new ViewModel(aErrorMsg));
	});
};