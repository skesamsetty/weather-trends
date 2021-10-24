// Creating our initial map object:
// We set the longitude, latitude, and starting zoom level.
// This gets inserted into the div with an id of "map".
// var myMap = L.map("map", {
//   center: [34.0689, -118.4452],
//   zoom: 14
// });

// function loadHomepage(event=null)
// {
//   console.log(event);

//   let dropdownMenu = document.getElementById("selDataset");
//   let shortLocation;
//   if (dropdownMenu == null)  {
//     shortLocation = "UCLA";
//   }
//   else
//   {
//     shortLocation = dropdownMenu.options[dropdownMenu.options.selectedIndex].value;
//   }

d3.json("/data2").then(function(data){

  // Set values for dropdown menu
  let campusLocations = data["locations"];
  var dropdownOptions = [];
  for (let i = 0; i < campusLocations.length; i++) {
    let campus = campusLocations[i];
    let campusName = campus["locationName"];
    let shortName = campus["shortName"];
      
    dropdownOptions.push({"shortName": shortName, "campusName": campusName});
  }

  // Use D3 to select dropdown menu
  var dropdown = d3.select("#selDataset");

  // Append dropdown options to menu
  dropdownOptions.forEach(option => {
    dropdown.append("option").text(option["campusName"]).attr("value", option["shortName"]).attr("name", option["shortName"]);
  });

// do not use data anymore
});

d3.json("/data2").then(function(locationData){

  // Leaflet map
  let lat = parseFloat(locationData["locations"][0]["latitude"])
  let lon = parseFloat(locationData["locations"][0]["longitude"])
  console.log(`${lat}, ${lon}`)

  var myMap = L.map('map').setView([lat, lon], 15);


  L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/light-v10',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoibmFwcHl0cmFpbHMiLCJhIjoiY2t1dXBvYXJ1MWlhNzJ1cGphZXJ3MHJ4diJ9.r-J1-mrEKBLhc2V3Kw5wXA'
  }).addTo(myMap);


  // Then move the map
  //myMap.panBy(new L.Point(0, -75), {animate: false});

  // Creating a new marker:
  var campus = L.circle([34.0689, -118.4452], {
    color: "#70DB70",
    weight: 15,
    stroke: true,
    fillColor: "yellowgreen",
    fillOpacity: 0.5,
    radius: 550
  }).addTo(myMap);

  // Binding a popup to the circle
  campus.bindPopup("<center><b>Current<br>Conditions</b><br><img src='https://api.weather.gov/icons/land/day/skc?size=medium'><br><hr><b>Sunny</b><br>Temperature: 75° F<br>Wind Speed: 5mph<br>Wind Direction: NNW</center>");

  // Weekly forecast
  let dailyForecasts = locationData["dailyForecasts"];
  var forecastPeriods = [];
  for (let i = 0; i < dailyForecasts.length; i++) {
    let period = dailyForecasts[i];
    let periodResponseName = period["daily_responseName"];
    let periodStartDate = period["daily_startDate"];
    let periodIcon = period["daily_icon"];
    let periodShortForecast = period["daily_shortForecast"];
    let periodTemperature = period["daily_temperature"];
    let periodDetailedForecast = period["daily_detailedForecast"];
    
    forecastPeriods.push({"periodResponseName": periodResponseName, "periodStartDate": periodStartDate, "periodIcon": periodIcon, "periodShortForecast": periodShortForecast, "periodTemperature": periodTemperature, "periodDetailedForecast": periodDetailedForecast});
  }
  console.log(forecastPeriods);

  var weeklyForecast = d3.select("#period-forecasts");

  // forecastPeriods.forEach(period => {
  //   weeklyForecast.append("p").text(period["periodStartDate"])//.property("value", option["periodDetailedForecast"]);
  // }
  for (let i = 0; i < forecastPeriods.length; i++) {
    console.log(forecastPeriods[i]["periodIcon"]);
    let auxp = weeklyForecast.append("p");
    auxp.append("h4").text(forecastPeriods[i]["periodResponseName"] + " (" + forecastPeriods[i]["periodStartDate"] + ")");
    auxp.append("img").attr("src", forecastPeriods[i]["periodIcon"]);
    auxp.append("div").text(forecastPeriods[i]["periodShortForecast"])
    auxp.append("div").text(forecastPeriods[i]["periodTemperature"] + "° F");
    auxp.append("div").text(forecastPeriods[i]["periodDetailedForecast"])
    auxp.append("hr").attr("class", "weather-divider")
    } 

// do not use localData anymore
});

// }


// loadDropdown();
// loadHomepage();

// // let dropdownMenu = document.getElementById("selDataset")
// // dropdownMenu.addEventListener("change", loadHomepage);

// document.getElementById("selDataset").addEventListener("change", function(event){
//   // console.log(event)
//   console.log(dropdownMenu.options[dropdownMenu.options.selectedIndex].value)
// })

