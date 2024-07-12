# Rezultate Bac 2024

Programul face scrape la toate paginile din http://bacalaureat.edu.ro/Pages/TaraRezultMedie.aspx și generează JSON din datele preluate.

## [Descărcare date](https://github.com/tacheometry/rezultate-bac-2024/releases/download/bac_12_07_2024_0800/bac_2024_full.json)

Tipul datelor:

```ts
{
    "nr": number,
    "cod_candidat": string,
    "unitate_invatamant": string,
    "judet_cod": number,
    "judet_nume": string,
    "promotie_anterioara": boolean,
    "forma_invatamant": "Zi" | "Seral" | "Frecvență redusă",
    "specializare": string,
    "limba_romana_competente": "Utilizator experimentat" | "Utilizator avansat" | "Utilizator nivel mediu" | "Neprezentat" | "Eliminat" | null,
    "limba_romana_scris": number | "Neprezentat" | "Eliminat din examen",
    "limba_romana_contestatie": number | null,
    "limba_romana_nota_finala": number | "Neprezentat" | "Eliminat din examen",
    "limba_materna": "Limba germană" | "Limba maghiară (REAL)" | "Limba italiană" | "Limba maghiară (UMAN)" | "Limba slovacă" | "Limba ucraineană" | "Limba sârbă" | "Limba croată" | "Limba turcă" | null,
    "limba_materna_competente": "Utilizator experimentat" | "Utilizator avansat" | "Utilizator nivel mediu" | "Neprezentat" | "Eliminat" | null,
    "limba_materna_scris": number | "Neprezentat" | null,
    "limba_materna_contestatie": number | null,
    "limba_materna_nota_finala": number | "Neprezentat" | null,
    "limba_moderna": "Limba engleză" | "Limba franceză" | "Limba germană modernă" | "Limba spaniolă" | "Limba rusă" | "Limba italiană" | "Limba japoneză" | "Limba ebraică" | "Limba chineză" | "Limba portugheză",
    "limba_moderna_nota": string | "Eliminat" | null,
    "disciplina_obligatorie": "Istorie" | "Matematică MATE-INFO" | "Matematică ST-NAT" | "Matematică TEHN" | "Matematică PED",
    "disciplina_obligatorie_scris": number | "Neprezentat" | "Eliminat din examen",
    "disciplina_obligatorie_contestatie": number | null,
    "disciplina_obligatorie_nota_finala": number | "Neprezentat" | "Eliminat din examen",
    "disciplina_aleasa": string,
    "disciplina_aleasa_scris": number | "Neprezentat" | "Eliminat din examen",
    "disciplina_aleasa_contestatie": number | null,
    "disciplina_aleasa_nota_finala": number | "Neprezentat" | "Eliminat din examen",
    "competente_digitale": "Utilizator experimentat" | "Utilizator avansat" | "Utilizator nivel mediu" | "Utilizator incepator" | "Neprezentat" | "Eliminat",
    "media": number | null,
    "rezultat_final": "Reusit" | "Respins" | "Neprezentat" | "Eliminat din examen"
}
```

## Folosire

`python3 combine.py`
