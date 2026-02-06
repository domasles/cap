/**
 * Find a Python ≥3.10 interpreter on the system.
 */

import * as vscode from "vscode";
import { execFile } from "child_process";
import { promisify } from "util";

import { MIN_PYTHON_VERSION } from "../constants";

const execFileAsync = promisify(execFile);

const CANDIDATES: string[] =
  process.platform === "win32"
    ? ["python", "python3", "py -3"]
    : ["python3", "python"];

export async function findPython(
  output: vscode.OutputChannel
): Promise<string | undefined> {
  const configured = vscode.workspace
    .getConfiguration("cap")
    .get<string>("pythonPath");

  if (configured && (await isValid(configured))) {
    return configured;
  }

  for (const candidate of CANDIDATES) {
    const parts = candidate.split(" ");
    const cmd = parts[0];
    try {
      const { stdout } = await execFileAsync(cmd, [...parts.slice(1), "--version"], {
        timeout: 5000,
      });
      if (meetsVersion(stdout.trim())) {
        if (parts.length > 1) {
          const { stdout: exe } = await execFileAsync(
            cmd,
            [...parts.slice(1), "-c", "import sys; print(sys.executable)"],
            { timeout: 5000 }
          );
          return exe.trim();
        }
        return cmd;
      }
    } catch {
      continue;
    }
  }

  output.appendLine("No Python ≥3.10 found.");
  return undefined;
}

async function isValid(pythonPath: string): Promise<boolean> {
  try {
    const { stdout } = await execFileAsync(pythonPath, ["--version"], {
      timeout: 5000,
    });
    return meetsVersion(stdout.trim());
  } catch {
    return false;
  }
}

function meetsVersion(versionString: string): boolean {
  const match = versionString.match(/Python\s+(\d+)\.(\d+)/);
  if (!match) {
    return false;
  }
  const [major, minor] = [parseInt(match[1], 10), parseInt(match[2], 10)];
  const [reqMajor, reqMinor] = MIN_PYTHON_VERSION;
  return major > reqMajor || (major === reqMajor && minor >= reqMinor);
}
