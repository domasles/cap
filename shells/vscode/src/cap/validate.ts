/**
 * Validate .cap/ files — command palette action + live file watcher with diagnostics.
 */

import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

import { CAP_DIR_NAME } from "../constants";
import type { CapEnvironment } from "../setup/environment";
import { runValidateJson, type ValidationFileResult } from "./runner";
import { pickWorkspaceFolder } from "../utils/workspace";

export function registerValidation(
  context: vscode.ExtensionContext,
  env: CapEnvironment
): vscode.Disposable {
  const diagnostics = vscode.languages.createDiagnosticCollection("cap");

  // Command: cap.validate
  context.subscriptions.push(
    vscode.commands.registerCommand("cap.validate", async () => {
      const folder = await pickWorkspaceFolder();
      if (!folder) {
        return;
      }
      const results = await runValidateJson(env, folder);
      updateDiagnostics(folder, results, diagnostics);

      const errors = results.filter((r) => !r.valid);
      if (errors.length > 0) {
        vscode.window.showWarningMessage(
          `CAP: ${errors.length} file(s) invalid. See Problems panel.`
        );
      } else if (results.length > 0) {
        vscode.window.showInformationMessage(
          `CAP: All ${results.length} configuration file(s) valid.`
        );
      } else {
        vscode.window.showInformationMessage(
          "CAP: No configuration files found. Run 'CAP: Initialize Configuration' first."
        );
      }
    })
  );

  // File watcher: validate on .cap/*.yaml changes
  const watcher = vscode.workspace.createFileSystemWatcher("**/.cap/*.yaml", false, false, false);
  const timers = new Map<string, ReturnType<typeof setTimeout>>();

  const scheduleValidation = (uri: vscode.Uri) => {
    const folder = vscode.workspace.getWorkspaceFolder(uri);
    if (!folder) {
      return;
    }
    const key = folder.uri.fsPath;
    const existing = timers.get(key);
    if (existing) {
      clearTimeout(existing);
    }
    timers.set(
      key,
      setTimeout(async () => {
        timers.delete(key);
        const results = await runValidateJson(env, folder.uri.fsPath);
        updateDiagnostics(folder.uri.fsPath, results, diagnostics);
      }, 500)
    );
  };

  watcher.onDidChange(scheduleValidation);
  watcher.onDidCreate(scheduleValidation);
  watcher.onDidDelete(scheduleValidation);

  // Initial validation for workspaces that already have .cap/
  for (const folder of vscode.workspace.workspaceFolders ?? []) {
    if (fs.existsSync(path.join(folder.uri.fsPath, CAP_DIR_NAME))) {
      runValidateJson(env, folder.uri.fsPath).then((results) =>
        updateDiagnostics(folder.uri.fsPath, results, diagnostics)
      );
    }
  }

  return vscode.Disposable.from(watcher, diagnostics, {
    dispose: () => {
      for (const timer of timers.values()) {
        clearTimeout(timer);
      }
      timers.clear();
    },
  });
}

function updateDiagnostics(
  workspacePath: string,
  results: ValidationFileResult[],
  diagnostics: vscode.DiagnosticCollection
): void {
  const capDir = path.join(workspacePath, CAP_DIR_NAME);

  // Clear previous diagnostics for this workspace's .cap/ files
  diagnostics.forEach((uri) => {
    if (uri.fsPath.startsWith(capDir)) {
      diagnostics.delete(uri);
    }
  });

  for (const result of results) {
    const fileUri = vscode.Uri.file(path.join(capDir, result.file));
    if (!result.valid && result.errors.length > 0) {
      const items = result.errors.map((msg) => {
        const d = new vscode.Diagnostic(
          new vscode.Range(0, 0, 0, 0),
          msg,
          vscode.DiagnosticSeverity.Error
        );
        d.source = "CAP";
        return d;
      });
      diagnostics.set(fileUri, items);
    } else {
      diagnostics.set(fileUri, []);
    }
  }
}
