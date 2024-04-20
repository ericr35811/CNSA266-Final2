var socketio = io();
var sock;
var maxPoints = 20;

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

    // fill the datasets on creation
    clearChart(chart);

    return chart;
}

// function to zero out a Chart.js chart
function clearChart(chart) {
    chart.data.labels = Array.from(Array(maxPoints), () => "");
    chart.data.datasets[0].data = Array.from(Array(maxPoints), () => 0);
    chart.update('none');
}

// load a new card onto the page
function navCard(path) {
    $('#Content').load(path)
}

// text box validation function
function checkTxt(ctlId, type, cb_success, cb_fail) {
    //if (!cb_success) cb_success = (num) => {console.log(ctlId + ': ' + num)}
    // default function to execute if validation fails
    if (!cb_fail) cb_fail = () => {console.log(ctlId + ': must be an int')}

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
    else cb_fail();
}

// push new values onto a Chart.js chart
function updateChart(chart, val, time) {
    // get linechart axes
    var xAxis = chart.data.labels;
    var yAxis = chart.data.datasets[0].data;

    // add new data to chart
    xAxis.unshift(time);
    yAxis.unshift(val);

    // limit chart length
    if (xAxis.length >= maxPoints)
        chart.data.labels = xAxis.slice(0, maxPoints);

    if (xAxis.length >= maxPoints)
        chart.data.datasets[0].data = yAxis.slice(0, maxPoints);

    // update the canvas with no animation
    chart.update('none');
}