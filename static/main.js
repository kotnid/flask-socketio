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

    socket.on('data_update' , function(msg){
        $('#log2').append('<br>' + $('<div/>').text(msg.date + ' - Data update' + ': ' + msg.name + ' views is at ' + msg.view + ' now~').html())
    });

    socket.on('data_search' , function(msg){
        if(msg.type == "0"){
            $('#search_log').empty();
            $('#search_log').append('<br>' + $('<div/>').text('search fail').html());
        }else{
            $('#search_log').empty();
            $('#search_log').append('<br>' + $('<div/>').text(msg.data).html());
        }
    });


    $('form#emit').submit(function(){
        socket.emit('client_event' , {data:$('#emit_data').val()});
        return false;
    });

    $('form#search').submit(function(){
        socket.emit('client_event_search' , {data:$('#search_name').val()});
        return false;
    });
})