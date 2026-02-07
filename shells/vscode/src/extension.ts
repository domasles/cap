import * as vscode from "vscode";

import { OUTPUT_CHANNEL_NAME } from "./constants";
import { setupEnvironment } from "./setup/environment";
import { checkForUpdate } from "./setup/updater";
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
    output.appendLine("Setup failed — extension inactive.");
    return;
  }

  context.subscriptions.push(registerMcpProvider(context, env));
  registerInitCommands(context, env);
  context.subscriptions.push(registerValidation(context, env));

  promptInitForWorkspaces(env);
  context.subscriptions.push(registerMcpNotice(context));
  checkForUpdate(context, env.capPath, output);

  output.appendLine("CAP activated.");
}

export function deactivate(): void {}
