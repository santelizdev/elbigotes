import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const frontendRoot = process.cwd();
const srcRoot = path.join(frontendRoot, "src");

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = await Promise.all(
    entries.map(async (entry) => {
      const fullPath = path.join(directory, entry.name);
      if (entry.isDirectory()) {
        return walk(fullPath);
      }
      return fullPath;
    }),
  );

  return files.flat();
}

async function read(relativePath) {
  return readFile(path.join(frontendRoot, relativePath), "utf8");
}

async function assertNoCssModuleImports() {
  const files = await walk(srcRoot);
  const sourceFiles = files.filter((file) => file.endsWith(".ts") || file.endsWith(".tsx"));
  const offenders = [];

  for (const file of sourceFiles) {
    const contents = await readFile(file, "utf8");
    if (contents.includes(".module.css")) {
      offenders.push(path.relative(frontendRoot, file));
    }
  }

  assert.deepEqual(
    offenders,
    [],
    `Estos archivos siguen importando CSS modules legacy:\n${offenders.join("\n")}`,
  );
}

async function assertNoLegacyUtilityClassUsage() {
  const files = await walk(srcRoot);
  const sourceFiles = files.filter((file) => file.endsWith(".ts") || file.endsWith(".tsx"));
  const offenders = [];

  for (const file of sourceFiles) {
    const contents = await readFile(file, "utf8");
    if (
      contents.includes('className="text-button') ||
      contents.includes("className={`text-button") ||
      contents.includes("className='text-button") ||
      contents.includes('className="skeleton-card') ||
      contents.includes("className={`skeleton-card") ||
      contents.includes("className='skeleton-card") ||
      contents.includes("skeleton-card__line") ||
      contents.includes('className="map-loading-shell') ||
      contents.includes("className={`map-loading-shell") ||
      contents.includes("className='map-loading-shell") ||
      contents.includes("map-legend__") ||
      contents.includes('className="map-legend') ||
      contents.includes("className={`map-legend") ||
      contents.includes("className='map-legend")
    ) {
      offenders.push(path.relative(frontendRoot, file));
    }
  }

  assert.deepEqual(
    offenders,
    [],
    `Estos archivos siguen usando utilidades legacy que ya debieron extraerse:\n${offenders.join("\n")}`,
  );
}

async function assertFileContains(relativePath, snippets) {
  const contents = await read(relativePath);
  for (const snippet of snippets) {
    assert.ok(
      contents.includes(snippet),
      `${relativePath} debería incluir: ${snippet}`,
    );
  }
}

async function assertFoundationAdoption() {
  await assertFileContains("src/components/places/place-profile.tsx", [
    'import { PageHero }',
    'import { PageShell }',
    'import { SectionHeader }',
    'import { SurfaceCard }',
  ]);

  await assertFileContains("src/components/places/place-detail-sheet.tsx", [
    'import { SectionHeader }',
    'import { SurfaceCard }',
  ]);

  await assertFileContains("src/components/places/place-list.tsx", [
    'import { SurfaceCard }',
  ]);

  await assertFileContains("src/components/lost-pets/lost-pets-explorer.tsx", [
    'import { PageHero }',
    'import { PageShell }',
    'import { SectionHeader }',
    'import { SurfaceCard }',
  ]);

  await assertFileContains("src/components/lost-pets/lost-pet-report-card.tsx", [
    'import { SurfaceCard }',
  ]);

  await assertFileContains("src/components/map/leaflet-map.tsx", [
    'import { MapLoadingShell }',
  ]);

  await assertFileContains("src/components/map/map-legend.tsx", [
    'className="flex flex-wrap items-center justify-end gap-3"',
  ]);

  await assertFileContains("src/components/chrome/site-header.tsx", [
    'const [theme, setTheme] = useState<ThemeMode>("light");',
  ]);

  await assertFileContains("src/components/chrome/theme-toggle.tsx", [
    'const [theme, setTheme] = useState<ThemeMode>("light");',
  ]);

  await assertFileContains("src/components/places/place-list.tsx", [
    'import { SkeletonCard, SkeletonLine }',
    'import { TextButton }',
  ]);

  await assertFileContains("src/components/places/place-card.tsx", [
    'import { TextButton }',
  ]);

  await assertFileContains("src/components/lost-pets/lost-pet-report-form.tsx", [
    'import { FormCheckbox, FormField, FormGrid, InfoBox }',
    'import { PageHero }',
    'import { PageShell }',
    'import { SurfaceCard }',
  ]);

  await assertFileContains("src/components/accounts/business-profile-edit-form.tsx", [
    'import { FormCheckbox, FormField, FormGrid, InfoBox }',
    'import { PageHero }',
    'import { PageShell }',
    'import { SurfaceCard }',
  ]);

  await assertFileContains("src/components/accounts/business-branch-create-form.tsx", [
    'import { FormField, FormGrid, InfoBox }',
    'import { PageHero }',
    'import { PageShell }',
    'import { SurfaceCard }',
  ]);
}

async function assertDocsStayInSync() {
  const contents = await read("../docs/frontend/tailwind-foundation.md");
  const documentedComponents = [
    "`PlaceGoogleRating`",
    "`PlaceLoopActions`",
    "`PlaceList`",
    "`PlaceDetailSheet`",
    "`PlaceProfile`",
    "`LostPetsExplorer`",
    "`LostPetReportCard`",
    "`LostPetReportForm`",
    "`TextButton`",
    "`SkeletonCard`",
    "`MapLoadingShell`",
    "`MapLegend`",
    "`BusinessProfileEditForm`",
    "`BusinessBranchCreateForm`",
  ];

  for (const component of documentedComponents) {
    assert.ok(
      contents.includes(component),
      `La documentación frontend debe incluir ${component}`,
    );
  }
}

async function main() {
  await assertNoCssModuleImports();
  await assertNoLegacyUtilityClassUsage();
  await assertFoundationAdoption();
  await assertDocsStayInSync();
  console.log("UI foundation checks passed.");
}

await main();
