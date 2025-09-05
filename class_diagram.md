```mermaid

classDiagram
    class User {
        -name: String
        -surname: String
        -password : String
    }
    class Customer(User) {
        -adresse: String
        +passerCommande()
        +login(name, password)
    }
    class Driver(User){
        -mean_of_transport
        +login(name, password)
    }
    class Admin(User){
        +login(name, password)
    }
    class Order {
        -id: int
        -dateTime: DateTime
        -dishes: Dish[]
        +addDish()
        +calculateTotal()
    }
    class Dish {
        -name: String
        -price: float
        +getDescription()
    }
```

    Client "1" --> "*" Commande : passe
    Commande "1" --> "*" Plat : contient
```
