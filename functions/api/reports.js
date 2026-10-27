// Lecture des signalements, réservée : en-tête « Authorization: Bearer <ADMIN_TOKEN> ».
import { json } from '../../lib/util.js';

export async function onRequestGet({ request, env }) {
  if (!env.REPORTS || !env.ADMIN_TOKEN) return json({ error: 'unavailable' }, 503);
  if (request.headers.get('authorization') !== `Bearer ${env.ADMIN_TOKEN}`) return json({ error: 'forbidden' }, 403);
  const { keys } = await env.REPORTS.list({ prefix: 'r:', limit: 1000 });
  const items = await Promise.all(keys.map(async k => JSON.parse(await env.REPORTS.get(k.name))));
  return json({ count: items.length, items: items.reverse() });
}
