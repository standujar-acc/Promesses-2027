export const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });

export async function hash(s) {
  const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(d)].slice(0, 12).map(b => b.toString(16).padStart(2, '0')).join('');
}

// Compteur journalier par visiteur (IP hachée, jamais stockée en clair) et global.
export async function quota(env, request, scope, perVisitor, global) {
  if (!env.LIMITS) return null;
  const day = new Date().toISOString().slice(0, 10);
  const who = await hash((request.headers.get('cf-connecting-ip') || '0') + day + (env.SALT || ''));
  const kU = `${scope}:u:${day}:${who}`, kG = `${scope}:g:${day}`;
  const [u, g] = await Promise.all([env.LIMITS.get(kU), env.LIMITS.get(kG)]);
  if (+u >= perVisitor) return 'visitor';
  if (+g >= global) return 'global';
  await Promise.all([
    env.LIMITS.put(kU, String(+u + 1), { expirationTtl: 172800 }),
    env.LIMITS.put(kG, String(+g + 1), { expirationTtl: 172800 }),
  ]);
  return null;
}
