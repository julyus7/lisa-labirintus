# Labirintus 3D – kiadási ellenőrzés

Kiadás: `dist/Labirintus3D.dc42`, 419284 bájt.
SHA256: `d95b32c3e84ca054dbaab8714d7386cb5b6e20d247b7528b332506974ad1d8d1`.

## Natív fordítás és floppy

Fordító: Lisa Pascal 3.26; kódgenerátor: MC68000 Code Generator 3.16.
Natív kódméret: 12924 bájt.
Linker: Lisa Linker 3.0. Fordítási hibák: 0;
linkerhibák: 0. A futtatható W.OBJ mérete
15872 bájt.

A lezárt fejlesztőlemezen az M.TEXT a helyi forrással byte-pontosan egyezik,
a Lisa TEXT fejlécének és DLE behúzásainak dekódolása után. A csomagolt
objektum a natívan linkelt W.OBJ változatlan eredménye. A linkerlistázatban
nulla hiba és futtatható programtípus szerepel.

Natív Sony 400 KB floppy, 800 eredeti szektorcímkével. Filer-név:
Labirintus; saját perspektivikus ikon; 249-es alkalmazásazonosító és D60A
lemezazonosító ellenőrizve. A DC42 hossza és mindkét ellenőrző összege helyes.

A futó natív program bitmapleíróját csak olvasva ellenőriztük: a puffer
12096 bájtos, 448×216 képpontos,
56 bájtos sorhosszal. A kezdőcím páros, szóhatárra igazított.
Az igazolás a kiadási DC42 fenti SHA256 értékéhez tartozik; a vendég
játékállapotába vagy képadataiba nem írtunk.

## Szabálymodell és natív futás

69359 külön Python-modell-ellenőrzés, valamint
345 natív ellenőrzési pont sikeres.
A natív szakaszok: input, levels, map, render, video.
A tényleges próbarendszer Linux LisaEm / LOS 3.1, 1 MB RAM,
5 MHz emulátoros célbeállítással. Ez célbeállítás, nem fizikai hardveres
sebességmérés.

A hosszú pályabejárás idejére az emulátor gyorsabb, normál kirajzolását
használtuk; minden mentett X11 képnél visszakapcsoltuk a teljes frissítést.
A bemeneti, térképi, perspektíva- és videópróbák teljes frissítéssel futottak.

A bevitel normál billentyű- és egérbemenet volt. A vendég játékállapotába
nem írtunk és kész nyerő állást nem töltöttünk be. Az ellenőrző eszköz
csak olvasta a játék állapotát, és összevetette a külön modellel.
Két külön normál X11 felvételt vizsgáltunk. Az álló helyzetű próba
80 tárolt képkockáján a teljes perspektívakép és térkép azonos
maradt, és a natív rajzolásszámláló sem változott. A Jobb nyíl tényleges
nyomva tartásával készült 80 képkockán a játék
3 fordulást végzett; a perspektívaképek között
3 különböző képet találtunk.
A térképből kizárólag a változó játékosnyilat körülvevő 32×32 natív képpontos
mezőt takartuk ki: azon kívül a térkép minden vizsgált képkockán azonos volt.
A billentyű felengedése után újra koherens, a szabálymodellel egyező
állapotot olvastunk.

A felvételi kérés 10 képkocka/másodperc volt;
ez nem a játék vagy a fizikai Lisa mért FPS-e. Ezek mintavételes
frissítésvizsgálatok, nem fizikai kijelzőmérések vagy teljes képkockára
atomi frissítés igazolásai.

## Együttélés és NAS

A program a meglévő játékok mellé csatolt floppyról indult.
A zárt privát rendszerlemezen mind a 20
korábbi eszközazonosító és 77 program-/erőforrásfájl
változatlan maradt. A privát merevlemezre másolást és az onnan indítást külön natív próba igazolta.

A Lisa szabályos kikapcsolása után visszaolvasott tesztfloppy programja és
ikonjai egyeznek a kiadással. A NAS-ra másolt fájl visszaolvasott SHA256 értéke
azonos. A 18 korábbi backup-fájl, köztük
a közös `.image` rendszerlemezek és az emulátorcsomag változatlan maradt.
Csak az új `Labirintus3D.dc42` került a NAS-ra.

## A próba határai

A cél valódi Apple Lisa 2 / LOS 3/3.1, natív alkalmazásként. Fizikai Lisa 2-n,
Windows LisaEmben és külön LOS 3.0 környezetben nem történt futási próba.
A fizikai floppyírást és egy konkrét hardveres floppyhelyettesítőt sem
ellenőriztünk. A DC42 alkalmazásfloppy, LOS nélkül nem indul.
A játszma nem mentődik vissza új programindításkor.


## 1.0.1 billentyűvezérlés-frissítés

A WASD bemeneti kezelőt Lisa Pascal 3.26 fordította, a M68000 Linker 3.0 nulla hibával linkelte. A DC42 ellenőrzése sikeres: 419284 bájt, tool 249, D60A lemezazonosító, 800 natív tag, mindhárom ikonerőforrás egyezik. A fizikai Lisa billentyűzetén a WASD eseményeket, valamint a friss bináris játék közbeni bemenetét nem sikerült külön ellenőriznem; ezt a csomag nem állítja igazoltnak.
