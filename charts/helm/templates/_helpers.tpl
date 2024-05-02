{{/*
Expand the name of the chart.
*/}}
{{- define "sfc-e2e-collector.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "sfc-e2e-collector.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "sfc-e2e-collector.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "sfc-e2e-collector.labels" -}}
helm.sh/chart: {{ include "sfc-e2e-collector.chart" . }}
{{ include "sfc-e2e-collector.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app: {{ include "sfc-e2e-collector.fullname" . }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "sfc-e2e-collector.selectorLabels" -}}
app.kubernetes.io/name: {{ include "sfc-e2e-collector.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Environments
*/}}
{{- define "sfc-e2e-collector.envs" -}}
{{- range $key, $val := .Values.envs }}
- name: {{ $key }}
  value: "{{ $val }}"
{{- end }}
{{- if not .Values.envs.ROOT_PATH }}
- name: ROOT_PATH
  value: "/{{ include "sfc-e2e-collector.fullname" . }}"
{{- end }}
{{- end }}
