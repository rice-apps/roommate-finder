var roommateFinder = angular.module("roommateFinder", []);

// Angular uses {{ }} by default to denote variables in HTML, but so does Flask/Jinja.
// This changes Angular to use {[ ]} instead.
roommateFinder.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);


// Users controller
roommateFinder.controller("usersControl", function($scope, $http) {

    // Retrieve users data from database
    $http.get("/get_users").success( function( data ) {
        $scope.users = data.users;
    });
});