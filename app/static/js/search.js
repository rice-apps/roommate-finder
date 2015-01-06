var roommateFinder = angular.module("roommateFinder", []);

// Angular uses {{ }} by default to denote variables in HTML, but so does Flask/Jinja.
// This changes Angular to use {[ ]} instead.
roommateFinder.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);


// Listings controller
roommateFinder.controller("listingsControl", function($scope, $http) {
    // Retrieve listings data from database
    $http.get("/app.db", {"responseType": "arraybuffer"}).success(function(data) {
        var uInt8Array = new Uint8Array(data);
        var db = new SQL.Database(uInt8Array);
        var contents = db.exec("SELECT * FROM listing")[0];
        $scope.listings = SQLiteToJSON(contents);
    });

    // Sorting order
    $scope.sortOrder = "timestamp";

    // Filtering logic
    // Need an if statement for each amenity. I couldn't figure out a cleaner way to do this.
    // Entries here must match with those in listing.amenities_[amenity], where each column amenities_[amenity] in the database is true or false
    $scope.filterByAmenities = {};
    $scope.amenitiesFilter = function () {
        return function (listing) {
            if ($scope.filterByAmenities["gym"] && $scope.filterByAmenities["gym"].toString() != listing.amenities_gym)
                return false;
            if ($scope.filterByAmenities["pool"] && $scope.filterByAmenities["pool"].toString() != listing.amenities_pool)
                return false;
            return true;
        }
    };

    // Full listing details show/hide logic
    $scope.selectedID = null;
    $scope.clicked = function(listing) {
        $scope.selectedID = listing.id;
    };
    $scope.showListing = function(listing) {
        return listing.id == $scope.selectedID;
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