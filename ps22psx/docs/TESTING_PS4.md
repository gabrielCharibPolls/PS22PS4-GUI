# Tester sur PS4 jailbreakée

PS22PSX produit uniquement des **fPKG PS4 Classics**.

## Build (Mac)

```bash
ps22psx create game.iso \
  --emulator bin/emulators/ps2emu.pkg \
  --icon cover.png --background back.png \
  --output out
```

## Install PS4

1. Copier le `.pkg` sur USB (exFAT).
2. Sur PS4 jailbreakée : **Debug Settings → Package Installer**.
3. Lancer le jeu depuis la bibliothèque.
4. Si bugs : ajouter config/LUA (`ps22psx config` / `ps22psx lua`) puis rebuild.

## Sans console PS4

On peut quand même valider sur Mac :

- `ps22psx doctor` → toolchain OK  
- `ps22psx info jeu.iso` → title id  
- `ps22psx create …` → fichier `.pkg` généré  

L’install / gameplay réelle nécessite une **PS4 jailbreakée**.

## Compatibilité

https://www.psdevwiki.com/ps4/PS2_Classics_Emulator_Compatibility_List
