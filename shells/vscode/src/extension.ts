import * as vscode from "vscode";

import { OUTPUT_CHANNEL_NAME } from "./constants";
import { setupEnvironment } from "./setup/environment";
import { registerMcpProvider } from "./mcp/provider";
import { registerInitCommands, promptInitForWorkspaces } from "./cap/init";
import { registerValidation } from "./cap/validate";

let output: vscode.OutputChannel;

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  output = vscode.window.createOutputChannel(OUTPUT_CHANNEL_NAME);
  context.subscriptions.push(output);

  const mode =
    context.extensionMode === vscode.ExtensionMode.Development ? "development" : "production";
  output.appendLine(`CAP activating (${mode})...`);

  const env = await setupEnvironment(context, output);
  if (!env) {
    output.appendLine("Setup failed — extension inactive.");
    return;
  }

  context.subscriptions.push(registerMcpProvider(context, env));
  registerInitCommands(context, env);
  context.subscriptions.push(registerValidation(context, env, output));

  promptInitForWorkspaces(env);
  showMcpNotice(context);
  output.appendLine("CAP activated.");
}

export function deactivate(): void {}

const MCP_NOTICE_KEY = "cap.mcpNoticeShown";

function showMcpNotice(context: vscode.ExtensionContext): void {
  if (context.globalState.get<boolean>(MCP_NOTICE_KEY)) {
    return;
  }
  context.globalState.update(MCP_NOTICE_KEY, true);
  vscode.window
    .showInformationMessage(
      "CAP MCP server registered. Enable it in Copilot Chat MCP settings to give coding agents access to your codebase architecture.",
      "Open MCP Settings"
    )
    .then((choice) => {
      if (choice === "Open MCP Settings") {
        vscode.commands.executeCommand('workbench.action.openSettings', 'mcp');
      }
    });
}
