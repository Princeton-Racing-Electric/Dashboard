// Initialize numbers to 0 before sensor data is picked up
window.onload = () => {
  [... document.querySelectorAll(".text-large")]
    .forEach(element => element.innerHTML = "0.0");
}


// Sets an interval to repeatedly query the update url of the server for
// the current sensor data
setInterval(function () {
  $.ajax({
    url: "/update",
    type: "POST",
    success: function (response) {
      console.log(response);
      $("#mph").html(Math.round(100*response["mph"])/100);
      $("#temperature").html(Math.round(100*response["temperature"])/100);
      $("#acceleration").html(Math.round(100*response["acceleration"])/100);
      $("#voltage").html(Math.round(100*response["voltage"])/100);
      $("#mileage").html(Math.round(100*response["mileage"])/100);
      $("#efficiency").html(Math.round(100*response["efficiency"])/100);
      $("#time").html(response["time"]);
    },
    error: function (error) {
      console.log(error);
    },
  });
}, 1000);
