package main

import (
	"path/filepath"
//	"fmt"
	"net/http"
	"log"
	"os"
)

func main() {
	static_root, err := filepath.Abs("site")
	if err != nil {
		log.Fatal(err)
	}

	http.Handle("/", http.FileServer(http.Dir(static_root)))
	log.Fatal(http.ListenAndServe(":" + os.Getenv("PORT"), nil))
}
