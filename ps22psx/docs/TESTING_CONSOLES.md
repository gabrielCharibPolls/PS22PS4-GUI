# Tester sur PS4 jailbreakée et PS5 exploitée

Les fPKG produits sont des **PS4 PS2 Classics** packages.  
Ils s’installent :

| Console | Condition | Comment installer |
|---------|-----------|-------------------|
| **PS4** | Firmware jailbreaké (ex. 9.00 / 11.00 selon scène) | Package Installer / Debug Settings → Install Package Files |
| **PS5** | Console **exploitée** (HEN) + **PS4 FPKG Enabler** ou **kstuff** | Activer l’enabler, puis installer le `.pkg` comme un fPKG PS4 |

> Une **PS5 stock / officielle** ne peut **pas** lancer ces packages. Il n’existe pas de chemin légitime “PS5 retail” pour ce projet.

## Build pour chaque cible

```bash
# PS4 jailbreak
ps22psx create game.iso \
  --emulator bin/emulators/ps2emu.pkg \
  --icon cover.png --background back.png \
  --output out --target ps4

# PS5 HEN (même format, nom de fichier tagué)
ps22psx create game.iso \
  --emulator bin/emulators/ps2emu.pkg \
  --icon cover.png --background back.png \
  --output out --target ps5
```

`--target ps5` produit le même contenu Classics PS4, nommé `*_PS5HEN.pkg`, destiné à une PS5 avec FPKG Enabler.

## Checklist test PS4

1. Copier le `.pkg` sur USB exFAT.
2. Sur PS4 jailbreakée : Debug Settings → Package Installer.
3. Lancer le titre depuis la bibliothèque.
4. Si écran noir / bugs : ajouter un `.conf` / `.lua` (wiki compat) puis rebuild.

```bash
ps22psx config --title-id SLUS-XXXXX --name "Game" -o game.conf --add --gs-upscale=smooth
ps22psx lua --title-id SLUS-XXXXX -o SLUS-XXXXX_config.lua
ps22psx create game.iso ... --config game.conf --lua SLUS-XXXXX_config.lua --target ps4
```

## Checklist test PS5 (hack)

1. Boot exploit / HEN selon ton firmware supporté.
2. Charger **PS4 FPKG Enabler** (ou payload kstuff équivalent).
3. Installer le `.pkg` (via gestionnaire / FTP / USB selon ton setup).
4. Lancer le jeu. Sans l’enabler, le package PS4 ne démarrera pas correctement.

## Compatibilité jeux

Liste communautaire : [PS2 Classics Emulator Compatibility List](https://www.psdevwiki.com/ps4/PS2_Classics_Emulator_Compatibility_List)

Beaucoup de titres nécessitent des patches LUA/config — le maker CLI sert exactement à ça.

## Legal

Utilise uniquement des dumps de **jeux que tu possèdes**. Ce dépôt est un outil technique de packaging homebrew, pas un dépôt d’ISO.
