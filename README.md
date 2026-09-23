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
3. (Optionnel) onglet **Variables** : `CROUS_URL` = l'URL d'une recherche faite
   sur le site, pour remplacer la zone Paris par défaut.
4. Onglet Actions → « Alerte logement CROUS » → **Run workflow**. Tu dois
   recevoir « Alerte CROUS active » avec le nombre de logements en ligne.
