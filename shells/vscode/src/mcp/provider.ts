/**
 * Register cap serve as an MCP server for each workspace folder with .cap/.
 */

import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

import { CAP_DIR_NAME, MCP_PROVIDER_ID } from "../constants";
import type { Environment } from "../setup/environment";
import type { FileSystemWatcher } from "../utils/fileSystemWatcher";

export function registerMcpProvider(
  context: vscode.ExtensionContext,
  env: Environment,
  capWatcher: FileSystemWatcher
): vscode.Disposable {
  const onDidChange = new vscode.EventEmitter<void>();

  const provider: vscode.McpServerDefinitionProvider = {
    onDidChangeMcpServerDefinitions: onDidChange.event,

    provideMcpServerDefinitions(
      _token: vscode.CancellationToken
    ): vscode.McpServerDefinition[] {
      return (vscode.workspace.workspaceFolders ?? [])
        .filter((f) => fs.existsSync(path.join(f.uri.fsPath, CAP_DIR_NAME)))
        .map(
          (folder) =>
            new vscode.McpStdioServerDefinition(
              `CAP: ${folder.name}`,
              env.capPath,
              ["serve", folder.uri.fsPath]
            )
        );
    },
  };

  const registration = vscode.lm.registerMcpServerDefinitionProvider(
    MCP_PROVIDER_ID,
    provider
  );

  const createSub = capWatcher.onDidCreate(() => onDidChange.fire());
  const deleteSub = capWatcher.onDidDelete(() => onDidChange.fire());

  const foldersWatcher = vscode.workspace.onDidChangeWorkspaceFolders(() =>
    onDidChange.fire()
  );

  return vscode.Disposable.from(registration, foldersWatcher, createSub, deleteSub, onDidChange);
}
