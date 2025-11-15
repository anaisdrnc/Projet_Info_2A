``` mermaid
---
title: Architecture overview
---
graph LR
    USR1((Customer))
    USR2((Deliverer))
    USR3((Admin))
    DB[(" App Database (PostgreSQL)" )]
    CLI(CLI)
    API(API / WebService)
    DAO(DAO)
    SVC(Service / Controllers )
    MDB[(Google Maps DB)]
    MDBAPI(Google Maps API)

    USR1<--->CLI
    USR2<--->CLI
        subgraph Python app 
            CLI<-->SVC
            API<-->SVC
            SVC<-->DAO
        END
    USR3<--->API

    DAO<--->DB
    MDBAPI <--> MDB
    SVC <--> MDBAPI
```