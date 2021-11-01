 function incrementDate(date_str, incrementor) {
             var parts = date_str.split("-");
             var dt = new Date(
                 parseInt(parts[0], 10),      // year
                 parseInt(parts[1], 10) - 1,  // month (starts with 0)
                 parseInt(parts[2], 10)       // date
             );
             dt.setTime(dt.getTime() + incrementor * 86400000);
             parts[0] = "" + dt.getFullYear();
             parts[1] = "" + (dt.getMonth() + 1);
             if (parts[1].length < 2) {
                 parts[1] = "0" + parts[1];
             }
             parts[2] = "" + dt.getDate();
             if (parts[2].length < 2) {
                 parts[2] = "0" + parts[2];
             }
             return parts.join("-");
         }

         function datediff(first, second) {
             // Take the difference between the dates and divide by milliseconds per day.
             // Round to nearest whole number to deal with DST.
             return Math.round((second - first) / (1000 * 60 * 60 * 24));
         }
          function getDate(elem,myArr) { 
              var iterable2 = elem.getAttribute("date_attr")+'';
              let date = iterable2.split(",");

              console.log(myArr)
              let qt = myArr
              console.log(qt[0])
              console.log(qt[3])
              a = [];
              var i = 0;
              //take first and last date from addta
              const startDate  = date[date.length - 1];
              var endDate    = date[0];
              const diffInMs   = new Date(endDate) - new Date(startDate)
              const diffInDays = diffInMs / (1000 * 60 * 60 * 24);
              var n = date.includes(endDate);
              var index = 0;
              for (i=0;i<diffInDays;i++) {
                  var n = date.includes(endDate);
                  if(n===true) {
                    //check_date_is_available = incrementDate(iterable[i], -1);
                    index = date.indexOf(endDate)
                    a.push({x: new Date(endDate), y: qt[index]});

                  }else{
                      a.push({x: new Date(endDate), y: 0});
                  }
                  endDate = incrementDate(endDate, -1);

              }

              var chart = new CanvasJS.Chart("chartContainer", {
                  animationEnabled: true,
                  zoomEnabled: true,
                  theme: "dark2",
                  title: {
                      text: "Selling day by day"
                  },
                  data: [{
                      type: "line",
                      xValueFormatString: "",
                      showInLegend: true,
                      name: "Log Scale",

                      dataPoints: a
                  }]
              });
              $('#chartModal').on('shown.bs.modal', function () {
                chart.render();
              });

          }