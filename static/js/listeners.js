socketio.on('connect', () => {
    console.log('socketio server connected')
    $('#rPiConnection').html('🟢')
});

socketio.on('disconnect', () => {
    console.log('socketio server disconnected')
    $('#rPiConnection').html('🔴')
})

socketio.on('car_connect_status', (status) => {
    if (status === true) {
        $('#carConnectStatus').html('🟢')
    }
    else {
        $('#carConnectStatus').html('🔴')
    }

    return true;
})

// handle event when the server sends new data
// push the new data onto each chart
socketio.on('send_data', (data) => {
    console.log('send_data')
    for (var sensor of data) {
        if (dataLog.length > maxData) {
            // discard old data if history limit is reached
            // all history is still logged on the server side
            dataLog[sensor.pid].shift();
        }

        dataLog[sensor.pid].push(sensor);

        updateChart(charts[sensor.pid], sensor.val, sensor.elapsed);

        $('#val_' + sensor.pid).html(sensor.val);
    }
});