function fileUpdates() {
  $(function () {
    // We can attach the `fileselect` event to all file inputs on the page
    $(document).on('change', ':file', function () {
      var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
      input.trigger('fileselect', [numFiles, label]);
    });

    // We can watch for our custom `fileselect` event like this
    $(document).ready(function () {
      $(':file').on('fileselect', function (event, numFiles, label) {

        var input = $(this).parents('.input-group').find(':text'),
          log = numFiles > 1 ? numFiles + ' files selected' : label;

        if (input.length) {
          input.val(log);
        } else {
          if (log) alert(log);
        }

      });
    });

  });
}

function setAjaxForm(formid, successFunction) {
  var frm = $(formid)
  frm.submit(function (ev) {
    $.ajax({
      type: frm.attr('method'),
      url: frm.attr('action'),
      data: frm.serialize()
    }).done(function(data){
      successFunction(data);
    });

    ev.preventDefault();
  });
}

fileUpdates();

setAjaxForm('#start-data', function (data) {
  console.log(data)
});
setAjaxForm('#stop-data', function (data) {
  console.log(data)
});
setAjaxForm('#data-sample-form', function (data) {
  console.log(data)
});
setAjaxForm('#data-update', function (data) {
  console.log(data)
});