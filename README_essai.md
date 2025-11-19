# ENSAI-2A-projet-info-template

Template for the ENSAI 2nd year IT project.

This very simple application includes a few elements that may help with the info 2A project:

- Layer programming (DAO, service, view, business_object)
- Connection to a database
- Terminal interface (view layer) with [inquirerPy](https://inquirerpy.readthedocs.io/en/latest/)
- Calling a Webservice
- Creating a webservice


## :arrow_forward: Software and tools

- [Visual Studio Code](https://code.visualstudio.com/)
- [Python 3.13](https://www.python.org/)
- [Git](https://git-scm.com/)
- A [PostgreSQL](https://www.postgresql.org/) database


## Clone the repository

- [ ] Open VSCode
- [ ] Open **Git Bash**
- [ ] Clone the repo
  - `git clone https://github.com/ludo2ne/ENSAI-2A-projet-info-template.git`


### Open Folder

- [ ] Open **Visual Studio Code**
- [ ] File > Open Folder
- [ ] Select folder *ENSAI-2A-projet-info-template*
  - *ENSAI-2A-projet-info-template* should be the root of your Explorer
  - :warning: if not the application will not launch. Retry open folder


## Repository Files Overview


| Item                       | Description                                                              |
| -------------------------- | ------------------------------------------------------------------------ |
| `README.md`                | Provides useful information to present, install, and use the application |
| `LICENSE`                  | Specifies the usage rights and licensing terms for the repository        |

### Configuration files

This repository contains a large number of configuration files for setting the parameters of the various tools used.

Normally, for the purposes of your project, you won't need to modify these files, except for `.env` and `requirements.txt`.


| Item                       | Description                                                              |
| -------------------------- | ------------------------------------------------------------------------ |
| `.github/workflows/ci.yml` | Automated workflow that runs predefined tasks (like testing, linting, or deploying) |
| `.vscode/settings.json`    | Contains VS Code settings specific to this project                       |
| `.coveragerc`              | Setup