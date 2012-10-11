package main

import (
	"fmt"
	"net/http"
	"log"
	//"os"
)


func main() {
	config := NewConfig()

	http.HandleFunc("/api/event/", JsonHandler(EventApi))
	http.Handle("/", http.FileServer(http.Dir(config.static_root)))

	fmt.Println("Listening on port", config.port)
	log.Fatal(http.ListenAndServe(":" + config.port, nil))
}
