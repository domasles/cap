/**
 * Find a Python ≥3.11 interpreter on the system.
 */

import * as vscode from "vscode";
import { execFile } from "child_process";
import { promisify } from "util";

import { MIN_PYTHON_VERSION } from "../constants";

const execFileAsync = promisify(execFile);

interface PythonCandidate {
  cmd: string;
  args: string[];
}

const CANDIDATES: PythonCandidate[] =
  process.platform === "win32"
    ? [
        { cmd: "python", args: [] },
        { cmd: "python3", args: [] },
        { cmd: "py", args: ["-3"] },
      ]
    : [
        { cmd: "python3", args: [] },
        { cmd: "python", args: [] },
      ];

export async function findPython(
  output: vscode.OutputChannel
): Promise<string | undefined> {
  const configured = vscode.workspace
    .getConfiguration("cap")
    .get<string>("pythonPath");

  if (configured && (await isValid(configured))) {
    return configured;
  }

  for (const { cmd, args } of CANDIDATES) {
    try {
      const { stdout } = await execFileAsync(cmd, [...args, "--version"], {
        timeout: 5000,
      });
      if (meetsVersion(stdout.trim())) {
        if (args.length > 0) {
          const { stdout: exe } = await execFileAsync(
            cmd,
            [...args, "-c", "import sys; print(sys.executable)"],
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

  output.appendLine("No Python ≥3.11 found.");
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
