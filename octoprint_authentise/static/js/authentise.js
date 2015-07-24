$(function() {
  function AuthentiseConnectViewModel(parameters) {
    this.settings = parameters[0];

    this.apiRoot = "/plugin/authentise";

    this.onSubmit = $.proxy(function() {
      this.toggleLoading();

      var form = $("#authentise-connect"),
          data = {
            username: form.find("[name=authentise_user]").val(),
            password: form.find("[name=authentise_pass]").val()
          };

      var handleSuccess = $.proxy(function(result){
        this.clearForm();
        this.hideModal();
      }, this);

      var handleError = $.proxy(function(jqXHR, textStatus, errorThrown){
        var results = jqXHR.responseJSON;
        console.error("Error connecting to Authentise", results);
      }, this);

      $.ajax({
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        url: this.apiRoot + "/connect/",
        data: JSON.stringify(data),
        success: handleSuccess,
        error: handleError,
        complete: this.toggleLoading
      });

      return false;
    }, this);

    this.hideModal = $.proxy(function() {
      $("#authentise-connect").modal('hide');
    }, this);

    this.clearForm = $.proxy(function() {
      $("#authentise-connect .modal-body input").val(null);
    }, this);

    this.toggleLoading = $.proxy(function() {
      var form = $("#authentise-connect"),
          inputs = form.find(".modal-body input, .modal-footer .btn-primary"),
          spinner = form.find(".modal-footer .btn-primary > i");

      if(!form.prop("loading")) {
        inputs.addClass("disabled").prop("disabled", true);
        spinner.addClass("icon-spinner icon-spin");
        form.prop("loading", true);
        return;
      }

      inputs.removeClass("disabled").prop("disabled", false);
      spinner.removeClass("icon-spinner icon-spin");
      form.prop("loading", false);
    }, this);
  }

  OCTOPRINT_VIEWMODELS.push([
    AuthentiseConnectViewModel,
    ["settingsViewModel"],
    ['#navbar_plugin_authentise']
  ]);
});
