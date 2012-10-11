package main

import (
	//"fmt"
	"net/http"
	"encoding/json"
	"log"
	"time"
)

type Response struct {
	content interface{}
	status int
}

type Event struct {
	fb_event_id int32
	fb_user_id int32
	times []time.Time
}

type ApiHandler func(*http.Request) *Response

func Error(status int, message string) *Response {
	log.Println("api error: " + message)
	content := make(map[string]string)
	content["error"] = message
	return &Response{content, status}
}

func Success(content interface{}) *Response {
	return &Response{content, http.StatusOK}
}

func JsonHandler(a ApiHandler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		response := a(r)
		status := response.status

		content, err := json.Marshal(response.content)
		if err != nil {
			status = http.StatusInternalServerError
			content = []byte(`{"error":"error serializing json"}`)
		}

		w.WriteHeader(status)
		if _, err := w.Write(content); err != nil {
			log.Println(err)
		}
	}
}

func EventApi(req *http.Request) *Response {
	if req.Method != "POST" {
		return Error(
			http.StatusMethodNotAllowed,
			"unexpected method: " + req.Method)
	}

	return Success(&Event{})
}
