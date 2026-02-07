import * as vscode from "vscode";
import * as path from "path";
import { execFile } from "child_process";
import { promisify } from "util";
import * as https from "https";

import { CAP_CLI_PACKAGE, VENV_DIR_NAME } from "../constants";
import { getVenvPython } from "../utils/venv";

const execFileAsync = promisify(execFile);

export async function checkForUpdate(
  context: vscode.ExtensionContext,
  capPath: string,
  output: vscode.OutputChannel
): Promise<void> {
  if (context.extensionMode === vscode.ExtensionMode.Development) {
    return;
  }

  try {
    const installed = await getInstalledVersion(capPath);
    const latest = await getLatestPyPIVersion();
    if (!installed || !latest || installed === latest) {
      return;
    }
    if (!isNewer(latest, installed)) {
      return;
    }

    output.appendLine(`CAP update available: ${installed} → ${latest}`);
    const choice = await vscode.window.showInformationMessage(
      `CAP v${latest} is available (installed: v${installed}). Update now?`,
      "Update",
      "Later"
    );

    if (choice === "Update") {
      await runUpdate(context, output);
    }
  } catch {
    // silently ignore update check failures
  }
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

function isNewer(latest: string, installed: string): boolean {
  const l = latest.split(".").map(Number);
  const i = installed.split(".").map(Number);
  for (let k = 0; k < 3; k++) {
    if ((l[k] ?? 0) > (i[k] ?? 0)) {
      return true;
    }
    if ((l[k] ?? 0) < (i[k] ?? 0)) {
      return false;
    }
  }
  return false;
}

async function runUpdate(
  context: vscode.ExtensionContext,
  output: vscode.OutputChannel
): Promise<void> {
  const venvDir = path.join(context.globalStorageUri.fsPath, VENV_DIR_NAME);
  const venvPython = getVenvPython(venvDir);

  output.appendLine(`Updating ${CAP_CLI_PACKAGE}...`);
  try {
    await execFileAsync(venvPython, ["-m", "pip", "install", "--upgrade", CAP_CLI_PACKAGE], {
      timeout: 60000,
    });
    vscode.window.showInformationMessage("CAP updated. Reload the window to use the new version.", "Reload").then((choice) => {
      if (choice === "Reload") {
        vscode.commands.executeCommand("workbench.action.reloadWindow");
      }
    });
  } catch (err: any) {
    vscode.window.showErrorMessage(`CAP: Update failed. ${err.message}`);
  }
}
