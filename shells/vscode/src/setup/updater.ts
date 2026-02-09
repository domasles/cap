import * as vscode from "vscode";
import * as path from "path";
import { execFile } from "child_process";
import { promisify } from "util";
import * as https from "https";

import { CAP_CLI_PACKAGE, VENV_DIR_NAME } from "../constants";
import { getVenvPython } from "../utils/venv";
import { isNewer } from "../utils/version";
import { acquireUpdateLock, releaseUpdateLock } from "./updateLock";
import type { McpProviderHandle } from "../mcp/provider";

const execFileAsync = promisify(execFile);

export async function checkForUpdate(
  context: vscode.ExtensionContext,
  capPath: string,
  output: vscode.OutputChannel,
  mcpProvider?: McpProviderHandle
): Promise<boolean> {
  if (context.extensionMode === vscode.ExtensionMode.Development) {
    return false;
  }

  try {
    const installed = await getInstalledVersion(capPath);
    const latest = await getLatestPyPIVersion();
    if (!installed || !latest || installed === latest) {
      return false;
    }
    if (!isNewer(latest, installed)) {
      return false;
    }

    output.appendLine(`CAP update available: ${installed} -> ${latest}`);
    const choice = await vscode.window.showInformationMessage(
      `CAP ${latest} is available (installed: ${installed}). Update now?`,
      "Update",
      "Later"
    );

    if (choice === "Update") {
      return await runUpdate(context, output, mcpProvider);
    }
  } catch {
    // Silently ignore update check failures
  }
  return false;
}

async function getInstalledVersion(capPath: string): Promise<string | undefined> {
  try {
    const { stdout } = await execFileAsync(capPath, ["--version"], { timeout: 5000 });
    const match = stdout.trim().match(/(\d+\.\d+\.\d+)/);
    return match?.[1];
  } catch {
    return undefined;
  }
}

function getLatestPyPIVersion(): Promise<string | undefined> {
  return new Promise((resolve) => {
    const req = https.get(
      `https://pypi.org/pypi/${CAP_CLI_PACKAGE}/json`,
      { timeout: 5000 },
      (res) => {
        let data = "";
        res.on("data", (chunk: Buffer) => (data += chunk));
        res.on("end", () => {
          try {
            const json = JSON.parse(data);
            resolve(json.info?.version);
          } catch {
            resolve(undefined);
          }
        });
      }
    );
    req.on("error", () => resolve(undefined));
    req.on("timeout", () => {
      req.destroy();
      resolve(undefined);
    });
  });
}

const MAX_RETRY_ATTEMPTS = 3;

export async function runUpdate(
  context: vscode.ExtensionContext,
  output: vscode.OutputChannel,
  mcpProvider?: McpProviderHandle,
  attempt: number = 1
): Promise<boolean> {
  const venvDir = path.join(context.globalStorageUri.fsPath, VENV_DIR_NAME);
  const venvPython = getVenvPython(venvDir);

  // Acquire cross-window update lock
  if (!acquireUpdateLock(venvDir)) {
    vscode.window.showInformationMessage("CAP: An update is already in progress in another window.");
    return false;
  }

  // Pause MCP servers so pip can replace files
  mcpProvider?.pause();
  output.appendLine("MCP servers paused for update.");

  // Brief delay to let other windows react to the lock file
  await new Promise((resolve) => setTimeout(resolve, 2000));

  output.appendLine(`Updating ${CAP_CLI_PACKAGE}...`);
  try {
    await execFileAsync(venvPython, ["-m", "pip", "install", "--upgrade", CAP_CLI_PACKAGE], {
      timeout: 60000,
    });

    // Release lock and restart MCP servers
    releaseUpdateLock(venvDir);
    mcpProvider?.resume();
    output.appendLine("CAP updated successfully. MCP servers restarted.");

    vscode.window.showInformationMessage("CAP updated successfully. MCP servers restarted.");

    return true;
  } catch (err: any) {
    // Release lock even on failure
    releaseUpdateLock(venvDir);
    mcpProvider?.resume();

    if (attempt < MAX_RETRY_ATTEMPTS) {
      const choice = await vscode.window.showErrorMessage(
        `CAP: Update failed. ${err.message}`,
        "Retry"
      );

      if (choice === "Retry") {
        return await runUpdate(context, output, mcpProvider, attempt + 1);
      }
    } else {
      vscode.window.showErrorMessage(
        `CAP: Update failed after ${MAX_RETRY_ATTEMPTS} attempts. ${err.message}`
      );
    }

    return false;
  }
}
