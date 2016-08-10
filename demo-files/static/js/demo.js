function setAjaxForm(formid, successFunction) {
  var frm = $(formid)
  frm.submit(function (ev) {
    $.ajax({
      type: frm.attr('method'),
      url: frm.attr('action'),
      data: frm.serialize()
    }).done(function (data) {
      successFunction(data);
    });

    ev.preventDefault();
  });
}

function setHtml(selector, message) {
  $(selector).html(message)
}

function flashMessage(message) {
  $("#message").html(message)
  $('#message').css({
    display: 'block'
  })
  $("#message").slideDown(500, function () {
    setTimeout(function () {
      $("#message").slideUp(500);
    }, 3000);
  });
}

function initMap(coords) {
  var map = L.map('leaflet-map').setView(coords, 16);
  var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  //  var osmUrl = 'http://tiles.mapc.org/basemap/{z}/{x}/{y}.png'
  var osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
  var osm = new L.TileLayer(osmUrl, {
    maxZoom: 18,
    attribution: osmAttrib
  }).addTo(map);
  //  map.invalidateSize();
  console.log("lol")
  return map
}

setAjaxForm('#start-data', function (data) {
  console.log(data.message)
  flashMessage(data.message)
});
setAjaxForm('#stop-data', function (data) {
  console.log(data.message)
  flashMessage(data.message);
});
setAjaxForm('#data-sample-form', function (data) {
  $('#data-sample').html(JSON.stringify(data, null, 2))
});
setAjaxForm('#data-update', function (data) {
  console.log(data)
  flashMessage(data.message)
});


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

$.ajax({
  type: "GET",
  url: "/data-gen/schema",
  success: function (data) {
    //    console.log(data)
    fmtd = JSON.stringify(JSON.parse(data.schema), null, 2);
    setHtml('#json-schema', fmtd)
    $('#data-sample-form').submit();
  }
});

$(document).delegate('#json-schema', 'keydown', function (e) {
  var keyCode = e.keyCode || e.which;

  if (keyCode == 9) {
    e.preventDefault();
    var start = $(this).get(0).selectionStart;
    var end = $(this).get(0).selectionEnd;

    // set textarea value to: text before caret + tab + text after caret
    $(this).val($(this).val().substring(0, start) + "  " + $(this).val().substring(end));

    // put caret at right position again
    $(this).get(0).selectionStart =
      $(this).get(0).selectionEnd = start + 1;
  }
});

var map = initMap([37.4133111, -121.9805886])
$(document).on("shown.bs.tab", "#map-view-tab", function () {
  map.invalidateSize(false);
});

$('#websockets-console-clear').on('click', function() {
  $('#websockets-console-data').html('')
})
