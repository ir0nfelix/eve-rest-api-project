db.createUser({
    user: "restaurant_user",
    pwd: "restaurant_passw0rd",
    roles: ["readWrite", "dbAdmin", "userAdmin"]
})
