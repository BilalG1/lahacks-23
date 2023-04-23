<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <div class="flex flex-wrap items-center">
            <el-menu
              class="el-menu-demo"
              mode="horizontal"
              :ellipsis="false"
              @select="handleSelect"
            >
              <el-sub-menu index="1"> 
                <template #title> File </template>
                  <el-menu-item>
                    <label for="folder"> Open Folder </label>
                    <input type="file" id="folder" @change="handleOpenFolder" hidden webkitdirectory>
                  </el-menu-item>
                  <el-menu-item>
                    <label for="file"> Open File </label>
                    <input type="file" id="file" @change="handleOpenFile" hidden >
                  </el-menu-item>
              </el-sub-menu>
              <el-menu-item index="2">
                <template #title> 
                  <span v-if="!showDelete" @click="showDelete=true" > Delete </span>
                  <span v-else @click="showDelete=false"> Done </span>
                 </template>
              </el-menu-item>
              <el-menu-item index="3">
                <template #title> 
                  <span @click="handleCompile" > Compile </span>
                 </template>
              </el-menu-item>
            </el-menu>
            <el-autocomplete
                v-model="language"
                style="padding-left: 50px"
                :fetch-suggestions="querySearch"
                clearable
                class="inline-input w-50"
                placeholder="Input Language"
                @select="handleSelect"
              />
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-tree 
            id="fileTreeView" 
            draggable
            default-expand-all
            :data="fileTree" 
            :props="defaultProps" 
            @node-click="handleNodeClick" 
            @node-drag-start="handleDragStart"
            @node-drag-enter="handleDragEnter"
            @node-drag-leave="handleDragLeave"
            @node-drag-over="handleDragOver"
            @node-drag-end="handleDragEnd"
            @node-drop="handleDrop"
          >
          <template #default="{ node, data }">
            <span class="custom-tree-node">
              <span>{{ node.label }}</span>
              <span>
                <a v-show="showDelete" style="margin-right: 10%;" @click="remove(node, data)"> Delete </a>
              </span>
            </span>
          </template>
          </el-tree>
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
import { config } from "../../constants/config";
import loader from "@monaco-editor/loader";
import 'element-plus/theme-chalk/dark/css-vars.css'
import _ from 'lodash'
import { useQuasar } from "quasar";

const $q = useQuasar()
const code = ref('')
const activeFile = ref('')
const editorRef = ref(null)
const showDelete = ref(false)
let editor;
const handleNodeClick = (data: Tree) => {
  activeFile.value = data.label
  if (fileList.value[data.label].fileContent){
    editor.setValue(fileList.value[data.label].fileContent)
  }
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
      language: language.value,
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
const language = ref('');
const languages = ref([  {'value': 'javascript'},  {'value': 'typescript'},  {'value': 'css'},  {'value': 'html'},  {'value': 'json'},  {'value': 'markdown'},  {'value': 'xml'},  {'value': 'yaml'},  {'value': 'python'},  {'value': 'java'},  {'value': 'csharp'},  {'value': 'cpp'},  {'value': 'ruby'},  {'value': 'php'},  {'value': 'go'},  {'value': 'rust'},  {'value': 'swift'},  {'value': 'kotlin'},  {'value': 'sql'}]);

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
        node = { type: "directory", label: nodeName, content: fileList.value[nodeName]?.fileContent};
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

  const uid = localStorage.id
  if (!uid)
    return $q.notify('Out of users, reset')
  const tech_stack = 'vue-flask'
  const url = `${config.apiUrl}/upload-files/${uid}?tech_stack=${tech_stack}` 
  const headers = { 'content-type': 'application/json' }
  const method = 'POST'
  const body = JSON.stringify(obj)
  fetch(url, { method, headers, body })
  // console.log(JSON.stringify(obj, null, 2));
}

const handleDragStart = (node: Node, ev: DragEvents) => {
  console.log('drag start', node)
}

const handleDragEnter = (
  draggingNode: Node,
  dropNode: Node,
  ev: DragEvents
) => {
  console.log('tree drag enter:', dropNode.label)
}
const handleDragLeave = (
  draggingNode: Node,
  dropNode: Node,
  ev: DragEvents
) => {
  console.log('tree drag leave:', dropNode.label)
}
const handleDragOver = (draggingNode: Node, dropNode: Node, ev: DragEvents) => {
  console.log('tree drag over:', dropNode.label)
}
const handleDragEnd = (
  draggingNode: Node,
  dropNode: Node,
  dropType: NodeDropType,
  ev: DragEvents
) => {
  console.log('tree drag end:', dropNode && dropNode.label, dropType)
}
const handleDrop = (
  draggingNode: Node,
  dropNode: Node,
  dropType: NodeDropType,
  ev: DragEvents
) => {
  console.log('tree drop:', dropNode.label, dropType)
  console.log(JSON.stringify(fileTree.value, null, 2))
}

const remove = (node: Node, data: Tree) => {
  const parent = node.parent
  const children: Tree[] = parent.data.children || parent.data
  console.log(children, data)

  const index = children.findIndex((d) => d.label === data.label)
  children.splice(index, 1)
  console.log(fileList.value[data.label])
  delete fileList.value[data.label];
}

const createFilter = (queryString: string) => {
  return (language: {}) => {
    return (
      language.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0
    )
  }
}

const querySearch = (queryString: string, cb: any) => {
  const results = queryString
    ? languages.value.filter(createFilter(queryString))
    : languages.value
  cb(results)
}

const handleSelect = (item: string) => {
  console.log(item)
  language.value = item.value;
  const model = editor.getModel();
  monaco.editor.setModelLanguage(model, language.value);
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
