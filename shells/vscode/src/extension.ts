import * as vscode from "vscode";
import * as path from "path";

import { OUTPUT_CHANNEL_NAME, VENV_DIR_NAME } from "./constants";
import { setupEnvironment } from "./setup/environment";
import { checkForUpdate } from "./setup/updater";
import { checkCompatibility } from "./setup/compatibility";
import { watchUpdateLock, isUpdateLocked } from "./setup/updateLock";
import { createCapDirectoryWatcher } from "./utils/fileSystemWatcher";
import { registerMcpProvider } from "./mcp/provider";
import { registerMcpNotice } from "./mcp/notice";
import { registerInitCommands, promptInitForWorkspaces } from "./cap/init";
import { registerValidation } from "./cap/validate";

let output: vscode.OutputChannel;

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  output = vscode.window.createOutputChannel(OUTPUT_CHANNEL_NAME);
  context.subscriptions.push(output);

  const mode = context.extensionMode === vscode.ExtensionMode.Development ? "development" : "production";

  output.appendLine(`CAP activating (${mode})...`);

  const env = await setupEnvironment(context, output);

  if (!env) {
    output.appendLine("Setup failed - extension inactive.");
    return;
  }

  // Check for CLI updates first (blocking) — user may need the latest CLI for compat
  await checkForUpdate(context, env.capPath, output);

  // Check CLI and extension version compatibility (runs after any update)
  const compatible = await checkCompatibility(context, env, output);
  if (!compatible) {
    output.appendLine("CLI incompatible - extension inactive.");
    return;
  }

  const capWatcher = createCapDirectoryWatcher();
  context.subscriptions.push(capWatcher);

  const mcpProvider = registerMcpProvider(context, env, capWatcher);
  context.subscriptions.push({ dispose: () => mcpProvider.dispose() });

  // Watch for cross-window update lock
  const venvDir = path.join(context.globalStorageUri.fsPath, VENV_DIR_NAME);

  if (isUpdateLocked(venvDir)) {
    output.appendLine("Update in progress in another window - MCP servers paused.");
    mcpProvider.dispose();
  }

  const lockWatcher = watchUpdateLock(venvDir);
  lockWatcher.onLocked(() => {
    output.appendLine("Update lock acquired by another window - pausing MCP servers.");
    mcpProvider.dispose();
  });
  lockWatcher.onUnlocked(() => {
    output.appendLine("Update lock released - restarting MCP servers.");
    mcpProvider.reregister();
  });
  context.subscriptions.push({ dispose: () => lockWatcher.dispose() });

  registerInitCommands(context, env);
  context.subscriptions.push(registerValidation(context, env, output));

  promptInitForWorkspaces(env).catch(() => {});
  registerMcpNotice(context, capWatcher);

  output.appendLine("CAP activated.");
}

export function deactivate(): void {
  if (output) {
    output.dispose();
  }
}
