const SKY_ENTRY = new URL(
  "file:///C:/Program%20Files/WindowsApps/OpenAI.Codex_26.803.5235.0_x64__2p2nqsd0c76g0/app/resources/cua_node/bin/node_modules/@oai/sky/dist/project/cua/sky_js/src/index.js",
);
const { sky } = await import(SKY_ENTRY.href);
console.log("sky imported ok");
const apps = await sky.list_apps();
console.log(JSON.stringify(apps, null, 2));
