import { pathToFileURL } from "node:url";

const configured = process.env.CODEX_SKY_ENTRY;
if (!configured) {
  console.error(
    "sky_probe requires OpenAI Codex's private @oai/sky module and is not portable.\n" +
      "Set CODEX_SKY_ENTRY to that module's index.js path (or a file:// URL).\n" +
      "See README.md; no public replacement is bundled.",
  );
  process.exit(2);
}

const entry = configured.startsWith("file:")
  ? new URL(configured)
  : pathToFileURL(configured);

let skyModule;
try {
  skyModule = await import(entry.href);
} catch (error) {
  console.error(`could not import @oai/sky from ${entry.href}\n${error.message}`);
  process.exit(1);
}

const { sky } = skyModule;
console.log("sky imported ok");
const apps = await sky.list_apps();
console.log(JSON.stringify(apps, null, 2));
