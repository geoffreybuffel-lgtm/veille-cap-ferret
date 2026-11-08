# Relevé de veille (tous les 2 jours)

Le site est publié par GitHub Pages depuis la branche `main` : `index.html` lit `data.json`.
Chaque relevé met `data.json` à jour avec `tools/update.py`, puis pousse sur `main`.

## Étapes

1. Relever les biens à VENDRE sur la presqu'île du Cap Ferret, sur le site propre de chaque agence uniquement (jamais les portails).
   Écrire un CSV par agence dans `releve/` avec l'en-tête exact :
   `agence,titre,type,secteur,prix,surface,chambres,terrain,ref,url,image,f,quartier,date_annonce,statut_annonce`
   - `agence` : exactement le nom de `data.json > agences[].nom`.
   - `type` : V (maison), VP (maison avec piscine), A (appartement), T (terrain).
   - `secteur` : Le Cap Ferret, L'Herbe, La Vigne, Le Canon, Piraillan, Piquey, Claouey, Les Jacquets… (Lège bourg est ignoré).
   - `prix` vide si prix sur demande ; `url` = lien exact de l'annonce (c'est l'identifiant : garder la même forme qu'au relevé précédent).
   - Colonnes facultatives, à remplir pour les NOUVEAUX biens (une lecture de la fiche) :
     `f` = lettres des caractéristiques citées dans l'annonce : P première ligne, B vue bassin, O vue océan, S piscine existante, W maison bois, R à rénover, N neuf/récent, D dépendance (ex. `PSW`) ;
     `quartier` = Mimbeau, 44 Hectares, La Pointe, Les Américains, Horizon, Bélisaire, Triangle d'or, Phare, Grand Piquey, Petit Piquey, Les Vallons (si cité) ;
     `date_annonce` = date de publication affichée sur l'annonce (AAAA-MM-JJ) ; `statut_annonce` = « sous offre » / « sous compromis » si affiché.
   - `image` = URL de la photo principale. Pour un bien déjà connu (même url dans `data.json`), on peut la laisser vide : l'ancienne est gardée.
   Sources (pages liste) :
   - Agence du Cap : API `https://www.agence-cap-ferret.fr/wp-json/wp/v2/properties?per_page=100&page=1&property_status=31` (et page=2), champs `property_meta` (fave_property_price, fave_property_size, fave_property_bedrooms, fave_property_land), photo via `featured_media`.
   - Barnes : `https://www.barnes-international.com/fr/vente/france/lege-cap-ferret.html?page=1..4` et `.../cap-ferret.html?page=1..2` (ne pas utiliser la page sans `?page=`).
   - Première Ligne : `https://agence-premiere-ligne.com/acheter/` (garder la presqu'île seulement).
   - John Taylor : `https://www.john-taylor.fr/vente/agence-immobiliere-de-prestige-cap-ferret-23245/` (exclure Arcachon, Andernos).
   - Christie's (Maxwell-Baynes) : `https://maxwellbaynes.com/for-sale/area/arcachon-atlantic-coast/?page=1..6` (presqu'île seulement).
   - Sotheby's : plan du site `https://www.capferretpylasothebysrealty.com/sitemap_3_fr.xml` (références CF5).
   - Elliman : plans du site de `https://www.elliman.fr` (biens dont l'adresse cite Cap-Ferret, Canon, Herbe, Vigne, Piquey…).
   - Une Villa et des Vignes : `https://www.unevillaetdesvignes.fr/offres?lstlocalisation=3` (toutes les pages, presqu'île seulement).
   - Cabinet Bedin : `https://www.cabinet-bedin.com/agence-immobiliere/cap-ferret?page=1..3` et `.../claouey?page=1..3`.
   - Émile Garcin : `https://www.emilegarcin.com/fr/annonces/vente-immobilier/cap-ferret` (et `.../lege-cap-ferret` si accessible).
   Si un site ne répond pas, ne pas écrire de CSV pour cette agence : ses biens ne seront pas marqués retirés.
2. `python3 tools/update.py releve/ AAAA-MM-JJ` (date du jour, heure de Paris).
3. Vérifier la sortie : si une agence a plus de 30 % de ses biens « retirés » d'un coup, le relevé de cette agence est sans doute incomplet :
   annuler (`git checkout data.json`), refaire le relevé de cette agence, relancer.
4. `git add data.json && git commit -m "Relevé du AAAA-MM-JJ" && git push origin main`. Ne pas commiter `releve/`.

## Rapprochements vérifiés
`data.json > verifications` contient les paires (votre bien, annonce concurrente) vérifiées sur photos : `meme` vrai ou faux.
Ne jamais les supprimer : l'application s'en sert en priorité sur le score automatique.
