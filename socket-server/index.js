const http = require('http').createServer();

const io = require('socket.io')(http, {
  cors: { origin: "*" }
});

io.on('connection', (socket) => {
  console.log('a user connected');

  socket.on('updateFile', (update) => {
    console.log(update);
    socket.broadcast.emit('updateFile', update);
  });
});

http.listen(8080, () => console.log('listening on http://localhost:8080'));
