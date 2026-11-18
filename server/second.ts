export function helper(values: number[]): number {
  let total = 0;
  for (const v of values) {
    total += v;
  }
  return total;
}

export const ROUTES = `
  /api/grocery/import
  /api/grocery/search
`.trim();
