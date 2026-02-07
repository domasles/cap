/**
 * Manage the extension's Python venv and cap-cli installation.
 * Resolves the `cap` executable path for both dev and production modes.
 */

import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";
import { execFile } from "child_process";
import { promisify } from "util";

import { CAP_CLI_PACKAGE, VENV_DIR_NAME } from "../constants";
import { findPython } from "./python";
import { getCapExecutable, getVenvPython } from "../utils/venv";

const execFileAsync = promisify(execFile);

export interface Environment {
  capPath: string;
}

export async function setupEnvironment(
  context: vscode.ExtensionContext,
  output: vscode.OutputChannel
): Promise<Environment | undefined> {
  const isDev = context.extensionMode === vscode.ExtensionMode.Development;

  const python = await findPython(output);
  if (!python) {
    vscode.window
      .showErrorMessage(
        "CAP: Python ≥3.11 not found. Install Python and reload, or set cap.pythonPath.",
        "Get Python"
      )
      .then((choice) => {
        if (choice === "Get Python") {
          vscode.env.openExternal(vscode.Uri.parse("https://www.python.org/downloads/"));
        }
      });
    return undefined;
  }

  if (isDev) {
    return setupDev(output);
  }
  return setupProduction(context, output, python);
}

async function setupDev(
  output: vscode.OutputChannel
): Promise<Environment | undefined> {
  try {
    await execFileAsync("cap", ["--version"], { timeout: 5000 });
    output.appendLine("Dev mode: cap found on PATH.");
    return { capPath: "cap" };
  } catch {
    vscode.window.showWarningMessage(
      "CAP (dev): cap not found on PATH. Run `pip install -e ./core -e ./mcp -e ./shells/cli` from the repo root."
    );
    return undefined;
  }
}

async function setupProduction(
  context: vscode.ExtensionContext,
  output: vscode.OutputChannel,
  systemPython: string
): Promise<Environment | undefined> {

  const venvDir = path.join(context.globalStorageUri.fsPath, VENV_DIR_NAME);
  const capPath = getCapExecutable(venvDir);

  if (!fs.existsSync(capPath)) {
    const ok = await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: "CAP: Setting up environment..." },
      async () => {
        output.appendLine(`Creating venv at ${venvDir}...`);
        try {
          fs.mkdirSync(path.dirname(venvDir), { recursive: true });
          await execFileAsync(systemPython, ["-m", "venv", venvDir]);
        } catch (err: any) {
          vscode.window.showErrorMessage(`CAP: Failed to create venv. ${err.message}`);
          return false;
        }

        output.appendLine(`Installing ${CAP_CLI_PACKAGE}...`);
        const venvPython = getVenvPython(venvDir);
        try {
          await execFileAsync(venvPython, ["-m", "pip", "install", "--upgrade", CAP_CLI_PACKAGE]);
        } catch (err: any) {
          vscode.window.showErrorMessage(`CAP: Failed to install ${CAP_CLI_PACKAGE}. ${err.message}`);
          return false;
        }
        return true;
      }
    );
    if (!ok) {
      return undefined;
    }
  }

  output.appendLine(`cap executable: ${capPath}`);
  return { capPath };
}
