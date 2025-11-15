
---
title: Architecture overview
---
graph LR
    USR1((Customer))
    USR2((Deliverer))
    USR3((Admin))
    DB[("fa:fa-database App Database (PostgreSQL)" )]
    CLI(fa:fa-python CLI)
    API(fa:fa-python API / WebService)
    DAO(fa:fa-python DAO)
    SVC(fa:fa-python Service / Controllers )
    MDB[(fa:fa-database Google Maps DB)]
    MDBAPI(Google Maps API)

    USR1<--->CLI
    USR2<--->CLI
        subgraph Python app 
            CLI<-->SVC
            API<-->SVC
            SVC<-->DAO
        end
    USR3<--->API

    DAO<--->DB
    MDBAPI <--> MDB
    SVC <--> MDBAPI

