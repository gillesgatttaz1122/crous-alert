# crous-alert

Notification push (ntfy) quand un nouveau logement CROUS apparaît à Paris sur
[trouverunlogement.lescrous.fr](https://trouverunlogement.lescrous.fr).

Un workflow GitHub Actions tourne toutes les 10 minutes, relève les annonces
(`/accommodations/<id>`) de la recherche et envoie une notification pour chaque
nouvelle annonce.

## Mise en place

1. Installer l'app **ntfy** (iOS / Android) et s'abonner à un sujet difficile à
   deviner (ex. `crous-xxxx-8f3k2`) — les sujets ntfy sont publics.
2. Settings → Secrets and variables → Actions → **Secrets** : ajouter
   `NTFY_TOPIC` avec ce nom de sujet.
3. Toujours dans **Secrets** : `MSE_LOGIN` (adresse courriel) et `MSE_PASSWORD`
   du compte MesServices.etudiant.gouv.fr. Sans connexion, le site n'affiche
   qu'une partie des logements (≈ 50 au lieu de 360 sur toute la France). Le
   script se connecte à chaque passage et résout lui-même la case « Je ne suis
   pas un robot » (ALTCHA, un simple calcul). Si la connexion échoue, une
   notification « connexion impossible » est envoyée.
4. (Optionnel) onglet **Variables** : `CROUS_URL` = l'URL d'une recherche faite
   sur le site, pour remplacer la zone Paris par défaut.
5. Onglet Actions → « Alerte logement CROUS » → **Run workflow**. Tu dois
   recevoir « Alerte CROUS active » avec le nombre de logements en ligne.
