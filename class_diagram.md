---
title: Ub'EJR Eats Class Diagram
---
```mermaid

---
title: Ub'EJR Eats Class Diagram
---
classDiagram
%% direction LR  
    class User {
        +id: int
        +firstName: string
        +lastName: string
        +username: string
        -password: string
        +email: string
    }
    
    class Customer {
        +address: string
        +postalCode: string
        +city: string 
    }
    
    class Driver {
        +transportation: string
    }

    class Administrator {
    }
    
    class Order {
        +id: int
        +date: Date
        +status: string
        +deliveryAddress: string
        +totalAmount: float
        +transportMethod : string
        +paymentMethod: string
        +calculateTotal() float
        +pay() bool
    }

    class Menu {
        -id: int
        +name: string
        +description: string
    }

    class Product {
        -id: int
        +name: string
        +sellingPrice: float
        -purchasePrice : float
        +type : string
        -stockQuantity: int
    }

    class OrderLine {
        +id:int
        +quantity: int
        +subTotal: float
    }


    %% Relations 
    User <|-- Customer : Heritage
    User <|-- Driver : Heritage
    User <|-- Administrator : Heritage
    
    Customer "1" -- "0..*" Order : place 

    Order "1" *-- "1..*" OrderLine : composition

    OrderLine "0..*" -- "1" Product : reference

    Driver "1" -- "0..*" Order : deliver 

    Administrator "1" -- "1" Menu : changes

    Menu "1" *-- "0..*" Product : composition
    
    %% Styles pour la lisibilité
    style User fill:#D6EAF8,stroke:#1A5276,stroke-width:2px
    style Customer fill:#E8F8F5,stroke:#27AE60,stroke-width:2px
    style Driver fill:#D6EAF8,stroke:#1A5276
    style Administrator fill:#FFB6B6,stroke:#E67E22
    
    style Order fill:#E0E0E0,stroke=#808080,stroke-width:2px
    style OrderLine fill:#E0E0E0,stroke=#808080

    style Menu fill:#E0E0E0,stroke=#808080,stroke-width:2px
    style Product fill:#E0E0E0,stroke=#808080
    style Cart fill:#E0E0E0,stroke=#808080

```