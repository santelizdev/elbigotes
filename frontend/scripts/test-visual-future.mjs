import { access } from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";

const frontendRoot = process.cwd();
const playwrightBin = path.join(frontendRoot, "node_modules", ".bin", "playwright");

async function exists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

if (!(await exists(playwrightBin))) {
  console.log("Playwright future runner scaffold listo.");
  console.log("Para habilitar snapshots o QA visual automatizado instala primero @playwright/test.");
  console.log("Luego este mismo runner podrá ejecutar: playwright test");
  process.exit(0);
}

const child = spawn(playwrightBin, ["test"], {
  stdio: "inherit",
  cwd: frontendRoot,
});

child.on("exit", (code) => {
  process.exit(code ?? 0);
});
