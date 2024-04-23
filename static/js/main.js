var socketio = io();
var maxPoints = 20;
var dataLog = [];
var maxData = 4000;

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
            spanGaps: false,
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
        }
    });
    return chart;
}

// function to zero out a Chart.js chart
function clearCharts(charts) {
    for (i in charts) {
        charts[i].data.labels.fill('');
        charts[i].data.datasets[0].data.fill(null);
        charts[i].update('none');
    }
}

// adjust the length of a chart
function resizeChart(chart, length, dataLog) {
    var ndata;

    // pad the list out to [length] if there are not at least [length] items in data
    if (dataLog.length <= length)
        ndata = dataLog.concat(
            Array(length - dataLog.length)
            .fill({val: null, elapsed: ''})
        );
    // otherwise get the most recent [length] items from the end of the data list
    else
        ndata = dataLog.slice(dataLog.length - length, dataLog.length);

    // set the values for each axis from the data
    chart.data.labels = ndata.map(x => x.elapsed);
    chart.data.datasets[0].data = ndata.map(x => x.val);

    chart.update('none');
}

// push new values onto a Chart.js chart
function updateChart(chart, val, time) {
    // get references to chart axes
    var x = chart.data.labels;
    var y = chart.data.datasets[0].data;

    // look for the first (leftmost) null value in the chart (a blank data point)
    // if it is found, replace that null with the new value
    i = y.indexOf(null);
    if (i > -1) {
        x[i] = time;
        y[i] = val;
    }
    // if there are no blank data points, add the new values and scroll the graph to the left
    else {
        x.shift();
        y.shift();
        x.push(time);
        y.push(val);
    }

    // update the canvas with no animation
    chart.update('none');
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
        console.log(ctlId + ': invalid');
        cb_fail();
    }
}


