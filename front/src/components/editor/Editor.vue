<template>
  <div id="editor" style="width: 100vw; height: 100vh" class="pt-4" />
</template>

<script setup>
import { onMounted, ref } from "vue";
import loader from "@monaco-editor/loader";

const socket = io('ws://localhost:8080'); // socket-server port
let editor = null;
var isSocket = false // Avoid conflicts between editor change event and socket change event when broadcasting changes

// Update text from websocket message
function changeText(e) {
  editor.getModel().applyEdits(e.changes) // Apply edits to model
}

// handle incoming websocket messages
socket.on('editText', text => {
  isSocket = true
  changeText(text)
});

onMounted(() => {
  loader.init().then((monaco) => {
    const editorOptions = {
      language: "typescript",
      // minimap: { enabled: false },
      theme: 'vs-dark'
    }

    editor = monaco.editor.create(document.getElementById("editor"), editorOptions);

    // Client side text change event. 
    editor.onDidChangeModelContent(function (e) {
      // Send websocket message to editText
      if (isSocket === false) {
        socket.emit('editText', e)
      } else {
        isSocket = false
      }

      // Update file on server
      if (isSocket === false) {
        socket.emit('updateFile', editor.getModel().createSnapshot().read() ?? "")
      } else {
        isSocket = false
      }
    });
  });
});

</script>

<style scoped>
a {
  color: #42b983;
}
</style>
