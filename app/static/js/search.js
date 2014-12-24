var roommateFinder = angular.module("roommateFinder", []);

// Angular uses {{ }} by default to denote variables in HTML, but so does Flask/Jinja.
// This changes Angular to use {[ ]} instead.
roommateFinder.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);


// Listings controller
roommateFinder.controller("listingsControl", function ($scope) {
    // Listings data
    // For all quantitative values, integers only
    $scope.listings = [
        {
            "id": "1",
            "apartment_name": "Rice Village",
            "poster_netid": "kl38",
            "poster_name": "Kevin Lin",
            "description": "Excellent apartments!",
            "address_line_1": "12345 Rice Village Lane",
            "address_line_2": "Houston, TX 77005",
            "photo": "disc.png",
            "distance": "0.65",
            "rent": "5000",
            "rent_details": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "property_size": "700",
            "number_roommates_needed": "4",
            "timestamp": 2,
            "amenities": {
                "gym": true,
                "pool": false
            }
        },
        {
            "id": "2",
            "apartment_name": "Kirby apartments",
            "poster_netid": "dl3",
            "poster_name": "Dave Lee",
            "description": "Excellent apartments, but not quite as nice.",
            "address_line_1": "12345 Kirby Lane",
            "address_line_2": "Houston, TX 77005",
            "photo": "computer.jpg",
            "distance": "0.76",
            "rent": "8000",
            "rent_details": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "property_size": "300",
            "number_roommates_needed": "2",
            "timestamp": 1,
            "amenities": {
                "gym": false,
                "pool": true
            }
        },
        {
            "id": "3",
            "apartment_name": "Luxury apartments",
            "poster_netid": "jd1",
            "poster_name": "John Doe",
            "description": "Luxury apartments!",
            "address_line_1": "12345 Luxury Lane",
            "address_line_2": "Houston, TX 77005",
            "photo": "computer.jpg",
            "distance": "0.1",
            "rent": "82000",
            "rent_details": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "property_size": "6000",
            "number_roommates_needed": "9",
            "timestamp": 4,
            "amenities": {
                "gym": true,
                "pool": true
            }
        }
    ];

    // Sorting order
    $scope.sortOrder = "timestamp";

    // Filtering logic
    // Need an if statement for each amenity. I couldn't figure out a cleaner way to do this.
    // Entries here must match with those in listing.amenities
    $scope.filterByAmenities = {};
    $scope.amenitiesFilter = function () {
        return function (listing) {
            if ($scope.filterByAmenities["gym"] && $scope.filterByAmenities["gym"] != listing.amenities.gym)
                return false;
            if ($scope.filterByAmenities["pool"] && $scope.filterByAmenities["pool"] != listing.amenities.pool)
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