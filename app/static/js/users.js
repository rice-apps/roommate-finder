var roommateFinder = angular.module("roommateFinder", []);

// Angular uses {{ }} by default to denote variables in HTML, but so does Flask/Jinja.
// This changes Angular to use {[ ]} instead.
roommateFinder.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);


// Listings controller
roommateFinder.controller("usersControl", function($scope, $http) {
    // Retrieve listings data from database
    $http.get("/app.db", {"responseType": "arraybuffer"}).success(function(data) {
        var uInt8Array = new Uint8Array(data);
        var db = new SQL.Database(uInt8Array);
        var contents = db.exec("SELECT * FROM profile")[0];
        $scope.users = SQLiteToJSON(contents);
    });
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