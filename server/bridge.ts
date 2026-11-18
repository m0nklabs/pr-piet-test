// Verify-PR for fallback 1.6: a code file with template literals and
// dedented control flow, so a review's suggested_fix has backtick-heavy
// content — the shape that broke YAML parsing twice in production.
export function makeQuery(table: string, where: string[]): string {
  const conditions = where.map((w) => `  AND ${w}`).join("\n");
  return `
    SELECT * FROM ${table}
    WHERE 1 = 1
${conditions}
  `;
}

export function route(store: string): number {
  const catalog = getCatalog();
  if (!catalog.usable) {
    throw new Error("stale");
  }
  const model = catalog.models.get(store);
  if (model === undefined) {
    return 404;
  }
  return 200;
}

function getCatalog(): { usable: boolean; models: Map<string, number> } {
  return { usable: true, models: new Map([["dirk", 1]]) };
}
