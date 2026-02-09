/**
 * Register cap serve as an MCP server for each workspace folder with .cap/.
 * Supports dispose/re-register for cross-window update coordination.
 */

import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

import { CAP_DIR_NAME, MCP_PROVIDER_ID } from "../constants";
import type { Environment } from "../setup/environment";
import type { FileSystemWatcher } from "../utils/fileSystemWatcher";

export interface McpProviderHandle {
  dispose: () => void;
  reregister: () => void;
}

export function registerMcpProvider(
  context: vscode.ExtensionContext,
  env: Environment,
  capWatcher: FileSystemWatcher
): McpProviderHandle {
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

  let registration: vscode.Disposable | undefined;

  function register(): void {
    if (registration) {
      return;
    }
    registration = vscode.lm.registerMcpServerDefinitionProvider(
      MCP_PROVIDER_ID,
      provider
    );
  }

  function unregister(): void {
    if (registration) {
      registration.dispose();
      registration = undefined;
    }
  }

  // Initial registration
  register();

  const createSub = capWatcher.onDidCreate(() => onDidChange.fire());
  const deleteSub = capWatcher.onDidDelete(() => onDidChange.fire());

  const foldersWatcher = vscode.workspace.onDidChangeWorkspaceFolders(() =>
    onDidChange.fire()
  );

  return {
    dispose: () => {
      unregister();
      foldersWatcher.dispose();
      createSub.dispose();
      deleteSub.dispose();
      onDidChange.dispose();
    },
    reregister: () => {
      register();
      onDidChange.fire();
    },
  };
}
