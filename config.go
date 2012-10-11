package main

import (
	"log"
	"os"
)

type Config struct {
	port        string
	static_root string
}

func NewConfig() *Config {
	config := &Config{}
	config.port = getenv("PORT", "5000")
	config.static_root = getenv("STATIC_ROOT", "./site")

	if _, err := os.Stat(config.static_root); err != nil {
		log.Fatalf("couldn't read STATIC_ROOT: ", config.static_root, err)
	}

	return config
}

func getenv(key, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}
