<template>
  <div id="editor" style="width: 100vw; height: 100vh" class="pt-4" />
</template>

<script setup>
import { onMounted, ref} from "vue";
import loader from "@monaco-editor/loader";

const code = ref('')

const handleChange = () => {
  
}

onMounted(() => {
  loader.init().then((monaco) => {
    const editorOptions = {
      language: "typescript",
      // minimap: { enabled: false },
      theme: 'vs-dark'
    }

    monaco.editor.create(document.getElementById("editor"),   editorOptions);
  });
})

</script>

<style scoped>
a {
  color: #42b983;
}
</style>
