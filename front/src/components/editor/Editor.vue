<template>
  <div class="common-layout">
    <el-container>
      <el-header>
          <div class="flex flex-wrap items-center">
            <el-dropdown>
              <el-button type="primary"> File </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>
                    <label for="folder"> Open Folder </label>
                    <input type="file" id="folder" @change="handleOpenFolder" hidden webkitdirectory>
                  </el-dropdown-item>
                  <el-dropdown-item>
                    <label for="file"> Open File </label>
                    <input type="file" id="file" @change="handleOpenFile" hidden >
                  </el-dropdown-item>
                  <el-dropdown-item>Action 3</el-dropdown-item>
                  <el-dropdown-item>Action 4</el-dropdown-item>
                  <el-dropdown-item>Action 5</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          <el-button type="primary" @click="handleCompile"> Compile </el-button>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-tree id="fileTreeView" :data="fileTree" :props="defaultProps" @node-click="handleNodeClick" />
        </el-aside>
        <el-main>
          <div id="editor" style="width: 100vw; height: 100vh" class="pt-4" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref} from "vue";
import loader from "@monaco-editor/loader";
import 'element-plus/theme-chalk/dark/css-vars.css'
import _ from 'lodash'
const code = ref('')
const activeFile = ref('')
const editorRef = ref(null)
let editor;
const handleNodeClick = (data: Tree) => {
  activeFile.value = data.label
  editor.setValue(fileList.value[data.label].fileContent)
}
interface Tree {
  label: string
  children?: Tree[]
}
interface Item {
  filename: string,
  filePath: string,
  fileContent: string | ArrayBuffer | null,
  parent: string
}
onMounted(() => {
  loader.init().then((monaco) => {
    const editorOptions = {
      language: "typescript",
      // minimap: { enabled: false },
      theme: 'vs-dark'
    }
    editor = monaco.editor.create(document.getElementById("editor")!,   editorOptions);
    editor.onDidChangeModelContent(() => {
      // Update the content of the active file in the fileContent object
      fileList.value[activeFile.value].fileContent = editor.getValue();
    });
  });
})

const fileList = ref({});
const fileTree = ref<Tree[]>([]);

function addToFileList(file, parent){

  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result;
      const item = {
        filePath: file.webkitRelativePath,
        fileContent: text,
        parent: parent
      };
      fileList.value[file.name] = item;
      resolve('resolved')
    };
    reader.readAsText(file);
  })
}

function buildTree(filenames) {
  const root = { type: "directory", label: ".", children:[]};

  for (const filename of filenames) {
    const parts = filename.split("/");
    let currentNode: any = root;

    for (let i = 1; i < parts.length; i++) {
      const nodeName = parts[i];
      let node: any = currentNode.children?.find((n) => n.label === nodeName);

      if (!node) {
        console.log(nodeName)
        node = { type: "directory", label: nodeName, content: fileList.value[nodeName].fileContent};
        if (!currentNode.children) {
          currentNode.children = [];
        }
        currentNode.children.push(node);
      }

      currentNode = node;
    }

    if (currentNode.type === "directory") {
      continue;
    }

    const fileNode = { label: currentNode.label };
    currentNode = currentNode.children ?? currentNode;
    currentNode.children.push(fileNode);
  }

  return root;
}

const handleOpenFolder = async(event) => {
  const files = event.target.files;
  const filePaths = <string[]>[];

  for (const file of files) {
    if (!file.isDirectory) {
      const folders = file.webkitRelativePath.split('\/')
      const parent = folders.length > 1 ? folders[folders.length-2] : ''
      filePaths.push(file.webkitRelativePath);
      await addToFileList(file, parent)
    }
  }
  fileTree.value.push(buildTree(filePaths));
}
const handleOpenFile = async(event) => {
  const file = event.target.files[0];
  await addToFileList(file, parent)
  fileTree.value.push({
    label: file.name,
    children: []
  });
}
const defaultProps = {
    children: 'children',
    label: 'label',
}
const handleCompile = async() => {
  const obj = {
    "label": ".",
    "children": fileTree.value
  }
  console.log(JSON.stringify(obj, null, 2));
}
</script>

<style scoped>
a {
  color: #42b983;
}

.common-layout {
  padding:20px;
}
</style>
