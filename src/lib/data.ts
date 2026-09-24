import { parse } from "yaml";
import papersJson from "../data/papers.json";
import metricsJson from "../data/metrics.json";
import starfieldJson from "../data/starfield.json";
import profileRaw from "../data/profile.yaml?raw";
import talksRaw from "../data/talks.yaml?raw";
import pressRaw from "../data/press.yaml?raw";

export type Category = "first" | "key" | "coauthor";

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  position: number;
  n_authors: number;
  year: number;
  date: string;
  journal: string;
  volume: string | null;
  page: string | null;
  kind: string;
  refereed: boolean;
  category: Category;
  citations: number;
  links: { ads: string | null; arxiv: string | null; doi: string | null };
}

export interface Sky {
  object: string;
  ra?: string;
  dec?: string;
  geo?: string;
  simbad?: string;
  coo?: string;
  note?: string;
}

/** Keep "η Car" (and similar) together on one line. */
const NB = (s: string) => s.replace(/([αβγδηθ]) (Car|Cen|Cru)\b/g, "$1\u00a0$2");
function nbDeep<T>(v: T): T {
  if (typeof v === "string") return NB(v) as T;
  if (Array.isArray(v)) return v.map(nbDeep) as T;
  if (v && typeof v === "object") return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, nbDeep(x)])) as T;
  return v;
}

export const papers = (papersJson as Paper[]).map((p) => ({ ...p, title: NB(p.title) }));
export const metrics = metricsJson;
export const starfield = starfieldJson as { stars: { x: number; y: number; v: number; bv: number }[] };
export const profile = nbDeep(parse(profileRaw));
export interface Talk { year: number; month?: string; title: string; event: string; place?: string; kind?: "oral" | "invited" | "poster" | "selected" }
export const talks = nbDeep(parse(talksRaw)) as Talk[];
export const press = nbDeep(parse(pressRaw)) as { year: number; title: string; outlet: string; url?: string }[];

export const paperById = (id: string) => papers.find((p) => p.id === id);

export const CATEGORY_LABEL: Record<Category, string> = {
  first: "First author",
  key: "Key contributor",
  coauthor: "Co-author",
};

export const SELF = "C. Bordiú";

/** The "refereed" filter counts refereed journal articles only (refereed proceedings excluded),
 *  matching the headline count in metrics.json. */
export const isRefereedArticle = (p: Paper) => p.refereed && p.kind === "article";

/** Author line: first three, then "…, C. Bordiú, …" when further down, then "(+N)". */
export function authorParts(p: Paper): { names: string[]; more: number } {
  const names = [...p.authors];
  if (p.position > names.length) {
    names.push(p.position > names.length + 1 ? `…, ${SELF}` : SELF);
  }
  return { names, more: Math.max(0, p.n_authors - Math.max(p.position, p.authors.length)) };
}

export function venue(p: Paper): string {
  const vol = p.volume && !["arXiv", "ASCL"].includes(p.journal) ? ` ${p.volume}` : "";
  const page = p.page && vol && !/^(stag|staf|staa)/.test(p.page) ? `, ${p.page}` : "";
  return `${p.journal}${vol}${page}`;
}

export function skyLink(s: Sky): string | null {
  if (s.simbad) return `https://simbad.cds.unistra.fr/simbad/sim-id?Ident=${encodeURIComponent(s.simbad)}`;
  if (s.coo) return `https://simbad.cds.unistra.fr/simbad/sim-coo?Coord=${encodeURIComponent(s.coo)}&Radius=2&Radius.unit=arcmin`;
  if (s.geo) return null;
  return null;
}
