var socketio = io();
var maxPoints = 20;
var dataLog = [];

// function to initialize a Chart.js chart, taking an HTML canvas as input
function CreateChart(ctx, min, max) {
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
            // todo: find a way to disable resize animation
            animation: false,
            transitions: false,
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
    return chart;
}

// function to zero out a Chart.js chart
function clearCharts(charts) {
    for (i in charts) {
        charts[i].data.labels = Array.from(Array(maxPoints), () => "");
        charts[i].data.datasets[0].data = Array.from(Array(maxPoints), () => '');
        charts[i].update('none');
    }
}

function resizeCharts(charts, length) {
    for (i in charts) {
        if (length > maxPoints) {
            charts[i].data.labels = charts[i].data.labels.concat(                       Array.from(Array(length - maxPoints), () => ""));
            charts[i].data.datasets[0].data = charts[i].data.datasets[0].data.concat(   Array.from(Array(length - maxPoints), () => 0));
        }

        constrainChart(charts[i], length);
        charts[i].update('none');
    }

    maxPoints = length;
}

// todo: make blank chart data not zero
function resizeChart(chart, length, data) {
    console.log(data);
    console.log(data.map(x => x.elapsed).slice(data.length - length, data.length));

    chart.data.labels = data.map(x => x.elapsed).slice(data.length - length, data.length);
    chart.data.datasets[0].data = data.map(x => x.val).slice(data.length - length, data.length);

    if (chart.data.labels.length < length) {
        chart.data.labels = Array(length - chart.data.labels.length).fill('').concat(chart.data.labels);
    }
    if (chart.data.datasets[0].data.length < length) {
        chart.data.datasets[0].data = Array(length - chart.data.datasets[0].data.length).fill('').concat(chart.data.datasets[0].data);
    }

    chart.update('none');
}


function constrainChart(chart, length) {
     // limit chart length
    //chart.data.labels = chart.data.labels.slice(0, length);
    //chart.data.datasets[0].data = chart.data.datasets[0].data.slice(0, length);

    chart.data.labels = chart.data.labels.slice(
        chart.data.labels.length - length,
        length
    );
    chart.data.datasets[0].data = chart.data.datasets[0].data.slice(
        chart.data.datasets[0].data.length - length,
        length
    );
}

// push new values onto a Chart.js chart
function updateChart(chart, val, time, limit) {
    // add new data to chart
    //chart.data.labels.unshift(time);
    //chart.data.datasets[0].data.unshift(val);

    if (chart.data.labels.length < limit) {
        chart.data.labels.pop();
        chart.data.labels.unshift(time);
        chart.data.datasets[0].data.pop();
        chart.data.datasets[0].data.unshift(val);
    }
    else {
        chart.data.labels.shift();
        chart.data.labels.push(time);
        chart.data.datasets[0].data.shift();
        chart.data.datasets[0].data.push(val);
    }

    // update the canvas with no animation
    chart.update('none');
}

function newData(charts, dataLog, data) {
    dataLog.push(data);
    updateChart(
        charts[data.pid],
        data.val,
        data.elapsed
    );

    $('#val_' + sensor.pid).html(sensor.val);
}

// load a new card onto the page
function navCard(path) {
    $('#Content').load(path)
}

// text box validation function
function checkTxt(ctlId, type, cb_success, cb_fail) {
    // get the value from the txtInterval control
    var num = $(ctlId).val();

    // try to parse value
    if (type === 'int') {
        num = parseInt(num)
    }
    else if (type === 'float') {
        num = parseFloat(num)
    }

    // if the parse functions fail, they return NaN
    if (!isNaN(num)) {
        console.log(ctlId + ': ' + num);
        cb_success(num);
    }
    else {
        console.log(ctlId + ': must be an int');
        cb_fail();
    }
}


