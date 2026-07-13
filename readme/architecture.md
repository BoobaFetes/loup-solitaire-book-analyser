# Architecture

this is the DATG or at less the minimum of the DATG (Data Architecture Technical Guide) for the project. It is a work in progress and will be updated as the project evolves.

*NOTES :*

- *je me demande si je ne devrais pas faire un HLM puis un LLM par environnement (local avec desktop-docker et stg/prod avec azure ou aws) pour bien représenter les inputs et outputs par environnement.*
- *par contre les LLM auront naturellement des inputs et outputs différents, mais je ne sais pas si c'est une bonne idée de faire un HLM par environnement. (GROS DOUTE surtout que le HLM est fait pour représenter les fonctionnalités normalement mais si on considère un HLM comme représentation technique alors dans ce cas cela represente aussi les inputs et output de chaque block donc ca complixifie inutilement les choses je pense)*

### Inputs (to be completed)

#### web app

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

#### batchs

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

#### persisted data

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

### Outputs (to be completed)

#### web app

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

#### batchs

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |

#### persisted data

| who send to web app | what is sent | how it is sent | where it is sent |
| --- | --- | --- | --- |
| user | url of the page to analyse | http request | web app |
