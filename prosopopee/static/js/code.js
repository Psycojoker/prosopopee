var context = {
  "current_gallery": "/build/",
  "current_images": "",
  "CodeMirror": null
}

$(function() {
  // init
  var _theframe = document.getElementById("buildIframe");
  _theframe.contentWindow.location.href = _theframe.src;

  // url changed in frame
  iframeSrcChanged = function(iframe) {
    console.log("-> " + context["current_gallery"]);
    context["current_gallery"] = iframe.contentWindow.location.pathname
      $.get("/settings" + context["current_gallery"] + "?_=" + (new Date).getTime()).done(function(data) {
        if (context.CodeMirror === null) {
          context.CodeMirror = CodeMirror.fromTextArea(document.getElementById("editor"), {mode: "yaml", theme: "dracula"})
        }
        context.CodeMirror.setValue(data);
      })

    if (context["current_gallery"] != "/build/") {
      $("#imagesZone").addClass("active");
      updateGalleryImages(context["current_gallery"]);
    } else {
      $("#imagesZone").removeClass("active");
    }
  }

  var updateGalleryImages = function(path) {
    $("#currentGalleryImages").html('<div class="loader"></div>').addClass("loading");
    $.get("/images" + path).done(function(data) {
      $("#currentGalleryImages").html(data).removeClass("loading");
      if (data != context["current_images"]) {
        context["current_images"] = data;
      }
    })
  }

  // update settings
  var save = function(event) {
    event.preventDefault();
    $("#save").addClass("loading").html("saving...");
    $.post("/save_settings" + context["current_gallery"], $("#saveForm").serialize())
      .done(function() {
        // dirty hack for save data
        $.post("/save_settings" + context["current_gallery"], $("#saveForm").serialize())
          $("#save").removeClass("loading").html("save");
        document.getElementById('buildIframe').contentWindow.location.reload();
      });
    updateGalleryImages(context["current_gallery"]);
  }

  $("#saveForm").submit(save);
  $("#editor").on('keydown', null, 'ctrl+s', save);


  $("#newGallery").click(function() {
    var folder_name = document.getElementById("folder").value;
    if (folder_name === null) return;
    var title = document.getElementById("title").value;
    if (title === null) return;
    var date = document.getElementById("date").value;
    if (date === null) return;
    var cover = document.getElementById("cover").files[0].name;
    if (cover === null) return;

    if (confirm("Are those correct?\nFolder name: " + folder_name + "\nTitle : " + title + "\nDate : " + date + "\nCover : " + cover)) {
      $.post("/new_gallery/", {folder_name: folder_name, title: title, date: date, cover: cover})
        .done(function(data) {
          // TODO doesn't support sub_galleries
          _theframe.contentWindow.location.href = _theframe.baseURI + "build/" + folder_name + "/";
          context["current_gallery"] = iframe.contentWindow.location.pathname
        })
    }
    // Fix upload file
    // $.post("/upload_images/", $("#cover").serialize());
    $('#modal1').modal('close');
    $('.btn-floating').sideNav('show');
  })

  $("#uploadImagesButton").click(function() {
    $("#uploadImagesPath").val(context["current_gallery"]);
    $("#uploadImagesInput").click();
    // console.log($("#uploadImagesForm").serialize());
    // $.post("/upload_images" + context["current_gallery"], $("#uploadImagesForm").serialize());
  })

  $("#uploadImagesInput").on("change", function() {
    console.log("prout");
    $("#uploadImagesForm").ajaxForm().submit();
    updateGalleryImages(context["current_gallery"]);
  })

})

$('.btn-floating').sideNav({
  menuWidth: '70%',
  edge: 'left',
  closeOnClick: true,
}
);

$(document).ready(function() {
  $('select').material_select();
});

$(document).ready(function(){
  $('.modal').modal();
});

$('.datepicker').pickadate({
  selectMonths: true,
  selectYears: 17,
  format: 'yyyy-mm-dd'
});
