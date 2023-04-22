const http = require('http').createServer();

const io = require('socket.io')(http, {
  cors: { origin: "*" }
});

io.on('connection', (socket) => {
  console.log('a user connected');

  socket.on('editText', (message) => {
    console.log(message);
    socket.broadcast.emit('editText', message);
  });
});

http.listen(8080, () => console.log('listening on http://localhost:8080'));
