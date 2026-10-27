// Signalement d'erreur : stocké dans la liaison KV REPORTS. Aucune donnée personnelle (pas d'IP).
import { json, quota } from '../../lib/util.js';
const TYPES = ['chiffre', 'source', 'verdict', 'camp', 'autre'];
const clip = (s, n) => String(s || '').slice(0, n);

export async function onRequestPost({ request, env }) {
  if (!env.REPORTS) return json({ error: 'unavailable' }, 503);
  let b; try { b = await request.json(); } catch { return json({ error: 'invalid' }, 400); }
  const doc = {
    candidate: clip(b.candidate, 40), measure: clip(b.measure, 60), type: TYPES.includes(b.type) ? b.type : 'autre',
    message: clip(b.message, 2000), url: /^https?:\/\//.test(b.url || '') ? clip(b.url, 500) : '', version: clip(b.version, 40),
    at: new Date().toISOString(),
  };
  if (doc.message.trim().length < 10 || !/^[a-z-]+$/.test(doc.candidate)) return json({ error: 'invalid' }, 400);
  const over = await quota(env, request, 'report', 20, 2000);
  if (over) return json({ error: 'limit' }, 429);
  await env.REPORTS.put(`r:${doc.at}:${crypto.randomUUID().slice(0, 8)}`, JSON.stringify(doc));
  return json({ ok: true });
}
