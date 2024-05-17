package config

import (
	"encoding/json"
	"log/slog"
	"os"
)

type Config struct {
	Reactions Reactions `json:"reactions"`
}

type Reactions struct {
	InMessage []map[string]Reaction `json:"inMessage"`
	InStickerName []map[string]Reaction `json:"inStickerName"`
}

type Reaction struct {
	Emoji *string `json:"emoji"`
	Message *string `json:"message"`
}

func (c *Config) Load(l *slog.Logger) {
	dir, _ := os.Getwd()

	dat, err := os.ReadFile(dir + "/config/config.json")

	if err != nil {
		l.Error("Cannot load config file", slog.String("error", err.Error()))
		panic("Cannot load config file")
	}

	err = json.Unmarshal(dat, c)

	if err != nil {
		l.Error("Cannot load config file", slog.String("error", err.Error()))
		panic("Cannot load config file")
	}
}