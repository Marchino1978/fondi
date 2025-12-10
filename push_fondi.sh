#!/bin/bash
# Script completo per push su GitHub

# Vai nella cartella del progetto (relativa allo script stesso)
cd "$(dirname "$0")" || exit 1

# Aggiunge tutte le modifiche (nuovi, modificati, eliminati)
git add --all

# Crea il commit con messaggio fisso o timestamp
git commit -m "fix" || echo "Nessuna modifica da commitare"

# Determina il branch corrente
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Fa il push sul branch corrente
echo "🚀 Push su branch: $CURRENT_BRANCH"
git push origin "$CURRENT_BRANCH"
