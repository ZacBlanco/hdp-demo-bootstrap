/* Setup the AJAX on the demo UI control forms. */
/* It's imperative that these are first Stops redirects before fetching the schema*/
setAjaxForm('#start-data', function (data) {
  flashMessage(data.message)
});
setAjaxForm('#stop-data', function (data) {
  flashMessage(data.message);
});
setAjaxForm('#data-sample-form', function (data) {
  $('#data-sample').html(JSON.stringify(data, null, 2))
});
setAjaxForm('#data-update', function (data) {
  flashMessage(data.message)
});

/* Init Map on the UI */
var map = initMap([37.4133111, -121.9805886])

/* Setup Websockets */
var ws = demoWebsocket();

setupClearWebsocketsConsole();
setupTextareaAllowTabs();
getDataSchema();
setupUpdateJSONSchema();

function getHost() {
  /* Returns the hostname from window.location */
  return window.location.hostname
}


function wsPort() {
  /* Gets the port that the demo websockets server should be running on
  
  The websockets port should always be +1 on the http web port
  
  
  */
  if (window.location.port == "" && window.location.protocol == "http:") {
    return 81 // port 80 + 1
  } else if (window.location.port == "" && window.location.protocol == "https:") {
    return 444 // 443 + 1
  } else {
    return Number(window.location.port) + 1;
  }
}

function getWsUrl() {
  /* Gets the URL for the websockets connection */
  return 'ws://' + getHost() + ":" + wsPort();
}

function demoWebsocket() {
  /* Use this object to define behavior for websocket connections
  
  To access the data in the message use `ev.data`
  
  onopen - functionality for when the connection opens
  opclose - funtionality for when the connection closes
  onmessage - the functionality for when the client receives a message from the server
      This is the "meat" of the connection. Most of your logic will probably go here
  onerror - What to do in the event of a connetion error
  */
  var self = this;
  self.connected = false;
  self.url = getWsUrl();

  self.connect = function (url) {
    self.ws = new WebSocket(url);

    /*These function must be set for every new websocket object*/
    self.ws.onopen = function (ev) {
      console.log('Websocket: opened new connection')
      self.connected = true;
      self.updateConnectionStatus(self.connected);


      //Add code below this
    };

    self.ws.onclose = function (ev) {
      console.log('Websocket: closed connection')
      self.connected = false;
      self.updateConnectionStatus(self.connected);


      //Add code below this
    };

    self.ws.onmessage = function (ev) {
      console.log('Websocket: received message')

      //Do stuff with ev.data
      //      console.log(ev.data)


      //      Lat/Lon. Demo for plotting markers
      //      
      //      var data = JSON.parse(ev.data);
      //      for(i = 0; i < data.length; i++) {
      //        lat = data[i].lat
      //        lon = data[i].lon
      //        L.marker([lat, lon]).addTo(map);
      //      }
      //      fmtd = JSON.stringify(JSON.parse(ev.data), null, 2)
      //      self.logSocket("<pre>" + fmtd + "</pre>")
    };

    self.ws.onerror = function (ev) {
      self.connected = false;
      self.logSocket('Error connecting to websocket server')
      self.updateConnectionStatus(self.connected);
    };

    self.checkConnection = function () {
      self.updateConnectionStatus(self.connected);
      if (self.connected == false) {
        self.ws = self.connect(self.url);
      }
    }
    return self.ws
  }

  self.logSocket = function (message) {
    var msg = message + '<br>';
    $('#websocket-console-data').append(msg)
  }

  self.updateConnectionStatus = function (connected) {
    if (connected == true) {
      $('#websocket-connection-status').removeClass().addClass('label label-success connection-label').html('Connected')
    } else if (connected == false) {
      $('#websocket-connection-status').removeClass().addClass('label label-danger  connection-label').html('Disconnected')
    }
  }

  self.ws = self.connect(self.url);


  //Set an interval to check whether or not our socket is connected.
  setInterval(function () {
    self.checkConnection(self.connected)
  }, 5000);

}

function setAjaxForm(formid, successFunction) {
  /* Allow a form to submit via AJAX instead of reloading or requesting a different page
  
  Args:
    formid (query selector): A jquery selector of the form you want to change. Should only return one form.
    successFunction (function): A callback that runs when the form successfully submits
    
  Returns:
    N/A
  */
  var frm = $(formid)
  frm.submit(function (ev) {
    $.ajax({
      type: frm.attr('method'),
      url: frm.attr('action'),
      timeout: 5000,
      data: frm.serialize(),
      error: function (xhr, textStatus, errorThrown) {
        if (xhr.readyState === 0) {
          flashMessage('Network connection error')
        }
      }
    }).done(function (data) {
      successFunction(data);
    });

    ev.preventDefault();
  });
}

function setHtml(selector, message) {
  /*Simple wrapper function on a jquery function
  
  Args:
    selector (jquery selector): The selector for the element(s) that you wish to change
    message (string): The innerhtml of the elements that will be displayed
    
  Returns:
    N/A
  */
  $(selector).html(message)
}

function flashMessage(message) {
  /*Flash a message at the top of the screen. Useful for displaying request responses
  
  Args:
    message(string): The string to display when flashed
    
  Returns:
    N/A
  */
  $("#message").html(message)
  $('#message').css({
    display: 'block'
  })
  $("#message").slideDown(500, function () {
    setTimeout(function () {
      $("#message").slideUp(500);
    }, 5000);
  });
}

function initMap(coords) {
  /* Initializes the map on the tab "Map View"
  
  Args:
    coords (array): A two item array of lat, lon coordinates to center the map on.
  
  Returns:
    N/A
  */
  var map = L.map('leaflet-map').setView(coords, 16);
  var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  var osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
  var osm = new L.TileLayer(osmUrl, {
    maxZoom: 18,
    attribution: osmAttrib
  }).addTo(map);

  $(document).on("shown.bs.tab", "#map-view-tab", function () {
    map.invalidateSize(false);
  });
  return map
}

function setupUpdateJSONSchema() {
  /* A function that sets up a handler to update the generator JSON schema 
  
  "#json-schema" is the textarea which holds the JSON schema. We extract the value from this element
  
  For the behavior on the HTTP endpoint see the demo_server.py with the endpoint /data-gen/update
  */
  $('#json-schema').on('input', function () {
    jsonString = $("#json-schema").val()
    dat = ""
    try {
      dat = JSON.parse(jsonString)
      $.ajax({
        type: "POST",
        url: "/data-gen/update",
        data: jsonString,
        success: function (data) {
          $('#data-sample-form').submit();
          setHtml('#schema-alert', data.message)
        },

        dataType: "json",
        contentType: 'application/json'
      });
    } catch (err) {
      setHtml('#schema-alert', err)
    }

  });
}


function getDataSchema() {
  /* Function that retrieves the generator schema and sets it to the #json-schema value
  
  Also gets a sample of data from the schema.
  */
  $.ajax({
    type: "GET",
    url: "/data-gen/schema",
    success: function (data) {
      fmtd = JSON.stringify(JSON.parse(data.schema), null, 2);
      setHtml('#json-schema', fmtd)
      $('#data-sample-form').submit();
    }
  });
}

function setupTextareaAllowTabs() {
  /* This function allows us to use the tab key in the textarea
  
  Instead of inserting a tab we add in two (2) spaces at the cursor location
  
  */
  $(document).delegate('#json-schema', 'keydown', function (e) {
    var keyCode = e.keyCode || e.which;

    if (keyCode == 9) {
      e.preventDefault();
      var start = $(this).get(0).selectionStart;
      var end = $(this).get(0).selectionEnd;

      // set textarea value to: text before caret + spaces + text after caret
      $(this).val($(this).val().substring(0, start) + "  " + $(this).val().substring(end));

      // put caret at right position again
      $(this).get(0).selectionStart =
        $(this).get(0).selectionEnd = start + 1;
    }
  });
}

function setupClearWebsocketsConsole() {
  /*Sets a listener function which will clear the websockets console on the click of the button
   */
  $('#websockets-console-clear').on('click', function () {
    $('#websocket-console-data').html('')
  })
}