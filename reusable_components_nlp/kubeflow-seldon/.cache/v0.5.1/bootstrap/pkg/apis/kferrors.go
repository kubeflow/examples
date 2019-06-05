// Copyright 2018 The Kubeflow Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package apis

import (
	"fmt"
)

type StatusCode int

const (
	OK               StatusCode = 200
	INVALID_ARGUMENT StatusCode = 400
	INTERNAL_ERROR   StatusCode = 500
	UNKNOWN          StatusCode = 520
)

// KfError stands for Kubeflow error. This is the standard error interface
// for Kubeflow components.
type KfError struct {
	// Code is the HTTP response status code.
	Code    int    `json:"code"`
	Message string `json:"message,omitempty"`
}

func (e *KfError) Error() string {
	return fmt.Sprintf(" (kubeflow.error): Code %d with message: %v",
		e.Code, e.Message)
}
