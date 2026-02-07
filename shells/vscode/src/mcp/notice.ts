import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

import { CAP_DIR_NAME } from "../constants";

const MCP_NOTICE_KEY = "cap.mcpNoticeShown";

export function registerMcpNotice(context: vscode.ExtensionContext): vscode.Disposable {
  const watcher = vscode.workspace.createFileSystemWatcher("**/.cap", false, true, true);
  watcher.onDidCreate(() => showNotice(context));

  const hasCapAlready = (vscode.workspace.workspaceFolders ?? []).some((f) =>
    fs.existsSync(path.join(f.uri.fsPath, CAP_DIR_NAME))
  );
  if (hasCapAlready) {
    showNotice(context);
  }

  return watcher;
}

function showNotice(context: vscode.ExtensionContext): void {
  if (context.globalState.get<boolean>(MCP_NOTICE_KEY)) {
    return;
  }

  vscode.window
    .showInformationMessage(
      "CAP MCP server registered. Enable it in Copilot Chat Configure Tools settings.",
      "Open Chat",
      "Don't Show Again"
    )
    .then((choice) => {
      if (choice === "Open Chat") {
        vscode.commands.executeCommand("workbench.panel.chat.view.copilot.focus");
      }
      if (choice === "Don't Show Again") {
        context.globalState.update(MCP_NOTICE_KEY, true);
      }
    });
}
