/**
 * Run cap CLI commands and return structured results.
 */

import { execFile } from "child_process";
import { promisify } from "util";

import type { CapEnvironment } from "../setup/environment";

const execFileAsync = promisify(execFile);

export interface CapResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export async function runCap(
  env: CapEnvironment,
  args: string[],
  cwd?: string
): Promise<CapResult> {
  try {
    const { stdout, stderr } = await execFileAsync(env.capPath, args, {
      timeout: 30000,
      cwd,
    });
    return { stdout, stderr, exitCode: 0 };
  } catch (err: any) {
    return {
      stdout: err.stdout ?? "",
      stderr: err.stderr ?? "",
      exitCode: err.code ?? 1,
    };
  }
}

export interface ValidationFileResult {
  file: string;
  valid: boolean;
  errors: string[];
}

export async function runValidateJson(
  env: CapEnvironment,
  workspacePath: string
): Promise<ValidationFileResult[]> {
  const result = await runCap(env, ["validate", "--json", workspacePath], workspacePath);
  try {
    return JSON.parse(result.stdout.trim());
  } catch {
    return [];
  }
}
