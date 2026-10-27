"""« Pour / Contre » du quiz : lecture de data/quiz_effets.json (utilisé par corrections.py et build.py)."""
PREUVES = ('solide', 'mitigé', 'faible', "pas d'étude")

def quiz_fx(v, k):
    """Ancien format : [plus, moins, sources]. Nouveau : {constat, constat_s, pour, preuve_pour, contre, preuve_contre,
    complement, complement_ref, cas_pour, cas_contre, etudes, src} :
    le constat (la réalité française que la proposition veut traiter : dernier chiffre officiel et évolution en %, même forme pour toutes),
    le meilleur argument réel de chaque côté avec la force de ses preuves (un fait que la mesure ne dit pas d'elle-même :
    effet mesuré, ordre de grandeur ; jamais la mesure redite à l'envers, même test des deux côtés), le complément (une autre mesure du même programme qui répond
    à la critique principale ; le « Contre » porte alors sur ce qui reste) et 0 à 3 cas réels sourcés par côté.
    Même méthode pour toutes les mesures, sans fausse symétrie : aucun cas ajouté pour équilibrer.
    Pas d'« actualité » au cas par cas : un événement récent compte quand il entre dans les statistiques officielles."""
    if isinstance(v, list): return {'quiz_plus': v[0], 'quiz_moins': v[1], **({'quiz_src': v[2]} if len(v) > 2 else {})}
    cp, cc, src = v['cas_pour'], v['cas_contre'], v['src']
    assert 'actu' not in v, f"quiz_effets.json : {k}, pas d'« actualité » au cas par cas : le constat donne le dernier chiffre officiel"
    assert len(cp) <= 3 and len(cc) <= 3, f"quiz_effets.json : {k}, 3 cas réels au plus par côté"
    assert v['preuve_pour'] in PREUVES and v['preuve_contre'] in PREUVES, f"quiz_effets.json : {k}, niveau de preuve manquant"
    assert all(c['s'] and all(0 <= i < len(src) for i in c['s']) for c in cp + cc), f"quiz_effets.json : {k}, chaque cas cite une source de la liste"
    assert len(v['pour']) <= 110 and len(v['contre']) <= 110, f"quiz_effets.json : {k}, « Pour » et « Contre » en 100 caractères environ"
    assert not v.get('complement') or (len(v['complement']) <= 120 and v.get('complement_ref')), f"quiz_effets.json : {k}, complément court, avec la mesure du programme qui le porte"
    assert not v.get('constat') or (len(v['constat']) <= 130 and v.get('constat_s') and all(0 <= i < len(src) for i in v['constat_s'])), f"quiz_effets.json : {k}, constat court et sourcé"
    return {'quiz_plus': v['pour'], 'quiz_moins': v['contre'], 'quiz_preuve_pour': v['preuve_pour'], 'quiz_preuve_contre': v['preuve_contre'],
            'quiz_cas_pour': cp, 'quiz_cas_contre': cc, 'quiz_etudes': v.get('etudes', ''), 'quiz_src': src,
            **({'quiz_constat': {'t': v['constat'], 's': v['constat_s']}} if v.get('constat') else {}),
            **({'quiz_complement': {'t': v['complement'], 'ref': v['complement_ref']}} if v.get('complement') else {})}
