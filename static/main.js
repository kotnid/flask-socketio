$(document).ready(function(){
    var url = 'http://127.0.0.1';
    var port = '5000';
    var socket = io.connect(url + ':' + port);

    socket.on('connect' , function(){
        socket.emit('connect_event' , {data : 'connect!'});
    });

    socket.on('server_response' , function(msg){
        $('#log').append('<br>' + $('<div/>').text('Received #' + ': ' + msg.data).html())
    });

    $('form#emit').submit(function(event){
        socket.emit('client_event' , {data:$('#emit_data').val()});
        return false;
    });
})