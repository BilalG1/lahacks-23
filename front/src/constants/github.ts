interface Tree {
  label: string
  children?: Tree[]
}

export const parseRepo = async (owner: string, repo: string) => {
  const fileList = {}
  const fileTree: Tree[] = []
  const filePaths: string[] = []
  const promises: Promise<any>[] = []

  const url = `https://api.github.com/repos/${owner}/${repo}/git/trees/main?recursive=1`
  const { tree } = await fetch(url).then(res => res.json())

  for (const file of tree) {
    const folders: string[] = file.path.split('\/')
    const parent = folders.length > 1 ? folders[folders.length-2] : ''
    filePaths.push(file.path)
    promises.push(fetch(file.url)
      .then(res => res.json())
      .then(data => {
        let content;
        try {
          content = atob(data.content)
        } catch {
          content = ''
        }
        const item = {
          filePath: file.path,
          fileContent: content,
          parent: parent
        };
        fileList[file.name] = item;
      }))
  }
  await Promise.all(promises)
  fileTree.push(buildTree(filePaths, fileList))
  return { fileList, fileTree }
}

function buildTree(filenames: string[], fileList: any) {
  const root = { type: "directory", label: ".", children:[]};
  for (const filename of filenames) {
    const parts = filename.split("/");
    let currentNode: any = root;
    for (let i = 1; i < parts.length; i++) {
      const nodeName = parts[i];
      let node: any = currentNode.children?.find((n) => n.label === nodeName);
      if (!node) {
        node = { type: "directory", label: nodeName, content: fileList[nodeName]?.fileContent};
        if (!currentNode.children) {
          currentNode.children = [];
        }
        currentNode.children.push(node);
      }
      currentNode = node;
    }
    if (currentNode.type === "directory")
      continue;
    const fileNode = { label: currentNode.label };
    currentNode = currentNode.children ?? currentNode;
    currentNode.children.push(fileNode);
  }
  return root;
}

