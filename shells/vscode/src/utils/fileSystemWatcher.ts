import * as vscode from "vscode";

export interface FileSystemWatcher extends vscode.Disposable {
  onDidCreate: vscode.Event<vscode.Uri>;
  onDidDelete: vscode.Event<vscode.Uri>;
}

export function createCapDirectoryWatcher(): FileSystemWatcher {
  const watcher = vscode.workspace.createFileSystemWatcher("**/.cap", false, true, false);

  return {
    onDidCreate: watcher.onDidCreate,
    onDidDelete: watcher.onDidDelete,
    dispose: () => watcher.dispose(),
  };
}
