# Automaattinen leikepöydän puhuminen -lisäosa

Tämä lisäosa puhuu automaattisesti leikepöydän sisällön sen muuttuessa. Tästä on hyötyä, jos pelaat peliä, joka tulostaa tekstiä leikepöydälle ja joka ei tue suoraa tulostusta NVDA:lle. Tämän lisäosan käyttämiseen ei tarvita ulkoisia ohjelmia.

[Muutosloki](https://github.com/mzanm/NVDAAutoclip/blob/main/changelog.md)
[Lataa viimeisin versio](https://github.com/mzanm/NVDAAutoclip/releases/latest/download/Autoclip.nvda-addon)

## Asennus

Yhteensopivuus: NVDA 2019.3 ja uudemmat

Asennus tapahtuu samalla tavalla kuin muidenkin lisäosien kohdalla.

1. Lataa viimeisin versio [releases-sivulta](https://github.com/mzanm/NVDAAutoclip/releases) tai yllä olevasta suorasta latauslinkistä.
2. Paina Enteriä lataamasi tiedoston kohdalla, jolloin lisäosan asennusvalintaikkuna avautuu.

## Käyttö

Kun lisäosa on asennettu ja otettu käyttöön joko pikanäppäimellä tai Työkalut-valikossa olevalla vaihtoehdolla, leikepöydän sisältö puhutaan automaattisesti sen muuttuessa. Huomaa, että oletuksena lisäosa on käytössä tilapäisesti seuraavaan NVDA:n uudelleenkäynnistykseen saakka. Lisäosa ei tallenna tilaansa NVDA:n asetuksiin, ellet muuta sitä lisäosan asetuspaneelista:

- **Pikanäppäin**: Ota käyttöön tai poista käytöstä automaattinen leikepöydän puhuminen painamalla `NVDA+Shift+Ctrl+K`. Pikanäppäintä on mahdollista muuttaa NVDA:n Näppäinkomennot-valintaikkunassa. Se löytyy Automaattinen leikepöydän puhuminen -kategoriasta.

- **Työkalut-valikko**: Ota käyttöön tai poista käytöstä automaattinen leikepöydän puhuminen avaamalla NVDA:n Työkalut-valikko ja valitsemalla "`Automaattinen leikepöydän puhuminen`" -vaihtoehto.

Lisäosa ei oletuksena keskeytä puhetta ennen leikepöydän sisällön puhumista. Mikäli haluat lisäosan keskeyttävän senhetkisen puheen aina ennen leikepöydän sisällön puhumista, voit muuttaa tätä asetusta lisäosan asetuspaneelista, joka löytyy NVDA:n asetusvalintaikkunasta. Tämä vaihtoehto on hyödyllinen, jos pelaat peliä, joka tulostaa tekstiä leikepöydälle NVDA:n ollessa lepotilassa, mikä estää näppäimistön näppäimiä keskeyttämästä NVDA:n puhetta.

## Asetukset

Lisäosan asetuspaneelissa on seuraavat asetukset:

- Käyttäjä voi määrittää, keskeyttääkö lisäosa senhetkisen puheen ennen leikepöydän sisällön puhumista.
- Käyttäjä voi määrittää, muistaako lisäosa tilansa, ts. onko se käytössä vai ei. Tämä vaihtoehto on otettava käyttöön, jotta lisäosa voidaan määrittää käynnistymään tietyssä ohjelmassa asetusprofiileja käyttäen.
