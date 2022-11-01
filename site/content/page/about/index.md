---
title: About
description: We value your privacy, trust us!
date: '2022-08-01'
aliases:
  - about-us
  - about-hugo
  - contact
license: GPL
menu:
    main: 
        weight: -90
        params:
            icon: user
#lastmod: '2020-10-09'
---

## Cosa facciamo

{{<quote autor="- StealBot team">}}
Mettendo a disposizione il tuo pc in brevissimo tempo potrai in brevissimo tempo condividerci tutti i tuoi dati sensibili! 😄
{{</quote>}}

## Obiettivo del progetto
L'obiettivo è la realizzazione di una BotNET[^1] per il recupero di quante più informazioni possibili sulla dispositivo in cui una delle componenti della BotNET venga eseguito.
### Strumenti e linguaggi adoperati
Si richiede un applicativo scritto in **Python**[^2] che utilizzi come strumento di comunicazione le **socket**[^3]
## Implementazione del sistema
Il progetto si concretizza in 2 componenti ben definite:
+ Un *Bot Master* per la gestione dei dati ricevuti dal *bot slave* al quale inpartisce comandi sfruttando una connessione tramite socket asincrona;
+ Il *Bot slave*, che ha il compito di ricavare quante più informazioni possibili sullo stato della macchina sul quale viene eseguito.

[^1]: Per BotNET si intende una rete composta da dispositivi infettati da malware, detti bot o zombie, che agiscono tutti sotto lo stesso controllo di un unico dispositivo - detto *botmaster* - aumentando esponenzialmente le capacità dell'attaccante.
[^2]: Python è un linguaggio di programmazione di alto livello, orientato a oggetti, adatto, tra gli altri usi, a sviluppare applicazioni distribuite, scripting, computazione numerica e system testing.
[^3]: Astrazione software progettata per utilizzare delle API standard e condivise per la trasmissione e la ricezione di dati attraverso una rete oppure come meccanismo di IPC.
