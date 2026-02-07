/**
 * Detect missing .cap/ directories and offer to run cap init.
 */

import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

import { CAP_DIR_NAME } from "../constants";
import type { Environment } from "../setup/environment";
import { pickWorkspaceFolder } from "../utils/workspace";

export async function promptInitForWorkspaces(env: Environment): Promise<void> {
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
  env: Environment
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

function runCapInit(env: Environment, workspacePath: string, force: boolean): void {
  const args = ["init"];
  if (force) {
    args.push("--force");
  }
  args.push(workspacePath);

  const task = new vscode.Task(
    { type: "cap", task: "init" },
    vscode.TaskScope.Workspace,
    "CAP Init",
    "cap",
    new vscode.ShellExecution(env.capPath, args, { cwd: workspacePath })
  );
  task.presentationOptions = { reveal: vscode.TaskRevealKind.Always };
  vscode.tasks.executeTask(task);
}
