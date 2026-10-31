# Labirintus 3D – Apple Lisa 2 / Lisa Office System

Magyar nyelvű, natív Lisa Pascal / MC68000 labirintusjáték. Balra belső nézetű,
perspektivikus folyosórajz, mellette felülnézeti térkép segíti a tájékozódást.
A három saját, 15×15 mezős pályán kulcsokat kell összegyűjteni, majd eljutni
a kijárathoz. A feliratok a Lisa betűkészletéhez igazodva ékezet nélküliek.

**Elkészült, ellenőrzött kiadás.** A kiadási fájl
[Labirintus3D.dc42](https://github.com/julyus7/lisa-labirintus/releases/latest/download/Labirintus3D.dc42); a LOS-ban látható programnév **Labirintus**.
Ez alkalmazásfloppy, önállóan nem indít operációs rendszert.

## Valódi Lisa és emulátor

A cél **valódi Apple Lisa 2, Lisa Office System 3/3.1 rendszerrel**, natív
Lisa-alkalmazásként. A DC42 400 KB-os Sony floppy Lisa-szektorcímkéket is
tartalmaz. Fizikai géphez ezeket megőrző floppyíró vagy megfelelő
floppyhelyettesítő szükséges. A DC42-t teljes lemezképként kell kiírni.

LisaEmben indítsd el saját LOS rendszeredet, csatold a DC42-t floppyként,
nyisd meg a lemezt, majd a **Labirintus** ikont. Ha félretett ablakként jelenik
meg, dupla kattintással aktiváld újra. A játék nagy LOS-ablakban fut.

A ténylegesen elvégzett futási próbák és korlátaik a
`VALIDATION-HU.md` fájlban szerepelnek. A célplatform megnevezése nem jelent
fizikai hardveres tesztet. Windows LisaEmben és fizikai Lisa 2-n csak külön
igazolt próba esetén állítható tesztelt működés.

## Kezelés és cél

LisaEmben válaszd a **Key → Raw Keyboard** módot.

| Billentyű | Művelet |
| --- | --- |
| Bal | Fordulás 90 fokkal balra |
| Jobb | Fordulás 90 fokkal jobbra |
| Fel | Egy mező előre |
| Le | Egy mező hátra, az irány megtartásával |

Egy nyíl lenyomása azonnal végrehajt egy parancsot. Nyomva tartva ismétlődik;
a célzott ismétlési köz 180 ms. Lassabb emulációban ez hosszabb lehet.
Felengedéskor megszűnik az ismétlés. Egyszerre egy nyílbillentyű vezérel;
több nyíl együtt nem indít új parancsot. Ha már csak az egyik marad
lenyomva, az folytatja a mozgást vagy fordulást.

A négy képernyőgomb: **Ujra**, **Elozo palya**, **Kovetkezo palya**,
**Terkep: teljes / Terkep: felfedes**. Az utolsó a térképnézetet váltja.

A falon nem lehet átmenni. A kulcsokat rájuk lépve veszed fel. A kijáratra
akkor léphetsz be győzelemmel, ha már minden kulcsot összegyűjtöttél.
A térkép mutatja a helyedet és azt is, merre nézel; teljes és felfedezett
térképnézet közül választhatsz. Újrakezdéskor az aktuális pálya alaphelyzete
áll vissza. A játszma új programindításkor nem töltődik vissza.

## Saját ikon és azonosító

Alkalmazásazonosító: **249**. Lemezazonosító vége: **D60A**.
A saját, 48×32 pontos natív ikon perspektivikus folyosót, kis térképet és
emberfigurát ábrázol. A rendes, maszkos és kiválasztási ikonadatok a natív
814 bájtos Lisa ikonformátumba kerülnek.

Az új alkalmazás az előző játékok külön azonosítóit nem használja fel.
A közös `.image` rendszerlemezeket a fejlesztés és a kiadás nem írja át.


## Forrás és ellenőrzés

Forrás: [src/M.TEXT](src/M.TEXT), [src/game.pas](src/game.pas), [src/levels.json](src/levels.json).
Újrafordítás: [BUILD.md](BUILD.md). Tesztjegyzőkönyv: [VALIDATION.md](VALIDATION.md).
A kiadás 69 359 modell- és 345 natív ellenőrzést teljesített. A merevlemezre
másolás és az onnan indítás is igazolt. Fizikai Lisa 2, Windows LisaEm
és külön LOS 3.0 futási próba még nem történt.
