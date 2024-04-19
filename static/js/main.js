var socketio = io();
var sock;
var maxPoints = 20;

function CreateChart(ctx, label, min, max) {
    //const ctx = document.getElementById(canvasId)
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            //labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
            labels: [],
            datasets: [{
                //label: label,
                data: [],
                borderWidth: 3,
                pointStyle: false
            }]
        },
        options: {
            scales: {
                x: {
                  ticks: {
                      maxTicksLimit: maxPoints / 4
                  }
                },
                y: {
                    beginAtZero: true,
                    min: min,
                    max: max
                }
            },
            plugins: {
                legend: {
                    display: false
                },
            },
        },

        maxPoints: length
    });

    // fill the datasets on creation
    clearChart(chart);

    return chart;
}

function clearChart(chart) {
    chart.data.labels = Array.from(Array(maxPoints), () => "");
    chart.data.datasets[0].data = Array.from(Array(maxPoints), () => 0);
    chart.update('none');
}

function navCard(path) {
    $('#Content').load(path)
}


function checkTxt(ctlId, type, cb_success, cb_fail) {
    if (!cb_success) cb_success = (num) => {console.log(ctlId + ': ' + num)}
    if (!cb_fail) cb_fail = () => {console.log(ctlId + ': must be an int')}
    // get the value from the txtInterval control
    var num = $(ctlId).val();

    // if value is an integer:
    if (type === 'int') {
        num = parseInt(num)
    }
    else if (type === 'float') {
        num = parseFloat(num)
    }

    if (!isNaN(num)) {
        console.log(ctlId + ': ' + num);
        cb_success(num);
    }
    else cb_fail();
}

function updateChart(chart, val, time) {
    // get  linechart axes
    var xAxis = chart.data.labels;
    var yAxis = chart.data.datasets[0].data;

    // add new data to chart
//    xAxis.push(time);
 //   yAxis.push(val);
    xAxis.unshift(time);
    yAxis.unshift(val);

    // limit chart data points
    if (xAxis.length >= maxPoints)
//        chart.data.labels = xAxis.slice(xAxis.length - maxPoints, xAxis.length);
        chart.data.labels = xAxis.slice(0, maxPoints);

    if (xAxis.length >= maxPoints)
//        chart.data.datasets[0].data = yAxis.slice(yAxis.length - maxPoints, yAxis.length);
        chart.data.datasets[0].data = yAxis.slice(0, maxPoints);

    // update with no animation
    chart.update('none');
}

    /*$.post(
        // send POST request to localhost/cpu with no data
        window.location.href,
        // callback function. "data" is returned by the server
        function (data, status) {
            // parse data
            var d = data.split('|');
            var t = d[0];
            var y = Number.parseFloat(d[1]);

            // get  linechart axes
            var xAxis = lineChart.data.labels;
            var yAxis = lineChart.data.datasets[0].data;

            // add new data to chart
            xAxis.push(t);
            yAxis.push(y);

            // limit chart to 20 data points?
            if (xAxis.length >= maxPoints)
                lineChart.data.labels = xAxis.slice(xAxis.length - maxPoints, xAxis.length);
            if (xAxis.length >= maxPoints)
                lineChart.data.datasets[0].data = yAxis.slice(yAxis.length - maxPoints, yAxis.length);

            // update with no animation
            lineChart.update('none');
        }
    );
}*/
