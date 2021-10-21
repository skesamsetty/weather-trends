// Creating our initial map object:
// We set the longitude, latitude, and starting zoom level.
// This gets inserted into the div with an id of "map".
// var myMap = L.map("map", {
//   center: [34.0689, -118.4452],
//   zoom: 14
// });
d3.json("/names").then(x => (
  console.log(x)
));

var myMap = L.map('map').setView([34.0689, -118.4452], 15);

// mapURL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

// mapURL = "https://api.mapbox.com/styles/v1/nappytrails/mapbox/streets-v11/tiles/0/0/0?access_token=pk.eyJ1IjoibmFwcHl0cmFpbHMiLCJhIjoiY2t1dXBvYXJ1MWlhNzJ1cGphZXJ3MHJ4diJ9.r-J1-mrEKBLhc2V3Kw5wXA"
// attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

// Adding a tile layer (the background map image) to our map:
// We use the addTo() method to add objects to our map.
// L.tileLayer(mapURL, {
//     attribution: attribution,
//     zoomOffset: -1
// }).addTo(myMap);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
  maxZoom: 18,
  id: 'mapbox/light-v10',
  tileSize: 512,
  zoomOffset: -1,
  accessToken: 'pk.eyJ1IjoibmFwcHl0cmFpbHMiLCJhIjoiY2t1dXBvYXJ1MWlhNzJ1cGphZXJ3MHJ4diJ9.r-J1-mrEKBLhc2V3Kw5wXA'
}).addTo(myMap);


// Calculate the offset
// var offset = myMap.getSize().x*0.05;
// Then move the map
myMap.panBy(new L.Point(0, -75), {animate: false});

// Creating a new marker:
// We pass in some initial options, and then add the marker to the map by using the addTo() method.
var campus = L.circle([34.0689, -118.4452], {
  color: "#70DB70",
  weight: 15,
  stroke: true,
  fillColor: "yellowgreen",
  fillOpacity: 0.5,
  radius: 550
}).addTo(myMap);

// Binding a popup to our marker
campus.bindPopup("<center><b>Current<br>Conditions</b><br><img src='https://api.weather.gov/icons/land/day/skc?size=medium'><br><hr><b>Sunny</b><br>Temperature: 75° F<br>Wind Speed: 5mph<br>Wind Direction: NNW</center>");
// campus.bindPopup("<img src='https://api.weather.gov/icons/land/day/skc?size=medium'><br><hr><b>Sunny</b><br>Temperature: 75° F<br>Wind Speed: 5mph<br>Wind Direction: NNW").openPopup();