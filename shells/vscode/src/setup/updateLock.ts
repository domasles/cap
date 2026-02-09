/**
 * File-based update lock for cross-window coordination.
 *
 * When one VS Code window starts a pip update, it writes a lock file
 * to the shared venv directory. All other windows watch for this file
 * and pause their MCP servers until the update completes.
 */

import * as fs from "fs";
import * as path from "path";

import { UPDATE_LOCK_FILE } from "../constants";

const STALE_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

export interface UpdateLockWatcher {
  onLocked: (callback: () => void) => void;
  onUnlocked: (callback: () => void) => void;
  dispose: () => void;
}

function lockPath(venvDir: string): string {
  return path.join(venvDir, UPDATE_LOCK_FILE);
}

export function acquireUpdateLock(venvDir: string): boolean {
  const file = lockPath(venvDir);

  if (fs.existsSync(file)) {
    // Check for stale lock
    try {
      const content = fs.readFileSync(file, "utf-8");
      const timestamp = parseInt(content, 10);
      if (!isNaN(timestamp) && Date.now() - timestamp > STALE_TIMEOUT_MS) {
        // Stale lock - take over
        fs.writeFileSync(file, Date.now().toString());
        return true;
      }
    } catch {
      // Malformed lock file - take over
      fs.writeFileSync(file, Date.now().toString());
      return true;
    }
    return false;
  }

  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, Date.now().toString());
  return true;
}

export function releaseUpdateLock(venvDir: string): void {
  const file = lockPath(venvDir);
  try {
    fs.unlinkSync(file);
  } catch {
    // Already deleted or never existed
  }
}

export function isUpdateLocked(venvDir: string): boolean {
  const file = lockPath(venvDir);
  if (!fs.existsSync(file)) {
    return false;
  }

  try {
    const content = fs.readFileSync(file, "utf-8");
    const timestamp = parseInt(content, 10);
    if (!isNaN(timestamp) && Date.now() - timestamp > STALE_TIMEOUT_MS) {
      // Stale - clean up
      fs.unlinkSync(file);
      return false;
    }
  } catch {
    return false;
  }
  return true;
}

export function watchUpdateLock(venvDir: string): UpdateLockWatcher {
  const file = lockPath(venvDir);
  let lockedCallbacks: (() => void)[] = [];
  let unlockedCallbacks: (() => void)[] = [];
  let wasLocked = fs.existsSync(file);

  // Ensure directory exists before watching
  fs.mkdirSync(venvDir, { recursive: true });

  const watcher = fs.watch(venvDir, (eventType, filename) => {
    if (filename !== UPDATE_LOCK_FILE) {
      return;
    }

    const nowLocked = fs.existsSync(file);
    if (nowLocked && !wasLocked) {
      wasLocked = true;
      for (const cb of lockedCallbacks) {
        cb();
      }
    } else if (!nowLocked && wasLocked) {
      wasLocked = false;
      for (const cb of unlockedCallbacks) {
        cb();
      }
    }
  });

  return {
    onLocked: (callback) => lockedCallbacks.push(callback),
    onUnlocked: (callback) => unlockedCallbacks.push(callback),
    dispose: () => {
      watcher.close();
      lockedCallbacks = [];
      unlockedCallbacks = [];
    },
  };
}
