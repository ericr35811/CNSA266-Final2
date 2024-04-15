var socketio = io();
var maxPoints = 10;
var intv;

function CreateChart(canvasId, label, min, max) {
    const ctx = $(canvasId);
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            //labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
            labels: Array.from(Array(maxPoints), () => ""),
            datasets: [{
                label: label,
                data: Array.from(Array(maxPoints), () => 0),
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    min: min,
                    max: max
                }
            }
        }
    });

    return chart;
}

function navCard(path) {
    $('#Content').load(path)
}

function setIntv() {
    // get the value from the txtInterval control
    var num = $("#txtInterval").val();
    // if value is an integer:
    num = parseInt(num)
    if (!isNaN(num)) {
    //     clearInterval(intv);
    //     intv = setInterval(updateCpu, num);

        socketio.emit('setInterval', num)
    }
}

function setMaxPoints(chart) {
    // fill chart with blank data
    var num = $("#txtMaxPoints").val();
    // if value is an integer:
    num = parseInt(num)
    if (!isNaN(num)) {
        maxPoints = num;

    }
}

socketio.on('sendcpu', (data) => {
    console.log(data);

    // parse data
    //var d = data.split('|');
    //var t = d[0];
    //var y = Number.parseFloat(d[1]);

    var t = data.elapsed;
    var y = data.percent;

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

})

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
