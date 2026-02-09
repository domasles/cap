/**
 * Check CLI and extension version compatibility.
 *
 * Runs `cap compatibility --json` and verifies this extension version
 * is in the CLI's list of compatible plugins.
 *
 * Three outcomes:
 * 1. Extension version in list -> proceed normally.
 * 2. Extension version < max(list) -> outdated, block + open marketplace.
 * 3. Extension version > max(list) -> ahead of CLI, warn + allow.
 */

import * as vscode from "vscode";
import { execFile } from "child_process";
import { promisify } from "util";

import { PLUGIN_NAME } from "../constants";
import { isNewer, maxVersion } from "../utils/version";
import type { Environment } from "./environment";

const execFileAsync = promisify(execFile);

interface CompatibilityInfo {
  cli_version: string;
  compatible_plugins: Record<string, string[]>;
}

/**
 * Check if the installed CLI is compatible with this extension version.
 * Returns true if the extension should activate, false to block.
 */
export async function checkCompatibility(
  context: vscode.ExtensionContext,
  env: Environment,
  output: vscode.OutputChannel
): Promise<boolean> {
  if (context.extensionMode === vscode.ExtensionMode.Development) {
    return true;
  }

  const extensionVersion = context.extension.packageJSON.version as string;

  let info: CompatibilityInfo;
  try {
    const { stdout } = await execFileAsync(env.capPath, ["compatibility", "--json"], {
      timeout: 5000,
    });
    info = JSON.parse(stdout.trim());
  } catch {
    // CLI too old to have the compatibility command - warn but allow
    output.appendLine("CAP CLI does not support compatibility check. Update recommended.");
    await vscode.window.showWarningMessage(
      "CAP: Installed CLI does not support compatibility checks. Consider updating CAP packages.",
      "Understood"
    );
    return true;
  }

  const compatibleVersions = info.compatible_plugins[PLUGIN_NAME];
  if (!compatibleVersions || compatibleVersions.length === 0) {
    output.appendLine(`CAP CLI ${info.cli_version} has no compatibility info for "${PLUGIN_NAME}".`);
    return true;
  }

  // Extension version is explicitly supported
  if (compatibleVersions.includes(extensionVersion)) {
    output.appendLine(`CAP CLI ${info.cli_version} is compatible with extension ${extensionVersion}.`);
    return true;
  }

  const highest = maxVersion(compatibleVersions)!;

  // Extension is outdated
  if (isNewer(highest, extensionVersion)) {
    output.appendLine(
      `Extension ${extensionVersion} is outdated. CLI ${info.cli_version} supports: ${compatibleVersions.join(", ")}.`
    );

    const choice = await vscode.window.showErrorMessage(
      `CAP: Extension ${extensionVersion} is outdated. ` +
        `CLI ${info.cli_version} requires one of: ${compatibleVersions.join(", ")}. ` +
        `Please update the extension.`,
      "Open in Marketplace"
    );

    if (choice === "Open in Marketplace") {
      vscode.commands.executeCommand("extension.open", context.extension.id);
    }

    return false;
  }

  // Extension is ahead of CLI
  output.appendLine(
    `Extension ${extensionVersion} is newer than CLI ${info.cli_version} recognizes (max: ${highest}). Allowing with warning.`
  );

  await vscode.window.showWarningMessage(
    `CAP: Extension ${extensionVersion} is newer than what CLI ${info.cli_version} recognizes. ` +
      `Some features may not work correctly until CLI is updated.`,
    "Understood"
  );

  return true;
}
