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
        charts[i].data.labels = Array(maxPoints).fill('');
        charts[i].data.datasets[0].data = Array(maxPoints).fill(null);
        charts[i].update('none');
    }
}


function resizeChart(chart, length, data) {
    var ndata;

    // pad the list out to [length] if there are not at least [length] items in data
    if (data.length <= length)
        ndata = data.concat(
            Array(length - data.length)
            .fill({val: null, elapsed: ''})
        );
    // otherwise get the most recent [length] items from the end of the data list
    else
        ndata = data.slice(data.length - length, data.length);


    // set the values for each axis from the data
    chart.data.labels = ndata.map(x => x.elapsed);
    chart.data.datasets[0].data = ndata.map(x => x.val);

    chart.update('none');
}

// push new values onto a Chart.js chart
function updateChart(chart, val, time, side) {
    // add new data to chart
    //chart.data.labels.unshift(time);
    //chart.data.datasets[0].data.unshift(val);

    var x = chart.data.labels;
    var y = chart.data.datasets[0].data;

    i = y.indexOf(null);
    if (i > -1) {
        x[i] = time;
        y[i] = val;

        // chart.data.labels.pop();
        // chart.data.labels.unshift(time);
        // chart.data.datasets[0].data.pop();
        // chart.data.datasets[0].data.unshift(val);
    }
    else {
        x.shift();
        x.push(time);
        y.shift();
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
        console.log(ctlId + ': must be an int');
        cb_fail();
    }
}


