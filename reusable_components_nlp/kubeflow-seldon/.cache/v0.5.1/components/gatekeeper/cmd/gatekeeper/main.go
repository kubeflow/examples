// Copyright 2019 The Kubeflow Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"flag"
	"github.com/kubeflow/kubeflow/components/gatekeeper/auth"
	"github.com/kubeflow/kubeflow/components/gatekeeper/cmd/gatekeeper/options"
	"github.com/onrik/logrus/filename"
	log "github.com/sirupsen/logrus"
)

func init() {
	// Add filename as one of the fields of the structured log message
	filenameHook := filename.NewHook()
	filenameHook.Field = "filename"
	log.AddHook(filenameHook)
}

func main() {
	sop := options.NewServerOption()
	sop.AddFlags(flag.CommandLine)

	flag.Parse()
	if sop.Username == "" || sop.Pwhash == "" {
		log.Fatal("Username or Pwhash empty, exit now")
	}
	s := auth.NewAuthServer(sop)
	s.Start(8085)
}
