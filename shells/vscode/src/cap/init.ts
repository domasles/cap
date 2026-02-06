/**
 * Detect missing .cap/ directories and offer to run cap init.
 */

import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

import { CAP_DIR_NAME } from "../constants";
import type { CapEnvironment } from "../setup/environment";

export async function promptInitForWorkspaces(env: CapEnvironment): Promise<void> {
  const autoInit = vscode.workspace.getConfiguration("cap").get<boolean>("autoInit", true);
  if (!autoInit) {
    return;
  }

  for (const folder of vscode.workspace.workspaceFolders ?? []) {
    const capDir = path.join(folder.uri.fsPath, CAP_DIR_NAME);
    if (!fs.existsSync(capDir)) {
      const choice = await vscode.window.showInformationMessage(
        `Workspace "${folder.name}" has no .cap/ configuration. Set up now?`,
        "Yes",
        "Not Now"
      );
      if (choice === "Yes") {
        runCapInit(env, folder.uri.fsPath, false);
      }
    }
  }
}

export function registerInitCommands(
  context: vscode.ExtensionContext,
  env: CapEnvironment
): void {
  context.subscriptions.push(
    vscode.commands.registerCommand("cap.init", async () => {
      const folder = await pickWorkspaceFolder();
      if (folder) {
        runCapInit(env, folder, false);
      }
    }),
    vscode.commands.registerCommand("cap.initForce", async () => {
      const folder = await pickWorkspaceFolder();
      if (folder) {
        runCapInit(env, folder, true);
      }
    })
  );
}

function runCapInit(env: CapEnvironment, workspacePath: string, force: boolean): void {
  const args = ["init"];
  if (force) {
    args.push("--force");
  }
  args.push(workspacePath);

  const terminal = vscode.window.createTerminal({
    name: "CAP Init",
    cwd: workspacePath,
  });

  const quoted = args.map((a) => `"${a}"`).join(" ");
  const cmd =
    process.platform === "win32"
      ? `& "${env.capPath}" ${quoted}`
      : `"${env.capPath}" ${quoted}`;

  terminal.sendText(cmd);
  terminal.show();
}

async function pickWorkspaceFolder(): Promise<string | undefined> {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders || folders.length === 0) {
    vscode.window.showWarningMessage("CAP: No workspace folder is open.");
    return undefined;
  }
  if (folders.length === 1) {
    return folders[0].uri.fsPath;
  }
  const picked = await vscode.window.showWorkspaceFolderPick({
    placeHolder: "Select workspace folder",
  });
  return picked?.uri.fsPath;
}
