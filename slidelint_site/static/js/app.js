LinterApp = angular.module('LinerApp', ['angularFileUpload', 'ui.bootstrap']);
LinterApp.factory('GlobalDataSharing', function() {
  var upload_file_info = {
      uploading_progress : 0
  }
  return {
    upload_file_info : upload_file_info
  };
});

var LinterCtrl = [ '$scope', 'GlobalDataSharing', '$upload', '$http', '$timeout', '$modal',
  function($scope, GlobalDataSharing, $upload, $http, $timeout, $modal) {
  $scope.check_rule = 'simple';
  $scope.job_uid = false;
  $scope.error = false;
  $scope.results = [];
  $scope.upload_file_info = GlobalDataSharing.upload_file_info;
  $scope.getResults = function(){
    if ($scope.job_uid !== false){
      $http.post('/results', {'uid': $scope.job_uid},
          {headers: {'Content-Type': 'application/json'}})
        .success(function(data, status, headers, config) {
            $scope.job_uid = false;
            $scope.upload_file_info.uploading_progress = 0;
            $scope.icons = data.icons;
            $scope.results = data.result;
            $scope.showResults = true;
            $scope.modalInstance.dismiss();
        }).
        error(function(data, status, headers, config) {
          // called asynchronously if an error occurs
          // or server returns response with an error status.
          if (status === 500) {
              $scope.job_uid = false;
              $scope.upload_file_info.uploading_progress = 0;
              $scope.error = data.result;
              $scope.showResults = true;
              $scope.modalInstance.dismiss();
          };
        });
    };
  };
  $scope.intervalFunction = function(){
    $timeout(function() {
      $scope.getResults();
      $scope.intervalFunction();
    }, 1000)
  };
  $scope.intervalFunction();
  $scope.onFileSelect = function($files) {
    //$files: an array of files selected, each file has name, size, and type.
    for (var i = 0; i < $files.length; i++) {
      var file = $files[i];
      $scope.open_waiting_modal()
      $scope.upload = $upload.upload({
        url: '/upload',
        // method: POST or PUT,
        // headers: {'headerKey': 'headerValue'}, withCredential: true,
        data: {check_rule: $scope.check_rule},
        file: file,
        // file: $files, //upload multiple files, this feature only works in HTML5 FromData browsers
        /* set file formData name for 'Content-Desposition' header. Default: 'file' */
        //fileFormDataName: myFile,
        /* customize how data is added to formData. See #40#issuecomment-28612000 for example */
        //formDataAppender: function(formData, key, val){}
      }).progress(function(evt) {
        $scope.upload_file_info.uploading_progress = parseInt(100.0 * evt.loaded / evt.total);
      }).success(function(data, status, headers, config) {
        // file is uploaded successfully
        // data = JSON.parse(data);
        uid = data.uid;
        rez_status = data.status;
        $scope.job_uid = uid;
        console.log(data);
      });
      //.error(...)
      //.then(success, error, progress);
    }
  };

  $scope.open_waiting_modal = function () {

    $scope.modalInstance = $modal.open({
        templateUrl: '/static/templates/waiting.html',
        controller: ModalInstanceCtrl,
        resolve: {}
    });

    // $scope.modalInstance.result.then(function (selectedItem) {
    //   $scope.selected = selectedItem;
    // }, function () {
    //   console.log('Modal dismissed at: ' + new Date());
    // });
  };

}];

var ModalInstanceCtrl = function ($scope, GlobalDataSharing, $modalInstance) {
  $scope.upload_file_info = GlobalDataSharing.upload_file_info;
  // $scope.uploading_complete = $scope.upload_file_info.uploading_progress==100 && true || false;
  // $scope.processing_image =  function () {
  //   type =
  //   url = '/static/img/wait-' + type + '.gif';
  //   return url
  // }
  // $scope.ok = function () {
  //   $modalInstance.close($scope.selected.item);
  // };

  // $scope.cancel = function () {
  //   $modalInstance.dismiss('cancel');
  // };
};
