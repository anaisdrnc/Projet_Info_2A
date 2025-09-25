---
title: Ub'EJR Eats Class Diagram
---
```mermaid

---
title: Ub'EJR Eats Class Diagram
---
classDiagram

    class User {
        +id: int
        +firstName: string
        +lastName: string
        +username: string
        -password: string
        +email: string
        +logIn() bool
        +logOut() 
        +CreateAccount()
    }
    
    class Customer {
        +address: string
        +postalCode: string
        +city: string 
        +placeOrder(cart: Cart) Order
        +viewMenu() Menu
    }
    
    class Driver {
        +transportation: string
        +isAvailable : bool
        +viewItinerary()
        +takeDelivery(orderId: int) bool
        +cancelOrder(orderId:int)
        +markAsDelivered(orderId: int) bool
    }

    class Administrator {
        +addItemToMenu(item: Item)
        +deleteItemFromMenu(itemId: int)
        +updateMenuItem(itemId: int, newValues: object)
        +generateDailyReport() object
    }
    
    class Order {
        +id: int
        +date: Date
        +status: string
        +deliveryAddress: string
        +totalAmount: float
        +paymentMethod: string
        +calculateTotal() float
        +pay(): bool
    }

    class Menu {
        -id: int
        +name: string
        +description: string
    }

    class Item {
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

    class Cart {
        +addItem(item: Item, quantity: int)
        +removeItem(item:Item, quantity:int)
        +clearCart()
    }

    %% Relations 
    User <|-- Customer : Héritage
    User <|-- Driver : Héritage
    User <|-- Administrator : Héritage
    
    Customer "1" -- "0..*" Order : passe

    Order "1" *-- "1..*" OrderLine : composition

    OrderLine "0..*" -- "1" Item : référence

    Driver "1" -- "0..*" Order : livre

    Administrator "1" -- "1" Menu : gère

    Menu "1" *-- "0..*" Item : composition

    Customer "1" -- "1" Cart : possède

    Order <.. Cart : crée à partir de
    
    %% Styles pour la lisibilité
    style User fill:#D6EAF8,stroke:#1A5276,stroke-width:2px
    style Customer fill:#D6EAF8,stroke:#1A5276
    style DeliveryDriver fill:#D6EAF8,stroke:#1A5276
    style Administrator fill:#D6EAF8,stroke:#1A5276
    
    style Order fill:#FDEBD0,stroke:#E67E22,stroke-width:2px
    style OrderLine fill:#FDEBD0,stroke:#E67E22

    style Menu fill:#E8F8F5,stroke:#27AE60,stroke-width:2px
    style MenuItem fill:#E8F8F5,stroke:#27AE60
    style Cart fill:#F5EEF8,stroke:#8E44AD

```