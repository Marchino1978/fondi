#!/bin/bash
# Script universale per riallineare e pushare su GitHub

# Vai nella cartella del progetto (relativa allo script stesso)
cd "$(dirname "$0")" || exit 1

# Determina il branch corrente
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "🔄 Pull dal branch remoto: $CURRENT_BRANCH"

# Se ci sono modifiche non committate, le stashiamo per evitare errori
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠️ Modifiche locali trovate, le salvo temporaneamente con git stash"
  git stash --include-untracked
  STASHED=true
fi

# Riallinea con il remoto
git pull origin "$CURRENT_BRANCH" --rebase

# Se avevamo fatto stash, ripristiniamo
if [ "$STASHED" = true ]; then
  echo "🔄 Ripristino modifiche locali dallo stash"
  git stash pop || echo "ℹ️ Nessuna modifica da ripristinare"
fi

# Aggiunge tutte le modifiche (nuovi, modificati, eliminati)
git add --all

# Commit fisso "fix"
git commit -m "fix" || echo "ℹ️ Nessuna modifica da commitare"

# Push sul branch corrente
echo "🚀 Push su branch: $CURRENT_BRANCH"
git push origin "$CURRENT_BRANCH"
