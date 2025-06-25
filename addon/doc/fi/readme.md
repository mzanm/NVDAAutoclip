# Automaattinen leikepöydän puhuminen

Tämä lisäosa puhuu automaattisesti leikepöydän sisällön sen muuttuessa. Tästä on hyötyä, jos pelaat peliä, joka tulostaa tekstiä leikepöydälle ja joka ei tue suoraa tulostusta NVDA:lle. Tämän lisäosan käyttämiseen ei tarvita ulkoisia ohjelmia.

[Muutosloki](https://github.com/mzanm/NVDAAutoclip/blob/main/changelog.md)
[Lataa viimeisin versio](https://github.com/mzanm/NVDAAutoclip/releases/latest/download/Autoclip.nvda-addon)

## Asennus

Yhteensopivuus: NVDA 2021.1 ja uudemmat

**Huom:** Lisäosa on saatavilla NVDA:n lisäosakaupasta (NVDA-valikko > Työkalut > Lisäosakauppa > Saatavilla olevat lisäosat -välilehti). Seuraavassa on ohje manuaaliseen asennukseen.

1. Lataa viimeisin versio [releases-sivulta](https://github.com/mzanm/NVDAAutoclip/releases) tai yllä olevasta suorasta latauslinkistä.
2. Paina Enteriä lataamasi tiedoston kohdalla, jolloin lisäosan asennusvalintaikkuna avautuu.

## Käyttö

Kun lisäosa on asennettu ja otettu käyttöön, leikepöydän sisältö puhutaan automaattisesti sen muuttuessa. Huomaa, että oletuksena lisäosa on käytössä vain tilapäisesti seuraavaan NVDA:n uudelleenkäynnistykseen saakka. Jotta toiminto pysyy käytössä myös uudelleenkäynnistysten välillä ja jotta sitä voidaan käyttää asetusprofiileissa, ota kyseinen asetus käyttöön lisäosan asetuksista.

- **Pikanäppäin**: `NVDA+Vaihto+Ctrl+K`. Pikanäppäintä on mahdollista muuttaa NVDA:n Näppäinkomennot-valintaikkunan Automaattinen leikepöydän puhuminen -kategoriasta.
- **Työkalut-valikko**: NVDA-valikko > Työkalut > "Automaattinen leikepöydän puhuminen".

## Asetukset

Asetuksia voi muuttaa NVDA:n asetusvalintaikkunan "Automaattinen leikepöydän puhuminen" -kategoriasta.

- **Keskeytä ennen leikepöydän sisällön puhumista**: Keskeytetäänkö senhetkinen puhe ennen leikepöydän sisällön lukemista
- **Muista automaattisen leikepöydän puhumisen tila NVDA:n uudelleenkäynnistyksen jälkeen**: Säilytä käytössä- tai ei käytössä -tila myös uudelleenkäynnistysten välillä (tarvitaan asetusprofiileissa)
- **Näytä NVDA:n Työkalut-valikossa**: Näytä tai piilota Työkalut-valikossa

#### Lisäasetukset

- **Jaa teksti erillisiin osiin**: Osan suurin merkkimäärä, jotta puhesyntetisaattorit eivät ylikuormitu, kun leikepöydälle kopioidaan paljon tekstiä (oletus on 500, alle 100 poistaa tekstin jakamisen kokonaan käytöstä)
- **Pyri katkaisemaan osat sanan rajakohdissa**: Kun tekstin jakaminen on käytössä, teksti jaetaan välilyöntien kohdalta sanan katkeamisen estämiseksi (oletuksena käytössä)
- **Puhuttavan tekstin enimmäispituus**: Ohita leikepöydän päivitykset, jotka ylittävät tämän merkkimäärän (oletus on 15 000 merkkiä)
- **Saman tekstin estämisen viive**: Estää saman sisällön toistumisen tämän ajan sisällä (millisekunteina, oletus on 100, 0 poistaa käytöstä, -1 ei koskaan toistoa)
- **Puheen keskeytysten vähimmäisaikaväli**: vähimmäisaika keskeytysten välillä, kun keskeyttäminen on käytössä (millisekunteina, oletus on 50, 0 keskeyttää aina)
- **Palauta oletukset**: Palauta lisäasetusten oletukset
