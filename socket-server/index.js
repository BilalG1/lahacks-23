const http = require('http').createServer();
const fs = require("fs");

const io = require('socket.io')(http, {
  cors: { origin: "*" }
});

io.on('connection', (socket) => {
  console.log('a user connected');

  // Update all users when a new user edits text
  socket.on('editText', (message) => {
    socket.broadcast.emit('editText', message);
  });

  // Save file when any user updates
  socket.on('updateFile', (text) => {
    const fileStream = fs.createWriteStream("./temp.txt");
    fileStream.write(text);
  });
});

http.listen(8080, () => console.log('listening on http://localhost:8080'));
