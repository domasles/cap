/**
 * Run cap CLI commands and return structured results.
 */

import { execFile } from "child_process";
import { promisify } from "util";
import type { OutputChannel } from "vscode";

import type { Environment } from "../setup/environment";

const execFileAsync = promisify(execFile);

export interface CapResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export async function runCap(
  env: Environment,
  args: string[],
  cwd?: string,
  output?: OutputChannel
): Promise<CapResult> {
  try {
    const { stdout, stderr } = await execFileAsync(env.capPath, args, {
      timeout: 30000,
      cwd,
    });
    if (stderr && output) {
      output.appendLine(`[cap ${args[0]}] ${stderr.trim()}`);
    }
    return { stdout, stderr, exitCode: 0 };
  } catch (err: any) {
    const stderr = err.stderr ?? "";
    if (stderr && output) {
      output.appendLine(`[cap ${args[0]}] ${stderr.trim()}`);
    }
    return {
      stdout: err.stdout ?? "",
      stderr,
      exitCode: err.code ?? 1,
    };
  }
}

export interface ValidationErrorItem {
  message: string;
  line: number | null;
  column: number | null;
}

export interface ValidationFileResult {
  file: string;
  valid: boolean;
  errors: ValidationErrorItem[];
}

export async function runValidateJson(
  env: Environment,
  workspacePath: string,
  output?: OutputChannel,
  file?: string
): Promise<ValidationFileResult[]> {
  const args = ["validate", "--json"];
  if (file) {
    args.push("-f", file);
  }
  args.push(workspacePath);
  const result = await runCap(env, args, workspacePath, output);
  try {
    return JSON.parse(result.stdout.trim());
  } catch {
    return [];
  }
}
