var rweek = {};
rweek["lat"] = 40.8080250;
rweek["lng"] = -73.9621343;

function updateRestTable() {
    $("#rViewer").tablesorter({
        //default sort by rating from highest to lowest, then closest to furthest away 
        sortList:[[5, 1], [4,0]],
        widgets:['zebra']
      });

    for(var i in rweek.rests) {
        if(updateDistance(i, rweek.rests[i].yelp_id)) {
          updateDirectionLink(i, rweek.rests[i].yelp_id);
        } else {
          displayAddressError();
          return false;
        }
    }
    return true;
    
  function updateDistance(name, id) {
    var el = $('#' + id + 'Distance')[0];
    var dLat = rweek.rests[name].lat;
    var dLng = rweek.rests[name].lng;
    var distance = getDistance(rweek['lat'], rweek['lng'], dLat, dLng, 'mi');
    if(distance < 100) {
      el.innerHTML = distance + ' miles';
      return true;
    } else {
      return false;
    }

    function getDistance(sLat, sLng, dLat, dLng, units) {
      units = units || 'mi';
      var r_map = {
        'mi':3963.0,
        'km':6378.7
      }
      var r = r_map[units] || r_map['mi']
      x = Math.sin(sLat/57.2958) * Math.sin(dLat/57.2958) + Math.cos(sLat/57.2958) * Math.cos(dLat/57.2958) * Math.cos(dLng/57.2958 - sLng/57.2958);
      var d = r * Math.atan(Math.sqrt(1 - Math.pow(x, 2)) / x);
      //round to 100ths
      d = Math.floor(d * 100);
      d /= 100;
      return d;
    }
  }

  function updateDirectionLink(name, id) {
    var el = $('#' + id + 'Directions')[0];
    var end = rweek.rests[name].address;
    var start = $('#address')[0].value;
    start = start === 'Enter Address' ? 'Columbia University' : start;
    el.href = "http://maps.google.com/maps?f=d&source=s_d&daddr=" + end + "&saddr=" + start;
  }

  function unesc(name) {
    console.log(unescape(name.replace(/&amp;|&lt;|&gt;/g, '').replace('/', '\\/')));
    return unescape(name.replace(/&amp;|&lt;|&gt;/g, '').replace('/', '\\/'));

    function jq(myid) { 
     return myid.replace(/(:|\.)/g,'\\$1');
    } 
  }
}

function setHolderText(selector, text) {

  $(selector)[0].value = text;

  $(selector).focus(function() {
      if(this.value === text) {
        this.value = "";
      }
    });

  $(selector).blur(function() {
      if(this.value === "") {
        this.value = text;
      }
    });
}

function makeQTips() {
  $('.rinput').qtip({
      content:false,
      position:{
      corner:{
          target:'bottomRight',
          toolTip:'bottomLeft'
        }
      },
      style:{ 
        name:'blue',
        padding: '7px 13px',
        tip: true
        }
      });
}

function updateAddress(loc) {
  $('#addressError').fadeOut();
  if(loc === '') return;
  geocoder = new google.maps.Geocoder();
  codeAddress(loc);

  function codeAddress(query) {
    geocoder.geocode( { 'address': query}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK && results[0] && results[0].geometry && results[0].geometry.location) {
        rweek.lat = results[0].geometry.location.lat();
        rweek.lng = results[0].geometry.location.lng();
        updateRestTable();
      } else {
        displayAddressError();
      }
    });
  }

}

function displayAddressError() {
   $("#addressError").fadeIn(); 
}


$(document).ready(function(){

  updateRestTable();

  /*
  $('.extLink').each(function(index, element) {
    console.log(this);
    this.click(function(e) {
      e.preventDefault();
    });
  });
  */

  $('.extLink').click(function(e) {
      //open link in new window or tab, depending on browser
      window.open(this.href);
      e.preventDefault();
    });

  $('input#rSearch').quicksearch('table#rViewer tbody tr');
  
  $('#address').blur(function() {
      updateAddress(this.value);
  });

  $('#address').keyup(function(e) {
      //enter key
      if(e.keyCode === 13) {
        updateAddress(this.value);
      }
    });

  setHolderText('#rSearch', 'Restaurants'); 
  setHolderText('#address', 'Columbia University');
  makeQTips();

});

