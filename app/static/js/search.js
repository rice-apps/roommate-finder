var roommateFinder = angular.module("roommateFinder", []);

roommateFinder.config(function ($interpolateProvider, $sceProvider) {
    // Angular uses {{ }} by default to denote variables in HTML, but so does Flask/Jinja.
    // This changes Angular to use {[ ]} instead.
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
    // Disable this really annoying security shit
    $sceProvider.enabled(false);
});


// Listings controller
roommateFinder.controller("listingsControl", function($scope, $http) {
    // Retrieve listings data from database
    $http.get("/app.db", {"responseType": "arraybuffer"}).success(function(data) {
        var db = new SQL.Database(new Uint8Array(data));
        var listings_data = db.exec("SELECT * FROM listing INNER JOIN profile ON listing.poster_netid=profile.net_id")[0];
        var photos_data = db.exec("SELECT * from photo")[0];
        var preferences_data = db.exec("SELECT * FROM preferences")[0];
        $scope.listings = SQLiteToJSON(listings_data);
        $scope.preferences = SQLiteToJSON(preferences_data)[0];
        var photos = SQLiteToJSON(photos_data);

        // Manually insert a preview photo into the JSON object from the photo table
        //
        for (var i = 0; i < $scope.listings.length; i++)
            for (var j = 0; j < photos.length; j++) {
                if (photos[j].listing_id == $scope.listings[i].id)
                    $scope.listings[i]["photo"] = photos[j].hash;
            }

        // Sorting order
        if ($scope.preferences.sorting_preference != "null") {  // Even null is a string
            $scope.sortOrder = $scope.preferences.sorting_preference;
            if ($scope.preferences.sorting_preference == "size")
                $scope.sortOrder = "property_size";  // -.- lack of consistency on my part
        }
        else
            $scope.sortOrder = "timestamp";

        // Filtering logic
        // Entries here must match with those in listing.amenities_[amenity], where each column amenities_[amenity] in the database is true or false
        $scope.filterByAmenities = {"gym": $scope.preferences.amenities_gym == "true", "pool": $scope.preferences.amenities_pool == "true", "pet_friendly": $scope.preferences.amenities_pet_friendly == "true", "computer_room": $scope.preferences.amenities_computer_room == "true", "trash_pickup_services": $scope.preferences.amenities_trash_pickup_services == "true"};
        $scope.amenitiesFilter = function () {
        return function (listing) {
            if ($scope.filterByAmenities["gym"] && $scope.filterByAmenities["gym"].toString() != listing.amenities_gym)
                return false;
            if ($scope.filterByAmenities["pool"] && $scope.filterByAmenities["pool"].toString() != listing.amenities_pool)
                return false;
            if ($scope.filterByAmenities["pet_friendly"] && $scope.filterByAmenities["pet_friendly"].toString() != listing.amenities_pet_friendly)
                return false;
            if ($scope.filterByAmenities["computer_room"] && $scope.filterByAmenities["computer_room"].toString() != listing.amenities_computer_room)
                return false;
            if ($scope.filterByAmenities["trash_pickup_services"] && $scope.filterByAmenities["trash_pickup_services"].toString() != listing.amenities_trash_pickup_services)
                return false;
            return true;
        }
    };
    });

    // Full listing details show/hide logic
    $scope.selectedID = null;
    $scope.clicked = function(listing) {
        $scope.selectedID = listing.id;
    };
    $scope.showListing = function(listing) {
        return listing.id == $scope.selectedID;
    };

    // Google Maps API
    $scope.getMapUrl = function (address) {
        return "https://www.google.com/maps/embed/v1/place?key=AIzaSyChrd2_zI_bHbhUnyw1P7-e8wf2Rq9uiiQ&zoom=16&q=" + address;
    };
});


function SQLiteToJSON(arrays) {
    // As the name implies, takes as input an array-formatted SQLite database and very tediously converts it into a JSON object.
    // Input is index 0 of the result of SQL.js SELECT query.
    var result = "[";
    var columns = arrays.columns;
    var values = arrays.values;
    for (var i = 0; i < values.length; i++) {
        result += "{";
        for (var j = 0; j < columns.length; j++) {
            result += "\"" + columns[j] + "\":\"" + values[i][j] + "\"";
            if (j != columns.length - 1)
                result += ",";
        }
        if (i != values.length - 1)
            result += "},";
        else
            result += "}";
    }
    result += "]";
    return JSON.parse(result);
}