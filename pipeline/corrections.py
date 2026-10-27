import json,random,re
D=json.load(open('base.json'))
C={c['id']:c for c in D['candidates']}
def M(cid,mid): return next(m for m in C[cid]['measures'] if m['id']==mid)
def K(cid,mid,central,low,high,formula=None,note=None,inputs_add=None):
    k=M(cid,mid)['claude']; k.update(central=central,low=low,high=high)
    if formula: k['formula']=formula
    if note is not None: k['note']=note
    if inputs_add: k['inputs']=k.get('inputs',[])+inputs_add
POST="Règle commune : 61,6 k€ par poste (362,1 Md€ / 5,88 M d'agents), moitié rendue aux agents, 70 % du plan réalisé en 2030 (3,5 ans sur 5)"
IN_POST={"label":"Masse salariale et effectifs publics","value":"362,1 Md€ ; 5,88 M d'agents","source":"Cour des comptes (Journal de l'économie)","url":"https://www.journaldeleconomie.fr/?p=49417"}
R62="Retour à 62 ans en 2030 : 13,6 Md€ (médiane de 11,8 Montaigne, 13,6 CNAV, 14,1 étude d'impact), valeur commune à tous les candidats"
IN62=[{"label":"Rendement de la réforme 2023 en 2030","value":"11,8 Md€","source":"Institut Montaigne","url":"https://www.institutmontaigne.org/legislatives-2024/ensemble-majorite-presidentielle/repousser-lage-de-depart-a-la-retraite-a-64-ans-avec-des-exemptions-pour-les-situations-de-penibilite-et-de-carrieres-longues"},
      {"label":"Report à 64 ans en 2030","value":"13,6 Md€","source":"CNAV (Public Sénat)","url":"https://www.publicsenat.fr/actualites/politique/reforme-des-retraites-combien-pourrait-rapporter-le-report-de-l-age-legal-a-65"},
      {"label":"Abrogation en 2030","value":"14,1 Md€","source":"Étude d'impact (MoneyVox)","url":"https://www.moneyvox.fr/retraite/actualites/98707/abroger-la-reforme-des-retraites-et-le-depart-a-64-ans-combien-ca-coute"}]
# --- retraites harmonisées
k=M('le-pen','retraites')['claude']; k.update(central=-17.6,low=-40,high=-14,formula=R62+" ; + départ à 60 ans des carrières précoces ≈ 4 Md€ (iFRAP) ; total ≈ −17,6",inputs=IN62+[{"label":"60 ans pour les carrières longues","value":"≈4 Md€","source":"iFRAP","url":"https://www.ifrap.org/retraite/retraites-et-si-lon-arretait-de-mentir-aux-francais"}],note="Borne basse : version Montaigne 2024 plus large (26,5 Md€ pour les carrières précoces). « Corrections » de 15-20 Md€ annoncées par le RN non détaillées, non comptées")
k=M('glucksmann','retraites')['claude']; k.update(central=-13.6,low=-14.1,high=-10.4,formula=R62,inputs=IN62,note="Départs anticipés pour pénibilité non chiffrés")
k=M('melenchon','retraites')['claude']; k.update(central=-34,low=-58,high=-13.6,formula=R62+" ; passage à 60 ans « plus tard dans le mandat » : moitié du surcoût en 2030 (50 à 58 Md€ à pleine charge) ; total ≈ −34",inputs=IN62+[{"label":"Retour à 60 ans à pleine charge","value":"50 à 58 Md€","source":"iFRAP / Institut Montaigne","url":"https://www.institutmontaigne.org/legislatives-2024/nouveau-front-populaire/synthese"}],note="Même règle de montée en charge que pour Philippe : la mesure est comptée à son état prévu en 2030")
# --- Zucman unique
ZU="Taxe Zucman : valeur commune +5 Md€ (médiane de 20 selon Zucman, 5 et 5,5 selon les critiques, 1,25 si IS imputé)"
k=M('glucksmann','zucman'); k['claude'].update(formula=ZU); k['a_confirmer']=True
k=M('melenchon','fiscalite')['claude']; k.update(central=21.4,low=9,high=35,formula="ISF climatique 4 + Zucman 5 (valeur commune) + héritages 9 + fin de la flat tax 3,4 = +21,4 Md€")
# --- SMIC base 2026
k=M('melenchon','smic')['claude']; k.update(central=-20,low=-23,high=-4,formula="Base SMIC juin 2026 (1 477,93 € net) : 1 700 € = +15 % ; Montaigne ≈ 19 Md€ pour +13,2 % → ≈ −20 Md€",inputs=[{"label":"SMIC à 1 600 € net (base 2024)","value":"19 Md€ pour +13,2 % de brut","source":"Institut Montaigne","url":"https://www.institutmontaigne.org/legislatives-2024/nouveau-front-populaire/augmenter-le-smic-a-1600-e-net"},{"label":"SMIC au 1er juin 2026","value":"1 867,02 € brut","source":"FFB","url":"https://www.ffbatiment.fr/actualites-batiment/actualite/augmentation-smic-juin-2026"}])
k=M('glucksmann','smic')['claude']; k.update(central=-11,low=-17,high=-3,formula="Base SMIC juin 2026 (1 477,93 € net) : 1 600 € = +8,3 % ; Montaigne ≈ 19 Md€ pour +13,2 % → ≈ −11 Md€",inputs=M('melenchon','smic')['claude']['inputs'],note="Étalement sur deux ans : effet en 2030 à pleine charge")
# --- CVAE déjà supprimée en 2030
CV={"label":"CVAE supprimée d'ici 2030 par la loi actuelle","value":"LF 2025, confirmée en LF 2026","source":"Légifiscal","url":"https://www.legifiscal.fr/actualites-fiscales/4401-plf-2026-49-3-baisse-cvae-2026.html"}
k=M('le-pen','production'); k['claude'].update(central=-13,low=-17,high=-5.1,formula="CFE + C3S (+ autres) ≈ 17 Md€ − CVAE déjà supprimée en 2030 (≈4) ≈ −13 Md€",inputs=k['claude']['inputs']+[CV])
k=M('lisnard','impots'); k['claude'].update(central=-5.1,low=-5.4,high=-4,formula="C3S seule (≈5,1 Md€) : la CVAE est déjà supprimée en 2030",inputs=k['claude']['inputs']+[CV]); k['verdict']='faisable'
k=M('zemmour','production'); k['claude'].update(central=-21,low=-26,high=-19.8,formula="30,4 Md€ − 6 Md€ d'IS récupéré − CVAE déjà supprimée (≈4) ≈ −21 Md€",inputs=k['claude']['inputs']+[CV]); k['claimed_md']=None; k['a_confirmer']=True; k['verdict']='faisable'
k=M('retailleau','production'); k['claude'].update(central=-10,low=-16,high=-8,formula="Détail du camp : C3S 5,3 + forfait social 2,8 + CFE industrielle 1,9 + heures sup ≈ 10 Md€ en 2030 (CVAE 4,3 retirée : déjà supprimée par la loi)",inputs=k['claude']['inputs']+[CV])
# --- fonction publique : règle commune
def post(cid,mid,c,l,h,f): k=M(cid,mid)['claude']; k.update(central=c,low=l,high=h,formula=POST+" ; "+f); k['inputs']=[IN_POST]+[i for i in k.get('inputs',[]) if 'Masse salariale' not in i['label']]
post('philippe','fonction',5.4,2.7,8,"250 000 postes × 70 % × 30,8 k€ ≈ +5,4 Md€")
post('retailleau','etat',10.3,5,18,"400 000 postes × 70 % × 30,8 k€ = 8,6 + agences 1,6 + carence 0,1 ≈ +10,3 Md€")
post('attal','fonctionnaires',2.2,1.5,4.3,"100 000 postes × 70 % × 30,8 k€ ≈ +2,2 Md€")
post('lisnard','fonction',5.9,3,11,"1 départ sur 3 non remplacé (hypothèse) : 160 000 postes × 30,8 k€ = 4,9 + agences ≈ 1 → +5,9 Md€")
post('zemmour','fonctionnaires',12,6,17,"800 000 × 70 % × 30,8 k€ = 17,2 au maximum ; central 12 car les départs hors secteurs épargnés ne suffisent pas")
post('le-pen','etat',5,0.5,13.5,"200 000 postes × 70 % × 30,8 k€ = 4,3 + agences ≈ 0,7 → +5 Md€")
for cid,mid in [('lisnard','fonction'),('philippe','fonction'),('retailleau','etat'),('attal','fonctionnaires')]: M(cid,mid)['verdict']='sous_conditions'
M('zemmour','fonctionnaires')['verdict']='tres_difficile'
# --- verdicts révision constitutionnelle / capitalisation
for cid,mid,ob in [('retailleau','immigration',"Chemin : révision de la Constitution par l'article 89 (vote identique de l'Assemblée et du Sénat, puis référendum) ; l'article 11 ne le permet pas en l'état."),
                   ('lisnard','referendum',"Chemin : révision de la Constitution par l'article 89, accord des deux chambres requis."),
                   ('melenchon','constituante',"Chemin : révision par l'article 89 (accord du Sénat) ; la voie de l'article 11 est contestée par les constitutionnalistes.")]:
    m=M(cid,mid); m['verdict']='bloque'; m['obstacle']=ob
M('lisnard','retraites')['verdict']='sous_conditions'
# --- Retailleau : effets annuels 2030 (rampe linéaire sur 5 ans : 2030 = 4/15 du cumul)
k=M('retailleau','retraites')['claude']; k.update(central=3.2,low=0,high=11.2,formula="Décote : 12 Md€ cumulés sur 5 ans, montée linéaire → 4/15 × 12 ≈ +3,2 Md€ en 2030 ; plan complet 42 Md€ → 11,2 au maximum",note="Aucune estimation indépendante publiée ; capitalisation : coût de transition non chiffré")
k=M('retailleau','immigration')['claude']; k.update(central=1.5,low=0,high=2.7,formula="10 Md€ cumulés → 4/15 × 10 ≈ 2,7 en 2030 ; hors part liée au référendum ≈ 1,5")
m=M('retailleau','travail'); m['estimates']=[e for e in m['estimates'] if 'Décodeurs' not in e['source'] and 'acrobatique' not in e['value']]
C['retailleau']['claude_total']['missing']="assurance chômage, capitalisation, audiovisuel public, aide au développement, et des postes du plan non vérifiés : collectivités 10, fraude 5, budget base zéro 11,5, santé 4, formation professionnelle 6 Md€ (cumulés)"
# --- divers
k=M('melenchon','prix'); k['claude'].update(central=-9,low=-24,high=0,formula="Chiffrage Montaigne de la mesure NFP : 9 Md€/an ; une estimation de presse à 24 Md€ en borne basse"); k['consensus']='divergent'
M('glucksmann','heritages')['claimed_md']=0
M('philippe','profs')['claimed_md']=None
M('zemmour','famille')['a_confirmer']=True
m=M('le-pen','ue'); 
for i in m['claude']['inputs']:
    if 'Prélèvement' in i['label']: i['value']="31,2 Md€ en 2027 ; solde net −9,5 Md€"
# Lisnard cotisations = 60 % des économies identifiées
ids={'fonction':5.9,'retraites':4,'allocation':22,'ame':0.7}
s=sum(ids.values()); c=-round(0.6*s,1)
k=M('lisnard','cotisations')['claude']; k.update(central=c,low=-48,high=-12,formula=f"Règle du candidat : 60 % des économies rendues. Économies identifiées dans l'app : {str(round(s,1)).replace('.',',')} Md€ → −{abs(c)} Md€ ; borne basse : 48 Md€ promis dès l'an 1",note="Le gain de 400 €/mois n'est atteint que si les 200 Md€ d'économies sont réalisés")
M('lisnard','cotisations')['verdict']='sous_conditions'
M('lisnard','depense')['claimed']="80 Md€ la 1re année, 200 Md€ par an en fin de mandat"
M('lisnard','depense')['proposal']="80 Md€ d'économies dès l'an 1, puis 200 Md€ par an ; 60 % rendus en salaires nets, 20 % en baisse d'impôts de production, 20 % pour la dette."
# --- review 3 : sources et fraîcheur (vérification du 26/10/2026)
m=M('philippe','fonction'); m['proposal']="Ne pas remplacer un départ à la retraite sur trois, ≈250 000 postes en moins sur 5 ans ; regrouper les opérateurs."
for e in M('philippe','retraites')['estimates']:
    if e['source'].startswith('Trésor'): e['source']='Gouvernement (via Public Sénat)'
m=M('melenchon','point_indice'); m['proposal']="Revaloriser de 10 % le point d'indice des fonctionnaires des trois versants."
m['claimed']="+10 % = 17 Md€/an"; m['claimed_md']=-17
m['estimates'].insert(0,{"source":"LFI, note sur les comptes publics","year":2026,"value":"+10 % du point d'indice = 17 Md€","low_md":-17,"high_md":-17,"url":"https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf"})
for i in M('le-pen','ue')['claude']['inputs']:
    if 'Prélèvement' in i['label']: i['value']="30,9 Md€ en 2027 ; solde net −9,5 Md€"
for i in M('le-pen','immigration')['claude']['inputs']:
    if 'fragile' in i['label']: i['label']="Montant RN non documenté, fragile ou sans effet"; i['value']="92 % de 29 Md€, dont 18,1 Md€ juridiquement fragiles"
for e in M('le-pen','immigration')['estimates']:
    if e['source']=="Institut de l'Entreprise": e['value']="92 % du poste non documenté, fragile ou sans effet ; 18,1 Md€ juridiquement fragiles"
for e in M('le-pen','fraude')['estimates']:
    if e['source']=="Institut de l'Entreprise": e['value']="100 % du montant sans mode opératoire documenté (catégorie B)"
for i in M('le-pen','fraude')['claude']['inputs']:
    if 'TVA' in i['label']: i.update(value="12,1 Md€ (2023)",source="Commission européenne, VAT gap report 2025 (via La Grande Conversation)",url="https://www.lagrandeconversation.com/politique/rn-les-mauvais-comptes-dun-budget-dope-a-lia/")
m=M('le-pen','retraites'); m['claimed']="1,9 Md€ en 2027, 9,5 Md€ en 2031 selon le RN ; détail annoncé pour le 17 novembre 2026"; m['claimed_md']=-9.5
m=M('glucksmann','heritages'); m['proposal']="Taxer le 1 % des plus gros héritages pour hausser les salaires nets / baisser la CSG."
for e in M('glucksmann','heritages')['estimates']+M('glucksmann','retraites')['estimates']:
    e['source']=e['source'].replace('Brut (7 économistes)','Brut (économistes)')
for c0 in D['candidates']:
    for m in c0['measures']:
        for e in m['estimates']:
            if e['source'].startswith("Institut de l'Entreprise") and 'Zucman' in (m['title']+m['proposal']+e['value']):
                e['source']="Institut de l'Entreprise (note de plaidoyer)"; e['value']=e['value'].replace('≈25 %','14 à 34 %')
        for i in (m.get('claude') or {}).get('inputs',[]):
            if i['source'].startswith("Institut de l'Entreprise") and 'Zucman' in (m['title']+m['proposal']+i['label']):
                i['source']="Institut de l'Entreprise (note de plaidoyer)"; i['value']=i['value'].replace('≈25 %','14 à 34 %')
M('retailleau','etat')['claimed']="25 Md€ (400 000 départs non remplacés) + 12,5 Md€ (agences), cumulés d'ici 2032"
for mid in ('csg','succession'):
    m=M('zemmour',mid); m['a_confirmer']=True; m['proposal']=m['proposal'].replace(' ; principe confirmé en 2026','').replace(' (annonce 2026)','')+" Reprise en août 2026 dans un livre de Sarah Knafo (Reconquête), pas encore dans un programme du candidat."
    m['estimates'].append({"source":"CNews (livre de S. Knafo)","year":2026,"value":"CSG et droits de succession parmi 15 mesures proposées","low_md":None,"high_md":None,"url":"https://www.cnews.fr/france/2026-08-30/impots-depenses-csg-droits-de-succession-sarah-knafo-devoile-15-mesures-pour"})
C['zemmour']['sim']['salaire_net']=None
C['zemmour']['sim']['salaire_note']="Baisse de la CSG sur les salaires jusqu'à 2 000 € net (programme 2022, non reconfirmée en 2026) : non comptée ici."
C['zemmour']['sim']['heritage']=[{"seuil":100000,"effet":"Abolition des droits de succession (programme 2022, non reconfirmée en 2026) ; la plupart des héritages en ligne directe sous 100 000 € par enfant ne sont déjà pas taxés."}]
C['melenchon']['sim']['point_indice_pct']=10
C['melenchon']['sim']['extra_min']=4000
for c0 in D['candidates']:
    if c0['id']=='le-pen': c0['poll']='32-33,5 %'
D['statu_quo']['smic_url']="https://www.legisocial.fr/reperes-sociaux/montant-smic-2026-taux-horaire-net-brut.html"
# nouvelle mesure annoncée le 8 octobre 2026
if not any(m['id']=='jeunes_parents' for m in C['philippe']['measures']):
    C['philippe']['measures'].append({"id":"jeunes_parents","theme":"fiscalite","title":"Zéro impôt pour les jeunes parents","proposal":"Pas d'impôt sur le revenu pendant 3 ans pour les jeunes parents des classes moyennes.","claimed":"3 Md€/an","claimed_md":-3,
      "estimates":[{"source":"Site de campagne (L'Heure de vérité)","year":2026,"value":"Coût annoncé : 3 Md€ par an","low_md":-3,"high_md":-3,"url":"https://www.edouardphilippe.fr/actualites/trois-principales-annonces-dedouard-philippe-a-lheure-de-verite"}],
      "consensus":"isolé","verdict":"faisable","obstacle":"Par la loi de finances ; plafond de revenus « classes moyennes » non précisé, coût non vérifié indépendamment.",
      "claude":{"id":"jeunes_parents","central":-3,"low":-4.5,"high":-2,"method":"camp","formula":"Seul chiffrage disponible : 3 Md€/an (camp) ; fourchette ±50 % faute de plafond de revenus publié","inputs":[{"label":"Coût annoncé","value":"3 Md€/an","source":"Édouard Philippe","url":"https://www.edouardphilippe.fr/actualites/trois-principales-annonces-dedouard-philippe-a-lheure-de-verite"}],"note":"Aucun chiffrage indépendant publié"}})
m=M('philippe','heures_sup'); m['proposal']="Heures au-delà de 35 h défiscalisées, plus aucune cotisation au-delà de 37 h ; durée du travail fixée par accord."
# --- statu quo retraite, contexte
D['statu_quo']['retraite']['taux_plein']=67
D['statu_quo']['retraite']['url']="https://manouvellevie.groupama.fr/s-informer-retraite/tout-savoir-age-depart-retraite/suspension-reforme-des-retraites-beneficiaires"
D['context'][2]={"v":"≈ 5 %","l":"taux d'emprunt à 10 ans, plus haut depuis 2002 (oct. 2026)"}
WEAK=['francebudget.fr','dettedelafrance.fr','votons-2027.fr','moicombien.fr','elyseescope.com','lessentieldeleco.fr','revueconflits.com','renseignementeconomique.fr','planetegrandesecoles.com','patrimoine-magazine.eu','algerie360.com','info.fr/','economiematin.fr','monvote2027','politograph','wikiglucksmann']
D['weak_domains']=WEAK
# --- review 2 : verdicts et cohérence
M('glucksmann','smic')['verdict']='faisable'
M('glucksmann','smic')['obstacle']="Un décret suffit ; coût des allègements de cotisations et effet sur l'emploi peu qualifié."
M('melenchon','fiscalite')['verdict']='tres_difficile'
m=M('lisnard','allocation'); m['proposal']="Allocation sociale unique plafonnée à un pourcentage du SMIC (non précisé)."
m=M('lisnard','ame'); m['verdict']='bloque'; m['proposal']="AME remplacée par une aide d'urgence ; titres de séjour divisés par 8 ; aides non contributives réservées aux résidents de plus de 5 ans."
m['obstacle']="Chemin : révision de la Constitution (égalité devant les aides, censurée en 2024) et renégociation de la CEDH et du droit de l'UE."
k=M('le-pen','immigration')['claude']; k.update(central=8.3,low=2.6,high=15,formula="Si la mesure passe : allocations familiales 3,8 + RSA 2,6 + asile 1,2 + AME 0,7 = 8,3 Md€ (Montaigne) ; borne basse 2,6 (variante restreinte), haute 15 (montant 2027 du RN)",note="Même règle que pour Zemmour : comptée si elle passe ; bloquée en l'état du droit (voir le total « si les révisions sont bloquées »)")
k=M('lisnard','cotisations')['claude']; k['formula']=k['formula'].replace('.',',',1) if False else k['formula']
ORD=['le-pen','melenchon','glucksmann','philippe','retailleau','attal','lisnard','zemmour']
D['candidates'].sort(key=lambda c:ORD.index(c['id']))
# --- simulateur : cohérence avec le chiffrage
sl=C['lisnard']['sim']['salaire_net']; sl.update(promised_md=120, measure='cotisations', note="Baisse des cotisations : +400 €/mois promis à terme pour un salaire moyen (2 733 €), au prorata du revenu")
sr=C['retailleau']['sim']; sr['alloc_familiales']=None
sr['famille']="« Revenu familial » de 240 € par enfant dès le 1er enfant, qui remplace 12 aides familiales : le gain ou la perte dépend des aides que vous touchez aujourd'hui ; non chiffré ici."
sr.pop('minima_cut',None)  # « −30 % » sans source : remplacé par le plafond publié (review 5)
C['melenchon']['sim']['jeunes_alloc']={"montant":1337,"label":"Garantie d'autonomie jusqu'à 1 337 €/mois (18-25 ans en formation, sous conditions)"}
C['philippe']['sim']['alloc_familiales']={"unique":350,"degress_above":3000,"degress_factor":0.5,"note":"Allocation unique de 350 €/mois dès le 1er enfant ; moitié supposée au-delà de 3 000 € net (dégressivité non publiée, même hypothèse que notre chiffrage)"}
C['le-pen']['sim'].pop('ir_exempt_under',None)
C['le-pen']['sim']['jeunes']="Moins de 30 ans exonérés d'impôt sur le revenu : mesure de 2022, non reconfirmée en 2026, donc non comptée ici."
C['le-pen']['sim']['minima_sociaux']="Prestations réindexées ; minimum vieillesse à 1 000 €/mois (il est déjà de 1 043,59 € en 2026) ; aides de solidarité réservées en priorité aux Français."
C['philippe']['sim']['overtime']={"label":"2 h sup par semaine exonérées (chiffre du camp : ≈1 000 €/an au SMIC)","annual_at_smic":1000}
C['retailleau']['sim']['overtime']={"label":"2 h sup par semaine exonérées (même base que Philippe, faute de chiffre comparable)","annual_at_smic":1000}
C['attal']['sim']['gel_pct']=1.8; C['attal']['sim']['gel_min']=1200; C['attal']['sim']['gel_status']=['retraite','minima']
C['attal']['sim']['gel_note']="Pensions et prestations non revalorisées en 2028 (inflation prévue 1,8 %) ; petites retraites épargnées, seuil supposé à 1 200 € (non publié)"
C['lisnard']['sim']['minima_sociaux']="Allocation sociale unique plafonnée à un pourcentage du SMIC : baisse possible, non chiffrée ici car le plafond n'est pas publié."

# --- review 3 : chiffres et neutralité (relecture indépendante du 26/10/2026)
def SET(cid,mid,c,l,h,f=None,**kw):
    m=M(cid,mid); k=m['claude']; k.update(central=c,low=l,high=h)
    if f: k['formula']=f
    for a,v in kw.items():
        if a in ('verdict','obstacle','proposal','claimed','a_confirmer','title'): m[a]=v
        else: k[a]=v
R62="Retour à 62 ans en 2030 : 11,8 Md€, valeur commune à tous (rendement de la réforme 2023 en 2030 : 13,6 Md€, médiane Montaigne 11,8 / CNAV 13,6 / étude d'impact 14,1 ; moins 1,8 Md€ déjà perdus par la suspension votée en 2025)"
SET('le-pen','retraites',-15.8,-38.2,-12.2,R62+" ; + départ à 60 ans des carrières précoces ≈ 4 Md€ (iFRAP) ; total ≈ −15,8",method='ascendant')
SET('melenchon','retraites',-32.2,-56.2,-11.8,R62+" ; passage à 60 ans « plus tard dans le mandat » : moitié du surcoût en 2030 (50 à 58 Md€ à pleine charge), ≈ 20,4 ; total ≈ −32,2")
SET('glucksmann','retraites',-11.8,-12.3,-8.6,R62)
SET('lisnard','retraites',5.8,1.8,8.8,"Fin de la suspension ≈ +1,8 Md€ + 64 → 65 ans ≈ 6,8 Md€ par année d'âge, montée en charge partielle en 2030 (≈ +4) = +5,8 Md€ (même base que Philippe et Zemmour)")
# règle : paramètre clé non publié → non chiffrable, fourchette indicative en note
for cid,mid,note in [('attal','retraites',"Fourchette indicative : de −11,8 (retour de fait à 62 ans) à 0 (décotes neutres) ; paramètres non publiés"),
                     ('glucksmann','ecole',"Indicatif : +10 % de salaire des enseignants ≈ 3,3 Md€ ; ampleur non publiée"),
                     ('glucksmann','ukraine',"Indicatif : doubler l'aide de 2024 ≈ 3 Md€, en partie financés par les avoirs russes ; ampleur non publiée"),
                     ('melenchon','niches',"Indicatif : les trois niches pèsent ≈ 20 Md€ ; taux de rabot non publié"),
                     ('lisnard','fonction',"Indicatif : 1 départ sur 3 non remplacé ≈ +4,9 Md€, agences ≈ +1 ; proportion non publiée"),
                     ('lisnard','allocation',"Indicatif : +12 à +34 Md€ selon le plafond (scénarios iFRAP) ; plafond non publié")]:
    k=M(cid,mid)['claude']; k.update(central=0,low=0,high=0,nc=True,note=note)
k=M('retailleau','travail')['claude']; k['note']="Indicatif : +12 à +34 Md€ selon le plafond (scénarios iFRAP) ; même règle que pour Lisnard"
ident=5.8+0.7
SET('lisnard','cotisations',-round(0.6*ident,1),-48,-2,f"Règle du candidat : 60 % des économies rendues. Économies chiffrables à ce jour : {str(ident).replace('.',',')} Md€ (retraites, AME) → −{str(round(0.6*ident,1)).replace('.',',')} Md€ ; borne basse : 48 Md€ promis dès l'an 1",note="Le gain de 400 €/mois n'est atteint que si les 200 Md€ d'économies sont réalisés")
# SMIC : règle proportionnelle appliquée exactement
SET('melenchon','smic',-21.6,-23.9,-19.4,"Base SMIC juin 2026 (1 477,93 € net) : 1 700 € = +15,0 % ; Montaigne ≈ 19 Md€ pour +13,2 % → 19 × 15,0/13,2 ≈ −21,6 Md€",obstacle="Un décret suffit ; coût des allègements de cotisations et effet sur l'emploi peu qualifié.")
SET('glucksmann','smic',-11.9,-13.1,-10.6,"Base SMIC juin 2026 (1 477,93 € net) : 1 600 € = +8,3 % ; Montaigne ≈ 19 Md€ pour +13,2 % → 19 × 8,3/13,2 ≈ −11,9 Md€")
SET('melenchon','point_indice',-20.7,-22,-17,"+1 % de point d'indice = 2,07 Md€ ; +10 % (publié) ≈ −20,7 Md€ ; le camp annonce 17 Md€")
SET('retailleau','production',-12,-18,-10,"Détail du camp : C3S 5,3 + forfait social 2,8 + CFE industrielle 1,9 = 10 ; + heures sup sans cotisations ≈ 2 (même valeur que Philippe) ≈ −12 Md€ (CVAE retirée : déjà supprimée par la loi)")
SET('retailleau','energie',1.0,0,3,"Hausse évitée du soutien aux ENR ≈ 1 Md€/an sur 2028-2030")
# enseignants : 3,3 Md€ par +10 %, montée en charge 70 %
SET('philippe','profs',-4.6,-6.6,-2.3,"+10 % = 3,3 Md€ (Montaigne) ; +20 % = 6,6 Md€ ; 70 % en vigueur en 2030 (règle commune) = −4,6")
def ADD(cid,m): 
    if not any(x['id']==m['id'] for x in C[cid]['measures']): C[cid]['measures'].append(m)
PROF_IN=[{"label":"+10 % pour tous les enseignants","value":"≈3,3 Md€/an","source":"Institut Montaigne","url":"https://www.institutmontaigne.org/presidentielle-2022/legislatives-2022/ensemble/revaloriser-les-salaires-des-enseignants-de-10"}]
ADD('lisnard',{"id":"profs","theme":"social","title":"Enseignants +20 %","proposal":"Hausse de 20 % des salaires des enseignants en cinq ans, en échange d'une réorganisation.","claimed":"Non chiffré","claimed_md":None,
  "estimates":[{"source":"Institut Montaigne (+10 %)","year":2022,"value":"+10 % = 3,3 Md€/an","low_md":-3.3,"high_md":-3.3,"url":PROF_IN[0]['url']}],"consensus":"isolé","verdict":"sous_conditions","obstacle":"Financement lié aux économies du plan, non identifiées.",
  "claude":{"id":"profs","central":-4.6,"low":-6.6,"high":-2.3,"method":"ascendant","formula":"+20 % = 6,6 Md€ ; 70 % en vigueur en 2030 (règle commune) = −4,6","inputs":PROF_IN}})
ADD('attal',{"id":"profs","theme":"social","title":"Enseignants +200 à 500 €","proposal":"+200 € net par mois pour les enseignants, jusqu'à 500 € en milieu de carrière.","claimed":"2,5 Md€","claimed_md":-2.5,
  "estimates":[{"source":"La Gazette (équipe Attal)","year":2026,"value":"Coût annoncé : 2,5 Md€","low_md":-2.5,"high_md":-2.5,"url":"https://www.lagazettefrance.fr/article/attal-assume-de-vouloir-augmenter-le-salaire-des-enseignants-via-d-autres-economies-notamment-sur-le-social"}],"consensus":"isolé","verdict":"faisable","obstacle":"Par la loi de finances ; financement par d'autres économies, notamment sociales.",
  "claude":{"id":"profs","central":-2.5,"low":-4,"high":-1.6,"method":"camp","formula":"Seul chiffrage : 2,5 Md€ (équipe du candidat) ; borne basse ≈ 4 Md€ si les 500 € concernent une large part des enseignants","inputs":PROF_IN}})
# immigration : comptée si elle passe, AME séparée (loi ordinaire)
R35="montée en charge : 3,5/15 du cumulé (règle commune, 70 % en 2030)"
SET('retailleau','retraites',2.8,0,9.8,f"Décote : 12 Md€ cumulés sur 5 ans, {R35} → +2,8 Md€ en 2030 ; plan complet 42 Md€ → 9,8 au maximum")
SET('retailleau','immigration',1.6,0,1.6,f"10 Md€ cumulés, {R35} ≈ 2,3 en 2030, comptés si la mesure passe (même règle que Le Pen et Zemmour), dont AME 0,7 comptée à part → 1,6")
SET('le-pen','immigration',7.6,1.9,14.3,"Si la mesure passe : allocations familiales 3,8 + RSA 2,6 + asile 1,2 = 7,6 Md€ (Montaigne) ; AME comptée à part ; bornes 1,9 et 14,3 (montant 2027 du RN, hors AME)")
AME_IN=[{"label":"Crédits AME 2026","value":"1,21 Md€","source":"Public Sénat","url":"https://www.publicsenat.fr/actualites/sante/budget-2026-le-senat-durcit-l-aide-medicale-d-etat"}]
for cid in ('le-pen','retailleau'):
    ADD(cid,{"id":"ame","theme":"immigration","title":"AME remplacée par une aide d'urgence","proposal":"Remplacer l'aide médicale d'État par une aide médicale d'urgence.","claimed":"Inclus dans le volet immigration","claimed_md":None,
      "estimates":[{"source":"Institut Montaigne","year":2024,"value":"≈0,7 Md€/an","low_md":0.7,"high_md":0.7,"url":"https://www.institutmontaigne.org/legislatives-2024/rassemblement-national/synthese"}],"consensus":"concordant","verdict":"sous_conditions","obstacle":"Une loi suffit ; report de dépenses vers l'hôpital (soins urgents).",
      "claude":{"id":"ame","central":0.7,"low":0.6,"high":1.2,"method":"mediane","formula":"Montaigne ≈ 0,7 Md€ ; plafond = crédits totaux de l'AME (≈1,2)","inputs":AME_IN}})
m=M('lisnard','ame'); m.update(title="AME remplacée par une aide d'urgence",proposal="Remplacer l'aide médicale d'État par une aide médicale d'urgence.",verdict='sous_conditions',obstacle="Une loi suffit ; report de dépenses vers l'hôpital (soins urgents).")
m['claude'].update(formula="Montaigne ≈ 0,7 Md€ ; plafond = crédits totaux de l'AME (≈1,2)",inputs=AME_IN)
ADD('lisnard',{"id":"aides5","theme":"immigration","title":"Aides après 5 ans de résidence","proposal":"Titres de séjour divisés par 8 ; aides non contributives réservées aux résidents de plus de 5 ans.","claimed":"Non chiffré","claimed_md":None,"estimates":[],"consensus":"isolé","verdict":"bloque",
  "obstacle":"Chemin : révision de la Constitution (égalité devant les aides, censurée en 2024) et renégociation de la CEDH et du droit de l'UE.","claude":{"id":"aides5","central":0,"low":0,"high":0,"method":"nc","formula":"Non chiffrable : publics et seuils non précisés","inputs":[],"nc":True}})
SET('attal','annee_blanche',5.0,1.8,6.0,"Chiffrages 2026 (3,6 et 4,3 Md€ pour ≈1,3 % d'inflation) rapportés à 1,8 % d'inflation ≈ +5 Md€ ; 1,8 si la plupart des pensions sont exemptées")
SET('glucksmann','heritages',-3.6,-8,0,"Recette : médiane des chiffrages indépendants 7 ; 9 ; 13,8 ; 19 = 11,4 Md€ (le chiffre du camp n'entre pas dans la médiane) − 15 Md€ de baisse de CSG promise = −3,6 Md€")
m=M('le-pen','tva'); m['verdict']='tres_difficile'; m['obstacle']="Électricité : possible par la loi. Gaz, fioul et carburants : la directive 2022/542 interdit les taux réduits sur les énergies fossiles à partir de 2030 ; il faudrait l'unanimité des 27 pour la changer."
ADD('le-pen',{"id":"enr","theme":"energie","title":"Fin des subventions aux renouvelables","proposal":"Supprimer les subventions aux énergies renouvelables, arrêter l'éolien.","claimed":"5 Md€ dès la 1re année","claimed_md":5,
  "estimates":[{"source":"Planète Grandes Écoles (contre-budget RN)","year":2026,"value":"5 Md€ annoncés","low_md":5,"high_md":5,"url":"https://www.planetegrandesecoles.com/budget-marine-le-pen-2027-mesures-contre-budget-rn"}],"consensus":"isolé","verdict":"sous_conditions","obstacle":"Contrats signés maintenus ; seuls les nouveaux soutiens peuvent être arrêtés.",
  "claude":{"id":"enr","central":1.0,"low":0,"high":3,"method":"ascendant","formula":"Même règle que Retailleau : hausse évitée du soutien aux ENR ≈ 1 Md€/an en 2030, les contrats signés étant maintenus","inputs":[]}})
for cid,mid,ob in [('philippe','immigration',"Chemin : le moratoire sur le regroupement familial exige une révision de la Constitution (Préambule de 1946) et une renégociation de la directive 2003/86 ; le reste relève de la loi."),
                   ('attal','immigration',"Chemin : des quotas votés par le Parlement ont été censurés (décision 2023-863 DC) ; il faut réviser la Constitution, et un accord européen pour Schengen."),
                   ('retailleau','securite',"Chemin : inscrire des peines minimales dans un « pacte constitutionnel » suppose une révision de la Constitution (individualisation des peines).")]:
    m=M(cid,mid); m['verdict']='bloque'; m['obstacle']=ob
# ton : même formulation pour une même situation
M('melenchon','jeunes')['obstacle']="15,5 Md€ selon notre calcul, contre 9,5 Md€ annoncés ; une seule source indépendante."
for cid,mid in [('lisnard','depense'),('retailleau','travail')]:
    m=M(cid,mid); m['obstacle']=m['obstacle'].replace(' ; effet récessif','').replace(', effet récessif','').replace(' ; forte contestation probable','').replace(', forte contestation probable','')
C['le-pen']['total']['independent']=C['le-pen']['total']['independent'].replace('seulement ','')
for cid in ('glucksmann','lisnard','melenchon'): C[cid]['total']['low_md']=None; C[cid]['total']['high_md']=None
# mesures annoncées non chiffrées : listées
ADDM={'le-pen':"exonération des hausses de salaire jusqu'à 10 %, impôt sur la fortune financière à la place de l'IFI, donations tous les 10 ans, prêt à taux zéro à la place de MaPrimeRénov'",
 'melenchon':"pension minimale au niveau du SMIC, indexation des pensions sur les salaires, APL +10 %, minimum vieillesse au seuil de pauvreté, abrogation des réformes de l'assurance chômage",
 'glucksmann':"leasing social d'un million de voitures (≈6 Md€ selon le camp)",
 'philippe':"réduction d'impôt à la naissance, deux jours de carence",
 'lisnard':"TVA unique à 25 %, 20 000 places de prison",
 'retailleau':"baisses d'impôts des ménages (21 Md€ cumulés selon le camp), intérêts d'emprunt déductibles"}
for cid,txt in ADDM.items():
    t0=C[cid]['claude_total']; t0['missing']=(t0.get('missing','')+', '+txt).strip(', ')
# --- review 4 : liens morts, sources et formulations (27/10/2026)
FIG="https://www.ofce.sciences-po.fr/pdf-articles/actu/Le-Figaroel.pdf"
URLFIX={
 "https://place-publique.eu/wp-content/uploads/2025/06/20250623_Projet_placepublique_acte1_BAT_BaDef.pdf":"https://place-publique.eu/document/6J8wjk3EW8dBCLwKxa7J96/projet-placepublique-acte1.pdf",
 "https://www.publicsenat.fr/actualites/sante/budget-2026-le-senat-durcit-l-aide-medicale-d-etat":"https://www.publicsenat.fr/actualites/sante/budget-2026-le-senat-durcit-les-conditions-de-laide-medicale-detat-et-vote-une-baisse-de-ses-credits-de-200-millions",
 "https://ofce.sciences-po.fr/blog/une-revue-recente-de-la-litterature-sur-les-multiplicateurs-budgetaires-la-taille-compte/?print=pdf":"https://web.archive.org/web/20251007054924/https://www.ofce.sciences-po.fr/blog/une-revue-recente-de-la-litterature-sur-les-multiplicateurs-budgetaires-la-taille-compte/",
}
USED=set()
def fix_urls(o):
    if isinstance(o,dict):
        if o.get('url') in URLFIX:
            USED.add(o['url']); o['url']=URLFIX[o['url']]
            if 'web.archive.org' in o['url']: o['source']=o.get('source','')+' (copie archivée)'
        for v in o.values(): fix_urls(v)
    elif isinstance(o,list):
        for v in o: fix_urls(v)
fix_urls(D)
assert USED==set(URLFIX), f"URLFIX sans effet : {set(URLFIX)-USED}"
# Mélenchon, point d'indice : la coupure de presse archivée par l'OFCE n'existe plus ; chiffrage OFCE à la place
m=M('melenchon','point_indice')
m['estimates']=[e for e in m['estimates'] if e['url']!=FIG]+[{"source":"OFCE (Geerolf et Plane)","year":2024,"value":"+10 % : ≈ 23 Md€/an, dont 7 Md€ pour les collectivités","low_md":-23,"high_md":-23,"url":"https://www.ofce-legislatives2024.fr/analyses/Indice_FP.html"}]
m['claude'].update(low=-23,note="Le camp chiffre +10 % à 17 Md€, soit ≈ +8 % au coût de la Cour des comptes",formula="+1 % de point d'indice = 2,07 Md€ (Cour des comptes) ; +10 % (publié) ≈ −20,7 Md€ ; fourchette de 17 (camp) à 23 Md€ (OFCE) ; Montaigne 20")
# Mélenchon, blocage des prix : formule fidèle au chiffrage Montaigne (9 à 38 Md€, médiane 24 sur 2022-2024)
m=M('melenchon','prix'); MP="https://www.institutmontaigne.org/legislatives-2024/nouveau-front-populaire/bloquer-les-prix-des-produits-de-premiere-necessite/"
for e in m['estimates']:
    if e['source'].startswith('Institut Montaigne'): e.update(value="9 à 38 Md€/an selon les prix de l'énergie, médiane 24 (moyenne des boucliers 2022-2024) ; sans compensation aux producteurs et distributeurs, « neutre pour les finances publiques »",low_md=-38,high_md=-9,url=MP)
k=m['claude']; k['inputs']=[i for i in k['inputs'] if i['url']!=FIG]
for i in k['inputs']:
    if i['source']=='Institut Montaigne': i.update(label="Blocage des prix de l'énergie, prix en baisse",value="9 Md€/an",url=MP)
k['inputs'].append({"label":"Blocage des prix de l'énergie, médiane 2022-2024","value":"24 Md€/an","source":"Institut Montaigne","url":MP})
k['formula']="Institut Montaigne (mesure NFP, 2024) : 9 à 38 Md€/an selon les prix de l'énergie, médiane 24 = moyenne des boucliers 2022-2024 ; retenu : 9 Md€, hypothèse de prix de l'énergie en baisse ; borne basse : la médiane de crise (24)"
# Retailleau : formulation neutre
k=M('retailleau','production')['claude']
assert k.get('note','').startswith('Incohérence interne du camp'); k['note']="Chiffres du camp différents selon les documents (51 Md€ cumulés contre 40 Md€ par an)"
# Attal, retraites : borne de retour à 62 ans = valeur commune
k=M('attal','retraites')['claude']; assert "retour à 62 ans (−14,1)" in k['formula']; k['formula']=k['formula'].replace("retour à 62 ans (−14,1)","retour à 62 ans (−11,8, valeur commune)")
# sources primaires pour les trois mesures qui ne reposaient que sur des sources faibles
CRE={"label":"Soutien aux ENR électriques (métropole)","value":"7,29 Md€ (2026) → 8,38 Md€ (2027), ≈ +1 Md€/an","source":"CRE, délibération n° 2026-149","url":"https://www.cre.fr/fileadmin/Documents/Deliberations/2026/260715_2026-149_CSPE_2026-2027.pdf"}
for cid,mid in (('le-pen','enr'),('retailleau','energie')):
    k=M(cid,mid)['claude']; k['inputs']=k.get('inputs',[])+[CRE]
m=M('le-pen','enr')
m['estimates']=[{"source":"Contre-budget 2027 du RN (Vert)","year":2026,"value":"Plus de 5 Md€ dès la 1re année : fin des subventions, moratoire sur les nouveaux projets, surtaxe sur l'éolien","low_md":5,"high_md":5,"url":"https://vert.eco/chaleurs-actuelles/marine-le-pen-presente-le-contre-budget-du-rn-pour-2027-une-attaque-contre-les-renouvelables-et-les-agences-environnementales/"},
 {"source":"Contre-budget 2026 du RN","year":2025,"value":"Fin des tarifs de rachat des énergies intermittentes : 7,2 Md€ en 2026","low_md":7.2,"high_md":7.2,"url":"https://rassemblementnational.fr/documents/GRN-CONTRE-BUDGET-2026.pdf"}]
m['claude']['note']="Les 7,2 Md€ du contre-budget 2026 ≈ tout le soutien 2026 aux ENR électriques en métropole (7,29 Md€, CRE), contrats en cours compris"
m=M('glucksmann','ukraine'); PP="https://place-publique.eu/document/6J8wjk3EW8dBCLwKxa7J96/projet-placepublique-acte1.pdf"
m['proposal']="Augmenter « drastiquement » l'aide militaire à l'Ukraine ; financement par la saisie des avoirs russes gelés proposé en 2025, non repris dans le programme."
m['obstacle']="Saisie des avoirs russes non décidée : faute d'accord, notamment avec la Belgique où Euroclear détient l'essentiel des avoirs, l'UE a choisi en décembre 2025 un prêt de 90 Md€ financé par emprunt commun."
m['estimates']=[{"source":"Place publique, projet « Acte I »","year":2025,"value":"« Augmenter drastiquement l'aide militaire à l'Ukraine » ; montant non précisé","low_md":None,"high_md":None,"url":PP},
 {"source":"R. Glucksmann, lettre « Cap clair »","year":2025,"value":"Armes européennes « drastiquement » augmentées ; saisir les 200 Md€ d'avoirs russes gelés","low_md":None,"high_md":None,"url":"https://raphaelglucksmann.kessel.media/posts/pst_bde552542ce94673b5d60ad3fd1e33c3/je-vous-ecris-dukraine-la-ou-se-joue-lavenir-de-leurope"},
 {"source":"Toute l'Europe","year":2025,"value":"Pas d'accord sur un prêt adossé aux avoirs ; prêt de 90 Md€ à taux zéro par emprunt commun pour 2026-2027","low_md":None,"high_md":None,"url":"https://www.touteleurope.eu/l-ue-dans-le-monde/faute-d-accord-sur-les-avoirs-russes-les-vingt-sept-debloquent-un-pret-de-90-milliards-d-euros-pour-l-ukraine/"}]
m['claude'].update(formula="Non chiffrable : ampleur de la hausse non publiée ; pour ordre de grandeur, doubler les livraisons françaises de 2025 ≈ −0,9 Md€",
 note="Indicatif : matériels livrés 0,86 Md€ en 2024 et 0,94 Md€ en 2025, soutien militaire total 6,5 Md€ de 2022 à 2025 (ministère des Armées) ; l'accord de février 2024 prévoyait « jusqu'à 3 Md€ » pour 2024",
 inputs=[{"label":"Matériels livrés à l'Ukraine ; soutien militaire 2022-2025","value":"0,86 Md€ (2024), 0,94 Md€ (2025) ; 6,5 Md€ au total","source":"Ministère des Armées, rapport au Parlement 2026","url":"https://www.defense.gouv.fr/sites/default/files/ministere-armees/Rapport%20au%20Parlement%202026%20sur%20les%20exportations%20d%E2%80%99armement%20de%20la%20France%20(12082026).pdf"},
 {"label":"Accord de sécurité France-Ukraine","value":"Jusqu'à 3 Md€ d'aide militaire supplémentaire en 2024","source":"Élysée","url":"https://www.elysee.fr/emmanuel-macron/2024/02/16/visite-de-volodymyr-zelensky-president-de-lukraine"}])
m=M('attal','travail')
m['proposal']="Supprimer le contingent annuel d'heures supplémentaires (220 h par salarié à défaut d'accord) et réformer l'assurance chômage pour inciter au travail."
m['estimates']=[{"source":"attalpresident.fr, travail et salaires","year":2026,"value":"Fin du plafond d'heures sup ; réforme de l'assurance chômage : +100 000 emplois, sans chiffrage en euros","low_md":None,"high_md":None,"url":"https://attalpresident.fr/programme/travail-salaires"},
 {"source":"Proposition de loi n° 1791 (cosignée par G. Attal)","year":2025,"value":"Affiliation 8 mois sur 20, durée maximale 15 mois : 3,6 Md€ d'économies (estimation 2024)","low_md":3.6,"high_md":3.6,"url":"https://www.assemblee-nationale.fr/dyn/17/textes/l17b1791_proposition-loi.pdf"}]
m['claude'].update(note="Indicatif : si la réforme reprend la proposition de loi de 2025, ≈ +3,6 Md€ ; le programme n'en donne pas les paramètres. Au-delà de 220 h, les heures sup sont déjà possibles avec un repos compensateur",
 inputs=[{"label":"Contingent annuel d'heures supplémentaires","value":"220 h par salarié à défaut d'accord","source":"Service-public.fr","url":"https://www.service-public.gouv.fr/particuliers/vosdroits/F2391"}])
# --- review 5 : simulateur, pertes et gains manquants (27/10/2026)
SQ=D['statu_quo']
SQ['carence_public']=1; SQ['carence_url']="https://www.service-public.gouv.fr/particuliers/vosdroits/F13861"
SQ['chomage_mois']=18; SQ['chomage_url']="https://www.service-public.gouv.fr/particuliers/vosdroits/F14860"
SQ['courses_url']="https://www.insee.fr/fr/statistiques/5370353"
SQ['rsa_etrangers_url']="https://www.service-public.gouv.fr/particuliers/vosdroits/F19778"
# aides réservées : même règle de calcul pour les quatre candidats qui en proposent (perte des allocations familiales et des minima selon la condition propre à chacun)
for cid,rule in (('le-pen',{"af":"nonfr","minima":"lt5"}),('zemmour',{"af":"hors","minima":"hors"}),('lisnard',{"af":"lt5","minima":"lt5"}),('retailleau',{"af":"lt5","minima":"lt5"})):
    s=C[cid]['sim']; s.pop('alloc_perte_etrangers',None); s.pop('alloc_perte_scope',None); s['etr']=rule
# enseignants : les hausses chiffrées dans nos totaux apparaissent aussi dans le simulateur
C['lisnard']['sim']['enseignants_pct']=20; C['lisnard']['sim']['enseignants_note']="+20 % en cinq ans, en échange d'une réorganisation des missions"
C['attal']['sim']['enseignants_eur']={"montant":200,"note":"+200 € net par mois, jusqu'à 500 € en milieu de carrière (montant minimal retenu)"}
C['philippe']['sim']['enseignants_note']="+20 % d'ici la fin du mandat"
# TVA supprimée sur les produits de première nécessité (comptée dans le total)
C['le-pen']['sim']['tva_courses']={"part":0.75,"note":"TVA de 5,5 % supprimée sur une centaine de produits de première nécessité, soit environ les trois quarts du panier (notre chiffrage rapporté à la TVA sur l'alimentation à domicile), si la baisse est répercutée"}
# jours de carence des agents publics, durée d'indemnisation du chômage
C['philippe']['sim']['carence_jours']=2; C['retailleau']['sim']['carence_jours']=3; C['zemmour']['sim']['carence_jours']=3
C['philippe']['sim']['chomage_duree']={"mois":12,"avant":50}
# jeunes parents : mesure comptée dans le total (−3 Md€), absente du simulateur
C['philippe']['sim']['ir_jeunes_parents']={"note":"Pas d'impôt sur le revenu pendant 3 ans pour les jeunes parents des classes moyennes","max":2*SQ.get('salaire_moyen',2733)}
# simulateur, review 5 bis : audit indépendant du 27/10/2026
D['asof']='27 octobre 2026'
for k,v in (('smic_url',"https://www.service-public.gouv.fr/particuliers/vosdroits/F2300"),):
    SQ[k]=v
SQ['alloc_familiales']['url']="https://www.service-public.gouv.fr/particuliers/vosdroits/F13213"
SQ['ir']['url_decote']="https://www.service-public.gouv.fr/particuliers/vosdroits/F34328"
SQ['retraite']['url']="https://www.service-public.gouv.fr/particuliers/vosdroits/F14043"
SQ['salaries']=26965000; SQ['salaries_url']="https://www.insee.fr/fr/statistiques/8733039?sommaire=8733125"
# heures sup : seules la CSG et la CRDS restent dues (impôt et cotisations salariales déjà exonérés)
C['philippe']['sim']['overtime']={"label":"Heures sup sans impôt ni cotisation"}
C['retailleau']['sim']['overtime']={"label":"Heures sup sans cotisation (même calcul que Philippe, faute de précision)"}
# jeunes parents : exonération sous 3 000 € d'impôt, réduction de 3 000 € au-delà (source du camp, 8/10/2026)
C['philippe']['sim']['ir_jeunes_parents']={"note":"Pas d'impôt sur le revenu pendant les 3 premières années de l'enfant","plafond":3000}
# allocation unique : 350 € par mois et par enfant, dégressive (source du camp) ; aides fusionnées non déduites
af=C['philippe']['sim']['alloc_familiales']; af['par_enfant']=True
af['note']="Allocation unique de 350 €/mois par enfant dès le 1er enfant ; moitié supposée au-delà de 3 000 € net (dégressivité non publiée) ; les aides qu'elle remplace (supplément familial, prime de naissance…) ne sont pas déduites"
# Retailleau : plafond publié des aides non contributives (70 % du SMIC net par adulte)
C['retailleau']['sim']['plafond_aides']={"pct":0.7,"note":"Total des aides non contributives plafonné à 70 % du SMIC net par adulte (foyer d'un adulte supposé)"}
C['retailleau']['sim']['minima_sociaux']="RSA, prime d'activité et ASS fusionnés, avec 15 h d'activité ; total des aides non contributives plafonné à 70 % du SMIC net par adulte."
C['retailleau']['sim']['tous']=["Fin de MaPrimeRénov' : plus d'aide de l'État pour isoler un logement ou changer de chauffage."]
C['retailleau']['sim']['etr']={"af":"lt5w","minima":"lt5w"}
C['le-pen']['sim']['etr']={"af":"nonfr","minima":"lt5w"}
# Mélenchon : taux publiés (note LFI d'octobre 2026)
C['melenchon']['sim']['fonctionnaires']="Hausse du point d'indice de 10 % ; 10 000 enseignants et 10 000 soignants recrutés."
C['melenchon']['sim']['minima_sociaux']="Toutes les prestations indexées ; allocations familiales et APL +10 % (non comptés dans notre total) ; minimum vieillesse porté au seuil de pauvreté."
C['melenchon']['sim']['carburant']={"prix":1.70,"actuel":2.21,"note":"Prix du carburant bloqué à 1,70 €/l par décret, contre ≈ 2,21 €/l en octobre 2026 (SP95, relevé du ministère) ; blocage de 6 mois au plus par décret"}
C['melenchon']['sim']['patrimoine']=[{"seuil":300000,"effet":"Fin de la flat tax : dividendes et intérêts imposés au barème de l'impôt sur le revenu."}]+C['melenchon']['sim'].get('patrimoine',[])
m=M('melenchon','prix'); m['proposal']="Bloquer les prix de l'alimentation et de l'énergie de base ; carburant ramené à 1,70 €/l par décret."
# Glucksmann : baisse de CSG financée par l'impôt sur les héritages, entièrement comptée dans le total
C['glucksmann']['sim']['salaire_net']={"gain_mensuel":round(15e9/SQ['salaries']/12,1),"ref":SQ.get('salaire_moyen',2733),"prorata":True,"sans_plafond":True,"public":"salariés",
 "note":"Baisse de la CSG sur les salaires : 15 Md€ répartis au prorata des salaires (27 millions de salariés, Insee), soit ≈ 46 €/mois au salaire moyen (notre calcul)"}
C['glucksmann']['sim'].pop('salaire_note',None)
C['glucksmann']['sim']['service_jeunes']="Service obligatoire de 10 mois : indemnité supposée égale à celle du service civique actuel"
# Attal : 1 000 € à la naissance (compté dans le total)
C['attal']['sim']['bebe']="1 000 € placés par l'État sur un compte retraite à la naissance, bloqués jusqu'à la retraite"
C['attal']['sim']['jeunes']="Réseaux sociaux interdits aux moins de 15 ans."
# Zemmour : jours de carence hors de la mesure chiffrée, donc en note seulement (même règle que les ruptures conventionnelles de Retailleau)
C['zemmour']['sim'].pop('carence_jours',None)
# Le Pen : donations, droit actuel précisé
C['le-pen']['sim']['heritage']=[{"seuil":100000,"effet":"Donations exonérées jusqu'à 100 000 € par enfant tous les 10 ans, contre tous les 15 ans aujourd'hui (version 2024)."}]
# --- review 6 : arbitrages tranchés par les règles communes et les faits (27/10/2026), relus par une relecture indépendante
# Philippe, allocation unique : 350 € par enfant (source du camp), dégressivité et aides fusionnées non publiées
# → paramètre clé non publié : non chiffrable, fourchette indicative en note (même règle que l'allocation unique de Lisnard)
PHI="https://www.edouardphilippe.fr/actualites/trois-principales-annonces-dedouard-philippe-a-lheure-de-verite"
SET('philippe','famille',0,0,0,"Non chiffrable : 350 € par mois et par enfant, dégressifs selon le revenu (seuils non publiés), « à coût constant » en fusionnant des aides existantes (liste non complète)",
    note="Indicatif : de 0 (coût constant annoncé par le camp) à environ −17,5 Md€ : 350 € par enfant pour les familles d'un et deux enfants (3,58 M × 4 200 € + 3,04 M × (700 − 152 €) × 12, allocations familiales actuelles déduites), divisé par 2 pour la dégressivité (hypothèse) ; familles de 3 enfants et plus et autres aides fusionnées non comptées",
    proposal="350 €/mois par enfant dès le premier enfant, dégressive selon le revenu, à coût constant en fusionnant des aides existantes.")
m=M('philippe','famille'); m['claimed']="À coût constant, selon le camp"
m['claude']['inputs'].append({"label":"Annonce du camp","value":"350 €/mois par enfant, dégressive avec le revenu, à coût constant","source":"Site d'Édouard Philippe (8/10/2026)","url":PHI})
# Retailleau, fusion des minima : le « −30 % » est sourcé (présentation du camp, Public Sénat 7/01/2026) → calcul ascendant
# inchangé (+5,5) ; il recoupe l'objectif du camp (30 Md€ sur 5 ans, chômage compris, ≈ 7 Md€ en 2030 par la règle 3,5/15).
# Le plafond à 70 % du SMIC reste non compté : le seul chiffrage (iFRAP) porte sur un autre dispositif.
PS1="https://www.publicsenat.fr/actualites/politique/la-fete-est-finie-bruno-retailleau-veut-supprimer-les-35-heures-inciter-a-la-reprise-dactivite-et-plafonner-les-aides-sociales-pour-relancer-lemploi"
PS2="https://www.publicsenat.fr/actualites/economie/presidentielle-2027-bruno-retailleau-sengage-sur-un-plan-deconomies-de-pres-de-200-milliards-deuros-sil-est-elu"
k=M('retailleau','travail')['claude']; assert k['central']==5.5 and k['method']=='ascendant'
k['note']="Plafond à 70 % du SMIC non compté : son seul chiffrage (iFRAP, 12 à 34 Md€ selon le plafond) porte sur un autre dispositif, une allocation unique versée en crédit d'impôt qui s'éteint au 8e décile. Objectif du camp : 30 Md€ sur cinq ans pour le chômage et les prestations, soit ≈ 7 Md€ en 2030 selon la règle commune"
k['inputs']+=[{"label":"Allocation fusionnée","value":"−30 %","source":"Public Sénat, présentation du plan (7/01/2026)","url":PS1},
              {"label":"Objectif du camp, chômage et prestations","value":"30 Md€ sur cinq ans","source":"Public Sénat, plan de 197 Md€ (12/10/2026)","url":PS2}]
sr=C['retailleau']['sim']
sr['baisse_minima']={"pct":30,"note":"RSA, prime d'activité et ASS fusionnés et réduits de 30 % (présentation du camp)"}
sr['minima_sociaux']="RSA, prime d'activité et ASS fusionnés et réduits de 30 %, avec 15 h d'activité ; total des aides non contributives plafonné à 70 % du SMIC net par adulte."
# Mélenchon, blocage des prix : médiane des chiffrages publiés, Institut Montaigne (médiane 24 Md€) et Gouvernement (≈ 20 Md€),
# soit 22 ; l'hypothèse basse de 9 Md€ (prix de l'énergie en baisse) est contredite par les prix pétroliers d'octobre 2026
NPG="https://www.ecologie.gouv.fr/sites/default/files/documents/NPG-2026.10.23.pdf"
m=M('melenchon','prix'); k=m['claude']; MONT=k['inputs'][0]['url']; assert 'institutmontaigne' in MONT
k.update(central=-22,low=-38,high=0,method="médiane",formula="Médiane des chiffrages publiés : Institut Montaigne (2024), médiane 24 Md€/an (moyenne des boucliers 2022-2024, « risque budgétaire en cas de résurgence d'une crise énergétique ») et Gouvernement (2024), ≈ 20 Md€/an, soit 22 ; hypothèse basse de 9 Md€ (prix en baisse) écartée, les prix pétroliers d'octobre 2026 étant au niveau de la crise de 2022 (SP95 2,18 €/l, gazole 2,35 €/l, Brent 119 $) ; borne haute 0 si le blocage se fait sans compensation publique",
    note="Carburant à 1,70 €/l par décret (note LFI d'octobre 2026), rangé parmi les dépenses du programme ; prix de l'électricité et du gaz de 2026 non relevés ici")
k['inputs']=[i for i in k['inputs'] if '9 Md€' not in i.get('value','')]+[
    {"label":"Estimation du Gouvernement (2024)","value":"≈ 20 Md€/an","source":"Institut Montaigne, citant le Gouvernement","url":MONT},
    {"label":"Prix à la pompe, semaine du 23 octobre 2026","value":"SP95-E5 2,18 €/l ; gazole 2,35 €/l ; Brent 119 $","source":"Ministère de la Transition écologique, prix et marges des produits pétroliers","url":NPG}]
m['estimates'].append({"source":"Gouvernement (cité par l'Institut Montaigne)","year":2024,"value":"≈ 20 Md€/an","low_md":-20,"high_md":-20,"url":MONT})
cb=C['melenchon']['sim']['carburant']; assert cb['actuel']==2.21
cb.update(actuel=2.18,note="Prix du carburant bloqué à 1,70 €/l par décret, contre 2,18 €/l pour le SP95 la semaine du 23 octobre 2026 (relevé du ministère) ; blocage de 6 mois au plus par décret")
# Le Pen, TVA sur l'énergie : même règle que les héritages de Glucksmann (le chiffre du camp n'entre pas dans la médiane)
# et que pour Mélenchon (chiffrages crédibles seulement : francebudget.fr est classé source faible) → médiane Bercy 16,8 / Montaigne 11,3
k=M('le-pen','tva')['claude']; assert k['central']==-14.5 and k['note'].startswith("Le périmètre")
IDEP=[i['url'] for i in k['inputs'] if 'institut-entreprise' in i['url']][0]
k.update(central=-14.1,low=-16.8,high=-11.3,formula="Médiane des chiffrages indépendants : Bercy 16,8 et Institut Montaigne 11,3 Md€ = 14,1 Md€ (le chiffre du camp, 12,2 Md€, et le simulateur francebudget.fr, 17,4 Md€, source faible, n'entrent pas dans la médiane)")
k['note']+=" ; Bercy et l'Institut Montaigne chiffrent aux prix de 2024 ; le coût « progresse avec les prix » (Institut de l'Entreprise, octobre 2026, Brent au-dessus de 100 $)"
for i in k['inputs']:
    if i['url']==IDEP: i.update(label="Chiffre du camp (contre-budget), repris par l'Institut de l'Entreprise",source="Institut de l'Entreprise (2026)")
# simulateur : plus de gain pour l'allocation de Philippe (mesure non chiffrable), une note à la place
sp=C['philippe']['sim']; sp.pop('alloc_familiales',None)
sp['famille']="Allocation unique de 350 €/mois par enfant dès le 1er enfant, dégressive selon le revenu, en remplacement d'aides existantes : non chiffrable (seuils et aides remplacées non publiés), donc non comptée ici."
# --- quiz : texte en langage courant, appliqué après toutes les corrections (mesures ajoutées comprises)
for c0 in D['candidates']:
    for m in c0['measures']:
        q=m['proposal']
        q=re.sub(r"\s*\([^)]*\)","",q); q=re.sub(r";\s*absente d'Acte I[^.;]*","",q)
        q=q.replace('réforme Borne','réforme de 2023').replace(' ; statut 2027 incertain','')
        m['quiz_text']=q.strip().rstrip(';').strip()
QP=json.load(open('data/quiz_plain.json'))
for c in D['candidates']:
    for m in c['measures']:
        k=c['id']+'.'+m['id']
        if k in QP: m['quiz_text'],m['quiz_concret']=QP[k]
QE={k:v for k,v in json.load(open('data/quiz_effets.json')).items() if not k.startswith('_')}
for c in D['candidates']:
    for m in c['measures']:
        k=c['id']+'.'+m['id']
        if k in QE:
            m['quiz_plus'],m['quiz_moins']=QE[k][0],QE[k][1]
            if len(QE[k])>2: m['quiz_src']=QE[k][2]
assert {k for k in QE if k.count('.')==1}<={c['id']+'.'+m['id'] for c in D['candidates'] for m in c['measures']}, "quiz_effets.json : mesure inconnue"
# (les clés candidat.thème.n sont des propositions « vie quotidienne », reprises par build.py après la fusion du volet)
for c0 in D['candidates']:
    for m in c0['measures']:
        if m.get('quiz_text'): m['quiz_text']=re.sub(r"\s+\.$",".",m['quiz_text']).replace(' .','.')
# --- non chiffrable
for c0 in D['candidates']:
    for m in c0['measures']:
        k=m.get('claude')
        if k and k['central']==0 and k['low']==0 and k['high']==0: k['nc']=True
# --- totaux
def draw(lo,c,hi):
    z=random.gauss(0,1); return c+z*((c-lo)/1.2816 if z<0 else (hi-c)/1.2816)
for c0 in D['candidates']:
    random.seed(c0['id'])  # tirage propre à chaque candidat : modifier une mesure ne déplace pas les fourchettes des autres
    ms=[m for m in c0['measures'] if m.get('claude') and not m['claude'].get('exclude') and not m.get('a_confirmer') and not m['claude'].get('nc')]
    def sim(real):
        xs=sorted(sum(draw(m['claude']['low'],m['claude']['central'],m['claude']['high']) for m in ms if not(real and m['verdict']=='bloque')) for _ in range(20000))
        return round(xs[2000],1),round(xs[18000],1)
    p10,p90=sim(False)
    t=c0['claude_total']
    t.update(sum=round(sum(m['claude']['central'] for m in ms),1),p10=p10,p90=p90,realsum=round(sum(m['claude']['central'] for m in ms if m['verdict']!='bloque'),1),n=len(ms),
      cost=round(sum(m['claude']['central'] for m in ms if m['claude']['central']<0),1),gain=round(sum(m['claude']['central'] for m in ms if m['claude']['central']>0),1),
      confirm=[m['title'] for m in c0['measures'] if m.get('a_confirmer')])
    for kk in ('p50','r10','r50','r90'): t.pop(kk,None)
# --- résumés gabarit
P={'le-pen':("Promet 140 Md€ d'économies nettes d'ici 2032, 30 Md€ de baisses d'impôts, la retraite à 62 ans et la TVA à 5,5 % sur l'énergie.","la priorité nationale et le référendum exigent une révision de la Constitution."),
'melenchon':("Promet la retraite à 60 ans, un SMIC à 1 700 € net et 106 Md€ de recettes nouvelles, surtout sur les hauts patrimoines.","le rendement réel des nouveaux impôts, et les traités européens pour l'annulation de la dette."),
'philippe':("Promet la retraite à 65 ans, un départ sur trois non remplacé dans la fonction publique, une allocation familiale dès le premier enfant et zéro impôt pour les jeunes parents.","l'acceptation d'un nouveau report de l'âge, et le financement de l'allocation familiale unique."),
'glucksmann':("Promet le retour à 62 ans, un SMIC à 1 600 € net, une taxe sur les très gros héritages et une défense européenne financée par emprunt commun.","l'accord des autres pays européens, et le rendement de la taxe sur les héritages."),
'retailleau':("Promet 197 Md€ d'économies cumulées d'ici 2032, un âge minimal de 63 ans, la fusion des aides sociales et un référendum sur l'immigration.","la révision de la Constitution, et des économies sur les agences plus faibles que celles annoncées."),
'attal':("Promet la fin de l'âge légal de départ, 100 000 postes publics en moins, le gel des prestations en 2028 et l'équilibre budgétaire en 2037.","des paramètres non publiés, en particulier pour les retraites."),
'lisnard':("Promet 80 Md€ d'économies la première année puis 200 Md€ par an, dont 60 % rendus en baisses de cotisations.","l'identification des économies : une partie seulement l'est, et la baisse des cotisations en dépend."),
'zemmour':("Promet l'expulsion des étrangers restés un an au chômage, des aides réservées aux Français, 800 000 postes publics en moins et la sortie de la CEDH.","plusieurs mesures exigent une révision de la Constitution et la sortie de la CEDH.")}
MEN=D['statu_quo']['menages']
def fr(x): return (('+' if x>0 else '−' if x<0 else '')+f"{abs(x):.1f}".replace('.',','))
for c0 in D['candidates']:
    t=c0['claude_total']; hh=round(t['sum']*1e9/MEN)
    hs=f"{abs(hh):,}".replace(',',' ')
    c0['promise']=P[c0['id']][0]; c0['obstacle_main']=P[c0['id']][1][0].upper()+P[c0['id']][1][1:]
    c0['summary']=f"{P[c0['id']][0]} Notre chiffrage : {fr(t['sum'])} Md€ par an en 2030, soit {('+' if hh>0 else '−')}{hs} € par ménage. Principal obstacle : {P[c0['id']][1]}"
json.dump(D,open('promesses-2027-data.json','w'),ensure_ascii=False,indent=1)
for c0 in D['candidates']:
    t=c0['claude_total']; print(c0['id'],t['sum'],t['p10'],t['p90'],'n',t['n'],'conf',t['confirm'])
print(D['candidates'][6]['summary'])
